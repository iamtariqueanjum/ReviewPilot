from __future__ import annotations

import os
import time
import jwt
import requests
import logging

from dotenv import load_dotenv
load_dotenv()

from app.client.github_client import GitHubClient

logger = logging.getLogger(__name__)


def generate_jwt() -> str:
    GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
    GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

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


def get_installation_token(installation_id: int) -> str:
    jwt_token = generate_jwt()

    client = GitHubClient(jwt_token=jwt_token)
    try:
        installation_token = client.get_installation_access_token(installation_id)
        logger.info("Fetched installation token for installation_id=%s", installation_id)
        print(f"Installation token for installation_id={installation_id}: {installation_token}")
        return installation_token
    except Exception:
        logger.exception("Failed to fetch installation token for %s", installation_id)
        raise
