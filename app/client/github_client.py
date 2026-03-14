from __future__ import annotations

import logging
from typing import Optional

from app.client.http_client import APIClient
from app.utils.constants import BaseUrl, RouteValues, HTTPMethod

logger = logging.getLogger(__name__)


class GitHubClient(object):

    def __init__(self, jwt_token, timeout=10):
        self.base_url = BaseUrl.GITHUB_API.value
        self.timeout = timeout
        self.jwt_token = jwt_token

        headers = {
            "Accept": "application/vnd.github+json",
            # "User-Agent": "ReviewPilot/1.0",
        }
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        self.client = APIClient(base_url=self.base_url, retries=3, headers=headers)


    def get_installation_access_token(self, installation_id: int) -> str:
        try:
            path = RouteValues.INSTALLATION_ACCESS_TOKEN.value.format(installation_id=installation_id)
            result = self.client.call_api(HTTPMethod.POST, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300 and isinstance(body, dict):
                token = body.get("token")
                if token:
                    return token
                raise ValueError("GitHub response did not contain an access token")

            logger.error("Failed to fetch installation token: status=%s body=%s", status, body)
            raise ValueError(f"Failed to fetch installation token: status={status}")
        except Exception:
            logger.exception("Error while requesting installation access token for %s", installation_id)
            raise
