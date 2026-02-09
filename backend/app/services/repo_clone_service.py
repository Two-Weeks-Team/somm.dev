import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.processors.codebase_analyzer import CodebaseAnalyzer, CodeMetrics

logger = logging.getLogger(__name__)

MAX_REPO_SIZE_MB = 200
MAX_FILE_SIZE_BYTES = 512 * 1024  # 512KB per file
MAX_FILES_TO_READ = 500
MAX_TOTAL_CONTENT_BYTES = 10 * 1024 * 1024  # 10MB total content
CLONE_TIMEOUT_SECONDS = 120

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    ".nuxt",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "vendor",
    "target",
    ".gradle",
    ".idea",
    ".vscode",
    "coverage",
    ".turbo",
    ".cache",
    ".output",
    "out",
    ".vercel",
    ".serverless",
}

SKIP_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".bmp",
    ".mp3",
    ".mp4",
    ".wav",
    ".avi",
    ".mov",
    ".mkv",
    ".flv",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".rar",
    ".7z",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".pyc",
    ".pyo",
    ".class",
    ".o",
    ".a",
    ".so",
    ".dll",
    ".exe",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".pkl",
    ".pickle",
    ".min.js",
    ".min.css",
    ".map",
    ".lock",
    ".sum",
}

ANALYZABLE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rb",
    ".kt",
    ".kts",
    ".swift",
    ".dart",
}

SOURCE_EXTENSIONS = ANALYZABLE_EXTENSIONS | {
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".rs",
    ".php",
    ".lua",
    ".r",
    ".scala",
    ".ex",
    ".exs",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".md",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".sql",
    ".graphql",
    ".proto",
    ".dockerfile",
    ".tf",
    ".hcl",
    ".env.example",
    ".gitignore",
    ".dockerignore",
    "Makefile",
    "Dockerfile",
    "Procfile",
}


@dataclass
class CloneResult:
    main_files: list[dict[str, str]] = field(default_factory=list)
    code_metrics: Optional[dict[str, Any]] = None
    summary: dict[str, Any] = field(default_factory=dict)
    skipped_reason: Optional[str] = None
    errors: list[str] = field(default_factory=list)


def _is_binary(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except Exception:
        return True


def _should_skip_dir(dir_name: str) -> bool:
    return dir_name in SKIP_DIRS or dir_name.startswith(".")


def _should_skip_file(file_path: Path) -> bool:
    name = file_path.name.lower()
    suffix = file_path.suffix.lower()

    if suffix in SKIP_EXTENSIONS:
        return True
    if name.endswith(".min.js") or name.endswith(".min.css"):
        return True
    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return True
    return False


def _is_source_file(file_path: Path) -> bool:
    suffix = file_path.suffix.lower()
    name = file_path.name

    if suffix in SOURCE_EXTENSIONS:
        return True
    if name in {"Makefile", "Dockerfile", "Procfile", "Gemfile", "Rakefile"}:
        return True
    if name.startswith(".") and name.endswith("rc"):
        return True
    return False


def _collect_files(repo_dir: Path) -> tuple[list[Path], dict[str, int]]:
    files = []
    stats = {"total_scanned": 0, "skipped_dir": 0, "skipped_file": 0, "collected": 0}

    for root, dirs, filenames in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not _should_skip_dir(d)]
        stats["skipped_dir"] += len(
            [
                d
                for d in os.listdir(root)
                if os.path.isdir(os.path.join(root, d)) and _should_skip_dir(d)
            ]
        )

        for name in filenames:
            stats["total_scanned"] += 1
            file_path = Path(root) / name

            if _should_skip_file(file_path):
                stats["skipped_file"] += 1
                continue

            if not _is_source_file(file_path):
                stats["skipped_file"] += 1
                continue

            if _is_binary(file_path):
                stats["skipped_file"] += 1
                continue

            files.append(file_path)
            stats["collected"] += 1

            if stats["collected"] >= MAX_FILES_TO_READ:
                break

        if stats["collected"] >= MAX_FILES_TO_READ:
            break

    return files, stats


