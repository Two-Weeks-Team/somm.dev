from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class ProviderDecision:
    provider: str
    reason: str


def _parse_csv(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def _is_admin(user_doc: dict | None) -> bool:
    if not user_doc:
        return False

    role = str(user_doc.get("role", "")).lower()
    if role in {"admin", "superadmin"}:
        return True

    user_id = str(user_doc.get("_id", "")).lower()
    email = str(user_doc.get("email", "")).lower()
    admin_ids = _parse_csv(settings.VERTEX_ADMIN_USER_IDS)
    admin_emails = _parse_csv(settings.VERTEX_ADMIN_EMAILS)
    return (user_id in admin_ids) or (email in admin_emails)


def _is_premium(user_doc: dict | None) -> bool:
    if not user_doc:
        return False

    plan = str(user_doc.get("plan", "")).lower()
    if plan in {"premium", "pro", "enterprise"}:
        return True

    user_id = str(user_doc.get("_id", "")).lower()
    email = str(user_doc.get("email", "")).lower()
    premium_ids = _parse_csv(settings.VERTEX_PREMIUM_USER_IDS)
    premium_emails = _parse_csv(settings.VERTEX_PREMIUM_EMAILS)
    return (user_id in premium_ids) or (email in premium_emails)


def decide_provider(
    user_doc: dict | None,
    requested_provider: str | None,
    api_key: str | None,
) -> ProviderDecision:
    if api_key:
        return ProviderDecision(provider="gemini", reason="byok")

    if _is_admin(user_doc):
        return ProviderDecision(provider="vertex", reason="admin")

    if _is_premium(user_doc):
        return ProviderDecision(provider="vertex", reason="premium")

    return ProviderDecision(provider=requested_provider or "gemini", reason="default")
