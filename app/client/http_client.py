import requests
import logging
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class APIClient(object):

    def __init__(self, base_url, retries=3, headers=None):
        self.base_url = base_url
        self.headers = headers or {}
        self.session = requests.Session()
        # self.retry_strategy = Retry(
        #     total=retries,
        #     backoff_factor=0.3,
        #     status_forcelist=[429, 500, 502, 503, 504], # TODO add other statuses if needed
        #     allowed_methods=["GET", "POST"], # TODO add other methods if needed
        # )
        # self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        # self.session.mount("http://", self.adapter)
        # self.session.mount("https://", self.adapter)

    def request(self, method, path, params, json, data, headers, timeout=10):
        url = f"{self.base_url}{path}"
        resp = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            data=data,
            headers=self.headers,
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
        return response

