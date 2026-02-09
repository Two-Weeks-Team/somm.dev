"""LLM Context utilities for token-efficient prompt construction.

This module provides utilities for:
- Rendering repository context into compact strings
- Estimating token counts heuristically
- Truncating context to fit within token budgets
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_MAX_CONTEXT_TOKENS = 8000
CHARS_PER_TOKEN_HEURISTIC = 4
MAX_README_CHARS = 4000
MAX_FILE_TREE_ITEMS = 200
MAX_FILE_TREE_DEPTH = 4


def estimate_tokens(text: str) -> int:
    """Estimate token count using character heuristic.

    Uses ~4 chars per token as a conservative estimate.
    This works reasonably well for English text and code.
    """
    if not text:
        return 0
    return len(text) // CHARS_PER_TOKEN_HEURISTIC + 1


def _summarize_file_tree(file_tree: list[dict[str, Any]]) -> str:
    """Summarize file tree into a compact representation."""
    if not file_tree:
        return "No files found."

    dirs: set[str] = set()
    files_by_ext: dict[str, int] = {}
    important_files: list[str] = []
    total_files = 0
    total_dirs = 0

    important_patterns = [
        "readme",
        "license",
        "contributing",
        "changelog",
        "package.json",
        "pyproject.toml",
        "cargo.toml",
        "go.mod",
        "requirements.txt",
        "setup.py",
        "dockerfile",
        "docker-compose",
        ".github/workflows",
        "makefile",
        "justfile",
        "tsconfig.json",
        "jest.config",
        "vitest.config",
        "pytest.ini",
        "conftest.py",
    ]

    for item in file_tree:
        path = item.get("path", "")
        item_type = item.get("type", "blob")

        if item_type == "tree":
            total_dirs += 1
            parts = path.split("/")
            if len(parts) <= 2:
                dirs.add(path)
        else:
            total_files += 1
            ext = path.rsplit(".", 1)[-1].lower() if "." in path else "other"
            files_by_ext[ext] = files_by_ext.get(ext, 0) + 1

            path_lower = path.lower()
            for pattern in important_patterns:
                if pattern in path_lower and len(important_files) < 20:
                    important_files.append(path)
                    break

    lines = [
        f"Repository Structure: {total_files} files, {total_dirs} directories",
        "",
        "Top-level directories:",
    ]

    sorted_dirs = sorted(dirs)[:15]
    for d in sorted_dirs:
        lines.append(f"  - {d}/")

    if len(dirs) > 15:
        lines.append(f"  ... and {len(dirs) - 15} more directories")

    lines.extend(["", "File types:"])
    sorted_exts = sorted(files_by_ext.items(), key=lambda x: -x[1])[:10]
    for ext, count in sorted_exts:
        lines.append(f"  - .{ext}: {count} files")

    if important_files:
        lines.extend(["", "Key files detected:"])
        for f in important_files[:10]:
            lines.append(f"  - {f}")

    return "\n".join(lines)


def _summarize_languages(languages: dict[str, dict[str, Any]]) -> str:
    """Summarize language breakdown."""
    if not languages:
        return "No language data available."

    sorted_langs = sorted(
        languages.items(), key=lambda x: x[1].get("percentage", 0), reverse=True
    )

    lines = ["Language breakdown:"]
    for lang, stats in sorted_langs[:8]:
        pct = stats.get("percentage", 0)
        lines.append(f"  - {lang}: {pct:.1f}%")

    if len(sorted_langs) > 8:
        lines.append(f"  ... and {len(sorted_langs) - 8} more languages")

    return "\n".join(lines)


def _truncate_readme(readme: str | None, max_chars: int = MAX_README_CHARS) -> str:
    """Truncate README to fit within character budget."""
    if not readme:
        return "No README found."

    if len(readme) <= max_chars:
        return readme

    truncated = readme[:max_chars]
    last_newline = truncated.rfind("\n", max_chars - 500)
    if last_newline > max_chars // 2:
        truncated = truncated[:last_newline]

    return truncated + "\n\n[README truncated for brevity]"


def render_repo_context(
    repo_context: dict[str, Any],
    max_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS,
) -> tuple[str, dict[str, Any]]:
    """Render repository context into a compact string for LLM prompts.

    Args:
        repo_context: Raw repository context from GitHubService.
        max_tokens: Maximum token budget for the rendered context.

    Returns:
        Tuple of (rendered_context_string, metadata_dict).
        metadata_dict contains truncation info for observability.
    """
    metadata = repo_context.get("metadata", {})
    languages = repo_context.get("languages", {})
    file_tree = repo_context.get("file_tree", [])
    readme = repo_context.get("readme")
    techniques = repo_context.get("techniques", [])

    meta_section = f"""Repository: {metadata.get("full_name", "Unknown")}
