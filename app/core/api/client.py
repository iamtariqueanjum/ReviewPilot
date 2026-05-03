import requests

from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError

from urllib3.util.retry import Retry
from app.core.logger import logger
from app.core.utils.constants import ConfigConstants


class APIClient:
    """Class representing a client to call internal APIs with retry mechanism and error handling."""

    def __init__(self, retries=3, timeout=60):
        self.base_url = ConfigConstants.INTERNAL_API.value
        self.session = requests.Session()
        self.retry_strategy = Retry(
            total=retries,
            backoff_factor=0.3,
            status_forcelist=[408, 409, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "PUT", "DELETE"],
        )
        self.timeout = timeout
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)
        self.headers = {
            "Accept": "application/json",
        }


    def request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        resp = self.session.request(
            method=method.upper(),
            url=url,
            params=kwargs.get('params'),
            json=kwargs.get('json'),
            data=kwargs.get('data'),
            headers=kwargs.get('headers') or self.headers,
            timeout=kwargs.get('timeout') or self.timeout
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
            logger.exception("Error while calling API : %s", str(err))
            resp = getattr(err, 'response', None)
            if resp is not None:
                try:
                    response = {"status_code": resp.status_code, "body": resp.json()}
                except Exception as _:
                    response = {"status_code": resp.status_code, "body": getattr(resp, 'text', None)}
        return response
