from __future__ import annotations

import requests
from requests.exceptions import HTTPError

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.core.utils.constants import ConfigConstants, GitHubRoutes, HTTPMethod
from app.core.utils.github_auth import generate_jwt

from app.core.logger import logger


class GitHubClient(object):

    def __init__(self, installation_id, retries=3, timeout=60):
        self.installation_id = installation_id
        self.base_url = ConfigConstants.GITHUB_API.value
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

    def request(self, method, path, params=None, json=None, data=None, timeout=60, headers=None):
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
        except HTTPError as err:
            logger.exception(f"Error while calling API : {str(err)}: {method} {path}")
            resp = getattr(err, 'response', None)
            if resp is not None:
                try:
                    response = {"status_code": resp.status_code, "body": resp.json()}
                except Exception as e:
                    response = {"status_code": resp.status_code, "body": getattr(resp, 'text', None)}
        print(f"API call: {method} {path} response: {response}")
        return response

    # TODO set installation token in the cache for expiration and regenerate if expired
    def get_installation_access_token(self) -> str:
        try:
            path = GitHubRoutes.INSTALLATION_ACCESS_TOKEN.value.format(installation_id=self.installation_id)
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