Description: {metadata.get("description") or "No description"}
Primary Language: {metadata.get("language") or "Not specified"}
Stars: {metadata.get("stars", 0)} | Forks: {metadata.get("forks", 0)}
Default Branch: {metadata.get("default_branch", "main")}"""

    lang_section = _summarize_languages(languages)
    tree_section = _summarize_file_tree(file_tree)

    max_readme_chars = MAX_README_CHARS
    remaining_budget = max_tokens * CHARS_PER_TOKEN_HEURISTIC
    current_size = len(meta_section) + len(lang_section) + len(tree_section) + 500

    if remaining_budget - current_size < MAX_README_CHARS:
        max_readme_chars = max(500, remaining_budget - current_size - 200)

    readme_section = _truncate_readme(readme, max_readme_chars)

    sections = [
        "=== REPOSITORY CONTEXT ===",
        "",
        meta_section,
        "",
        lang_section,
        "",
        tree_section,
        "",
        "=== README ===",
        readme_section,
    ]

    if techniques:
        technique_names = [t.get("name", t.get("id", "")) for t in techniques[:15]]
        if technique_names:
            sections.extend(
                [
                    "",
                    "=== AVAILABLE EVALUATION TECHNIQUES ===",
                    ", ".join(technique_names),
                ]
            )
            if len(techniques) > 15:
                sections.append(f"... and {len(techniques) - 15} more techniques")

    rendered = "\n".join(sections)

    estimated_tokens = estimate_tokens(rendered)
    truncated = estimated_tokens > max_tokens

    if truncated:
        chars_to_keep = max_tokens * CHARS_PER_TOKEN_HEURISTIC
        rendered = rendered[:chars_to_keep]
        last_section = rendered.rfind("\n===")
        if last_section > chars_to_keep // 2:
            rendered = rendered[:last_section]
        rendered += "\n\n[Context truncated to fit token budget]"
        estimated_tokens = estimate_tokens(rendered)

    render_metadata = {
        "estimated_tokens": estimated_tokens,
        "truncated": truncated,
        "original_file_count": len(file_tree),
        "original_readme_length": len(readme) if readme else 0,
        "rendered_length": len(rendered),
    }

    logger.info(
        f"Rendered repo context: {render_metadata['estimated_tokens']} tokens, "
        f"truncated={truncated}, files={len(file_tree)}"
    )

    return rendered, render_metadata


def get_context_budget(provider: str, model: str | None = None) -> int:
    """Get recommended context token budget for a provider/model.

    Returns a conservative budget leaving room for system prompts and output.
    """
    model_budgets = {
        "gemini-3-pro-preview": 32000,
        "gemini-3-flash-preview": 32000,
        "gemini-2.5-pro": 32000,
        "gemini-2.5-flash": 32000,
        "gemini-2.0-flash": 32000,
        "gemini-1.5-pro": 32000,
        "gemini-1.5-flash": 32000,
        "gpt-4o": 32000,
        "gpt-4o-mini": 32000,
        "gpt-4-turbo": 32000,
        "o1": 64000,
        "o3-mini": 64000,
        "claude-opus-4-5-20251101": 64000,
        "claude-opus-4-20250514": 64000,
        "claude-sonnet-4-5-20250929": 64000,
        "claude-sonnet-4-20250514": 64000,
        "claude-3-opus-20240229": 32000,
        "claude-3-5-sonnet-20241022": 32000,
    }

    if model and model in model_budgets:
        return model_budgets[model]

    provider_defaults = {
        "gemini": 32000,
        "vertex": 32000,
        "openai": 32000,
        "anthropic": 64000,
    }

    return provider_defaults.get(provider, DEFAULT_MAX_CONTEXT_TOKENS)
