from __future__ import annotations

import os
import hmac
import hashlib
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def verify_github_webhook(payload_body: bytes, signature: str) -> bool:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
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