def _read_files(files: list[Path], repo_dir: Path) -> list[dict[str, str]]:
    main_files = []
    total_bytes = 0

    for file_path in sorted(files):
        if total_bytes >= MAX_TOTAL_CONTENT_BYTES:
            break

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            rel_path = str(file_path.relative_to(repo_dir))
            total_bytes += len(content.encode("utf-8"))

            main_files.append(
                {
                    "path": rel_path,
                    "content": content,
                    "size": len(content),
                    "language": file_path.suffix.lstrip(".") or file_path.name,
                }
            )
        except Exception as e:
            logger.debug(f"Failed to read {file_path}: {e}")

    return main_files


def _run_code_analysis(main_files: list[dict[str, str]]) -> Optional[CodeMetrics]:
    analyzer = CodebaseAnalyzer()

    analyzable = [
        f for f in main_files if Path(f["path"]).suffix.lower() in ANALYZABLE_EXTENSIONS
    ]

    if not analyzable:
        return None

    return analyzer.analyze_files(analyzable)


async def clone_and_analyze(
    repo_url: str,
    branch: Optional[str] = None,
    github_token: Optional[str] = None,
) -> CloneResult:
    result = CloneResult()

    clone_url = repo_url
    if github_token and "github.com" in repo_url:
        clone_url = repo_url.replace(
            "https://github.com", f"https://x-access-token:{github_token}@github.com"
        )
    if not clone_url.endswith(".git"):
        clone_url += ".git"

    with tempfile.TemporaryDirectory(prefix="somm_clone_") as tmp_dir:
        try:
            clone_cmd = [
                "git",
                "clone",
                "--depth",
                "1",
                "--single-branch",
                "--no-tags",
            ]
            if branch:
                clone_cmd.extend(["--branch", branch])

            clone_cmd.extend([clone_url, tmp_dir])

            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            env["GIT_LFS_SKIP_SMUDGE"] = "1"

            proc = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=CLONE_TIMEOUT_SECONDS,
                env=env,
            )

            if proc.returncode != 0:
                error_msg = proc.stderr.strip()[:200]
                result.skipped_reason = f"git clone failed: {error_msg}"
                result.errors.append(result.skipped_reason)
                return result

            repo_dir = Path(tmp_dir)

            files, scan_stats = _collect_files(repo_dir)
            result.main_files = _read_files(files, repo_dir)

            code_metrics = _run_code_analysis(result.main_files)
            if code_metrics:
                result.code_metrics = code_metrics.to_dict()

            result.summary = {
                "files_analyzed": len(result.main_files),
                "scan_stats": scan_stats,
                "total_content_bytes": sum(f["size"] for f in result.main_files),
                "languages_found": list(set(f["language"] for f in result.main_files)),
            }
            if code_metrics:
                result.summary["code_quality"] = {
                    "total_functions": code_metrics.total_functions,
                    "total_classes": code_metrics.total_classes,
                    "avg_complexity": round(code_metrics.avg_cyclomatic_complexity, 2),
                    "max_complexity": code_metrics.max_cyclomatic_complexity,
                    "maintainability_index": round(
                        code_metrics.maintainability_index, 2
                    ),
                    "large_functions_count": len(code_metrics.large_functions),
                    "high_complexity_count": len(
                        code_metrics.high_complexity_functions
                    ),
                }

        except subprocess.TimeoutExpired:
            result.skipped_reason = f"git clone timed out ({CLONE_TIMEOUT_SECONDS}s)"
            result.errors.append(result.skipped_reason)
        except Exception as e:
            result.skipped_reason = f"clone_and_analyze failed: {e!s}"
            result.errors.append(result.skipped_reason)
            logger.exception("clone_and_analyze error")

    return result
