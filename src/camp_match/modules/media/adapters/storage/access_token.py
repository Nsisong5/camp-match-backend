from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from camp_match.modules.media.application.ports.outbound import AccessGrant


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def issue_token(key: str, secret: str, ttl_seconds: int = 300) -> AccessGrant:
    expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
    expires_at_unix = str(int(expires_at.timestamp()))

    key_b64 = _base64url_encode(key.encode("utf-8"))
    time_b64 = _base64url_encode(expires_at_unix.encode("utf-8"))

    message = f"{key}:{expires_at_unix}"
    signature = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    token = f"{key_b64}.{time_b64}.{signature}"
    return AccessGrant(token=token, expires_at=expires_at)


def verify_token(token: str, secret: str) -> str | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        key_b64, time_b64, signature = parts

        key = _base64url_decode(key_b64).decode("utf-8")
        expires_at_unix_bytes = _base64url_decode(time_b64)
        expires_at_unix = expires_at_unix_bytes.decode("utf-8")

        expires_at = datetime.fromtimestamp(int(expires_at_unix), UTC)
        if datetime.now(UTC) >= expires_at:
            return None

        message = f"{key}:{expires_at_unix}"
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return None

        return key
    except Exception:
        return None
