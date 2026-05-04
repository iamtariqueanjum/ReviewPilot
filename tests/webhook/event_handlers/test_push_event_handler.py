"""Unit tests for push event handler."""

from unittest.mock import patch

from app.webhook.event_handlers.push_event_handler import PushEventHandler


def test_handle_default_branch_logs_update_message():
    payload = {
        "ref": "refs/heads/main",
        "repository": {"default_branch": "main"},
    }
    with patch("builtins.print") as mock_print:
        PushEventHandler().handle(payload)
    assert any(
        "default branch" in str(call).lower() for call in mock_print.call_args_list
    )


def test_handle_feature_branch_does_not_log_default_message():
    payload = {
        "ref": "refs/heads/feature/x",
        "repository": {"default_branch": "main"},
    }
    with patch("builtins.print") as mock_print:
        PushEventHandler().handle(payload)
    joined = " ".join(str(c) for c in mock_print.call_args_list)
    assert "default branch" not in joined.lower()
