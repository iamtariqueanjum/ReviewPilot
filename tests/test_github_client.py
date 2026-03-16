import logging

from app.clients.github_client import GitHubClient


class DummyClient:
    def __init__(self, response):
        self._response = response

    def call_api(self, method, path, **kwargs):
        return self._response


def test_get_installation_access_token_success():
    # Arrange
    dummy_response = {"status_code": 201, "body": {"token": "fake-token-123"}}
    client = GitHubClient(jwt_token="fake-jwt")
    # inject dummy client to avoid network
    client.client = DummyClient(dummy_response)

    # Act
    token = client.get_installation_access_token(12345)

    # Assert
    assert token == "fake-token-123"


def test_get_installation_access_token_missing_token_logs_error(caplog):
    caplog.set_level(logging.ERROR)
    dummy_response = {"status_code": 201, "body": {}}
    client = GitHubClient(jwt_token="fake-jwt")
    client.client = DummyClient(dummy_response)

    try:
        client.get_installation_access_token(12345)
    except ValueError:
        # expected
        pass
    else:
        raise AssertionError("Expected ValueError when token is missing")

    assert any("did not contain an access token" in rec.message for rec in caplog.records)

