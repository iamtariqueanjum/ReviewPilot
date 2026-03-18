from __future__ import annotations

import hmac
import hashlib

from app.core.logger import logger
from app.utils.constants import ConfigConstants


def verify_github_webhook(payload_body: bytes, signature: str) -> bool:
    secret = ConfigConstants.GITHUB_WEBHOOK_SECRET
    if not secret:
        logger.warning("GITHUB_WEBHOOK_SECRET not set in environment variables")
        return False
    try:
        expected_signature = "sha256=" + hmac.new(
            secret.encode(),
            payload_body or b"",
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        logger.exception("Error while verifying GitHub webhook signature")
        return False
