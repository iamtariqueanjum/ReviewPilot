from __future__ import annotations

import time
import jwt

from app.core.logger import logger
from app.utils.constants import ConfigConstants


def generate_jwt() -> str:
    GITHUB_APP_ID = ConfigConstants.GITHUB_APP_ID
    GITHUB_PRIVATE_KEY_PATH = ConfigConstants.GITHUB_PRIVATE_KEY_PATH

    if not GITHUB_APP_ID or not GITHUB_PRIVATE_KEY_PATH:
        raise EnvironmentError("GITHUB_APP_ID and GITHUB_PRIVATE_KEY_PATH must be set in environment")

    with open(GITHUB_PRIVATE_KEY_PATH, "r") as f:
        signing_key = f.read()

    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + (10 * 60),  # JWT valid for 10 minutes
        "iss": GITHUB_APP_ID
    }
    encoded_jwt_token = jwt.encode(payload, signing_key, algorithm="RS256")
    return encoded_jwt_token
