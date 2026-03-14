import os
import time
import jwt
import requests


def generate_jwt() -> str:
    GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
    GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

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

    # url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"