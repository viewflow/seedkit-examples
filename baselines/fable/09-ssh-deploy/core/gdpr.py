"""GDPR helpers: PII scrubbing for error reports and user data export/delete."""

from typing import Any

from django.utils import timezone

# Keys whose values must never reach the error tracker.
SENSITIVE_KEYS = frozenset(
    {
        "password",
        "passwd",
        "secret",
        "token",
        "authorization",
        "cookie",
        "csrfmiddlewaretoken",
        "api_key",
        "apikey",
        "session",
        "sessionid",
        "email",
        "phone",
        "ssn",
        "credit_card",
    }
)

SCRUBBED = "[Scrubbed]"


def _scrub(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: SCRUBBED if key.lower() in SENSITIVE_KEYS else _scrub(val)
            for key, val in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_scrub(item) for item in value]
    return value


def scrub_sentry_event(event: dict, hint: dict) -> dict:
    """sentry-sdk before_send hook: strip PII before events leave the host."""
    request = event.get("request")
    if request:
        request.pop("cookies", None)
        request["headers"] = _scrub(request.get("headers", {}))
        request["data"] = _scrub(request.get("data", {}))
        request["env"] = _scrub(request.get("env", {}))

    user = event.get("user")
    if user:
        # Keep only the opaque id; drop email, username, IP.
        event["user"] = {"id": user.get("id")}

    if "extra" in event:
        event["extra"] = _scrub(event["extra"])
    if "contexts" in event:
        event["contexts"] = _scrub(event["contexts"])

    return event


def export_user_data(user) -> dict:
    """Collect the personal data held for a user (GDPR art. 15/20)."""
    return {
        "exported_at": timezone.now().isoformat(),
        "user": {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
        },
        "groups": list(user.groups.values_list("name", flat=True)),
    }


def delete_user_data(user) -> None:
    """Erase a user's personal data (GDPR art. 17) by anonymising the account."""
    user.username = f"deleted-user-{user.pk}"
    user.email = ""
    user.first_name = ""
    user.last_name = ""
    user.set_unusable_password()
    user.is_active = False
    user.save(
        update_fields=["username", "email", "first_name", "last_name", "password", "is_active"]
    )
