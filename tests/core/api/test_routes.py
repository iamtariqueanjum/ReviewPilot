"""Tests for FastAPI webhook routes."""

from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from app.core.utils.constants import APIEndpoints
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_github_webhook_rejects_invalid_signature(client):
    with patch("app.core.api.routes.verify_github_webhook", return_value=False) as verify:
        response = client.post(
            APIEndpoints.GITHUB_WEBHOOK.value,
            json={"action": "opened"},
            headers={
                "x-hub-signature-256": "sha256=deadbeef",
                "x-github-event": "pull_request",
            },
        )
    assert response.status_code == 204
    verify.assert_called_once()


def test_github_webhook_dispatches_when_signature_valid(client):
    with patch("app.core.api.routes.verify_github_webhook", return_value=True), patch(
        "app.core.api.routes.WebhookEventDispatcher"
    ) as mock_dispatcher_class:
        instance = MagicMock()
        mock_dispatcher_class.return_value = instance
        response = client.post(
            APIEndpoints.GITHUB_WEBHOOK.value,
            json={"action": "opened", "pull_request": {"number": 1}},
            headers={
                "x-hub-signature-256": "sha256=good",
                "x-github-event": "pull_request",
            },
        )
    assert response.status_code == 204
    instance.dispatch.assert_called_once()
