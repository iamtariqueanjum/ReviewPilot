from __future__ import annotations

import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.utils.constants import BaseUrls, Routes, HTTPMethod
from app.utils.jwt_generator import generate_jwt


logger = logging.getLogger(__name__)


class GitHubClient(object):

    def __init__(self, installation_id, retries=3, timeout=10):
        self.installation_id = installation_id
        self.base_url = BaseUrls.GITHUB_API.value
        self.session = requests.Session()
        self.retry_strategy = Retry(
            total=retries,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504], # TODO add other statuses if needed
            allowed_methods=["GET", "POST"], # TODO add other methods if needed
        )
        self.timeout = timeout
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.get_installation_access_token()}"
        }

    def request(self, method, path, params=None, json=None, data=None, timeout=10, headers=None):
        url = f"{self.base_url}{path}"
        resp = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            data=data,
            headers=headers or self.headers,
            timeout=timeout
        )
        resp.raise_for_status()
        return resp

    def call_api(self, method, path, **kwargs):
        response = {"status_code": None, "body": None}
        try:
            resp = self.request(method=method, path=path, **kwargs)
            response = {"status_code": resp.status_code}
            try:
                response["body"] = resp.json()
            except ValueError:
                response["body"] = resp.text
        except Exception as err:
            logger.exception(f"Error while calling API : {str(err)}: {method} {path}")
        print(f"API call: {method} {path} response: {response}")
        return response

    # TODO set installation token in the cache for expiration and regenerate if expired
    def get_installation_access_token(self) -> str:
        try:
            path = Routes.INSTALLATION_ACCESS_TOKEN.value.format(installation_id=self.installation_id)
            headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {generate_jwt()}"}
            result = self.call_api(HTTPMethod.POST, path, headers=headers)
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
            logger.exception("Error while requesting installation access token for %s", self.installation_id)
            raise