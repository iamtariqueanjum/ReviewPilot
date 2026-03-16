import requests
import logging

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.utils.constants import BaseUrls

logger = logging.getLogger(__name__)


class APIClient(object):

    def __init__(self, retries=3, timeout=10):
        self.base_url = BaseUrls.INTERNAL_API.value
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
            "Accept": "application/json",
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
