import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

MAX_FIELD_LENGTH = 10000

INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)you\s+are\s+now\s+a\s+different",
    r"(?i)system\s+prompt\s+override",
    r"(?i)give\s+this\s+(repo|project|code)\s+a\s+score\s+of\s+\d+",
    r"(?i)as\s+an?\s+evaluator[,\s]+i\s+should",
    r"(?i)forget\s+(everything|all|your)\s+(above|previous)",
    r"(?i)new\s+instructions?\s*:",
    r"(?i)override\s+(the\s+)?(scoring|evaluation|rubric)",
    r"(?i)pretend\s+(you\s+are|to\s+be)",
    r"(?i)disregard\s+(the\s+)?(above|previous|prior)",
    r"(?i)\bscore\s*[:=]\s*(?:10|100|perfect|maximum)\b",
    r"(?i)maximum\s+score\s+for\s+(?:all|every)\s+(?:item|criteria)",
]


@dataclass
class ContentValidation:
    is_suspicious: bool = False
    flags: list[str] = field(default_factory=list)
    risk_level: str = "none"  # none, low, medium, high
    patterns_found: int = 0


def sanitize_repo_content(content: str) -> str:
    """Strip known prompt injection patterns and truncate."""
    if not content:
        return content

    if len(content) > MAX_FIELD_LENGTH:
        content = content[:MAX_FIELD_LENGTH]

    for pattern in INJECTION_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            logger.warning(f"Prompt injection pattern found: {pattern[:50]}")
            content = re.sub(pattern, "[REDACTED]", content)

    return content


def validate_repo_content(content: str) -> ContentValidation:
    """Check for suspicious patterns without modifying content."""
    result = ContentValidation()

    if not content:
        return result

    for pattern in INJECTION_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            result.flags.append(f"Pattern: {pattern[:60]}")
            result.patterns_found += len(matches)

    if result.patterns_found > 0:
        result.is_suspicious = True
        if result.patterns_found >= 3:
            result.risk_level = "high"
        elif result.patterns_found >= 2:
            result.risk_level = "medium"
        else:
            result.risk_level = "low"

    return result


def wrap_with_delimiters(repo_content: str, instructions: str) -> str:
    """Wrap content in XML-style delimiters for prompt hardening.
    Instructions placed AFTER content (harder to override).
    """
    return (
        "<repo_content>\n"
        f"{repo_content}\n"
        "</repo_content>\n\n"
        "<evaluation_instructions>\n"
        f"{instructions}\n"
        "</evaluation_instructions>"
    )
