"""Unit tests for webhook event dispatcher."""

import pytest
from unittest.mock import MagicMock, patch
from app.webhook.event_dispatcher import WebhookEventDispatcher
from app.core.utils.constants import GitHubWHEvent


class TestWebhookEventDispatcher:
    """Test suite for WebhookEventDispatcher."""

    def test_init(self):
        """Test WebhookEventDispatcher initialization."""
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler'), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler'), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            dispatcher = WebhookEventDispatcher()
            
            assert dispatcher.handlers is not None
            assert GitHubWHEvent.PULL_REQUEST in dispatcher.handlers
            assert GitHubWHEvent.INSTALLATION in dispatcher.handlers
            assert GitHubWHEvent.ISSUE_COMMENT in dispatcher.handlers
            assert GitHubWHEvent.PUSH in dispatcher.handlers

    def test_dispatch_pull_request_event(self, sample_pr_payload):
        """Test dispatching pull request event."""
        mock_handler = MagicMock()
        mock_handler.handle.return_value = {"status": "success"}
        
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler', return_value=mock_handler), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler'), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            dispatcher = WebhookEventDispatcher()
            result = dispatcher.dispatch(GitHubWHEvent.PULL_REQUEST, sample_pr_payload)
            
            mock_handler.handle.assert_called_once_with(sample_pr_payload)
            assert result["status"] == "success"

    def test_dispatch_issue_comment_event(self, sample_issue_comment_payload):
        """Test dispatching issue comment event."""
        mock_handler = MagicMock()
        mock_handler.handle.return_value = {"status": "success"}
        
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler'), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler', return_value=mock_handler), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            dispatcher = WebhookEventDispatcher()
            result = dispatcher.dispatch(GitHubWHEvent.ISSUE_COMMENT, sample_issue_comment_payload)
            
            mock_handler.handle.assert_called_once_with(sample_issue_comment_payload)
            assert result["status"] == "success"

    def test_dispatch_installation_event(self):
        """Test dispatching installation event."""
        payload = {"action": "created", "installation": {"id": 12345}}
        mock_handler = MagicMock()
        mock_handler.handle.return_value = {"status": "success"}
        
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler'), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler', return_value=mock_handler), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler'), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            dispatcher = WebhookEventDispatcher()
            result = dispatcher.dispatch(GitHubWHEvent.INSTALLATION, payload)
            
            mock_handler.handle.assert_called_once_with(payload)
            assert result["status"] == "success"

    def test_dispatch_push_event(self):
        """Test dispatching push event."""
        payload = {"ref": "refs/heads/main", "repository": {"name": "test-repo"}}
        mock_handler = MagicMock()
        mock_handler.handle.return_value = {"status": "success"}
        
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler'), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler'), \
             patch('app.webhook.event_dispatcher.PushEventHandler', return_value=mock_handler):
            
            dispatcher = WebhookEventDispatcher()
            result = dispatcher.dispatch(GitHubWHEvent.PUSH, payload)
            
            mock_handler.handle.assert_called_once_with(payload)
            assert result["status"] == "success"

    def test_dispatch_unknown_event(self):
        """Test dispatching unknown event."""
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler'), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler'), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            dispatcher = WebhookEventDispatcher()
            result = dispatcher.dispatch("unknown_event", {})
            
            assert result["status"] == "error"
            assert "not found" in result["error"]

    def test_dispatch_event_handler_error(self, sample_pr_payload):
        """Test error handling when handler raises exception."""
        mock_handler = MagicMock()
        mock_handler.handle.side_effect = Exception("Handler error")
        
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler', return_value=mock_handler), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler'), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            dispatcher = WebhookEventDispatcher()
            
            # Whether the exception is propagated or handled depends on implementation
            # This test documents the current behavior
            with pytest.raises(Exception):
                dispatcher.dispatch(GitHubWHEvent.PULL_REQUEST, sample_pr_payload)

    def test_dispatch_multiple_events_in_sequence(self):
        """Test dispatching multiple events in sequence."""
        pr_payload = {"action": "opened", "pull_request": {"number": 1}}
        comment_payload = {"action": "created", "comment": {"body": "test"}}
        
        mock_pr_handler = MagicMock()
        mock_pr_handler.handle.return_value = {"status": "success"}
        
        mock_comment_handler = MagicMock()
        mock_comment_handler.handle.return_value = {"status": "success"}
        
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler', return_value=mock_pr_handler), \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler', return_value=mock_comment_handler), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            dispatcher = WebhookEventDispatcher()
            
            result1 = dispatcher.dispatch(GitHubWHEvent.PULL_REQUEST, pr_payload)
            result2 = dispatcher.dispatch(GitHubWHEvent.ISSUE_COMMENT, comment_payload)
            
            assert result1["status"] == "success"
            assert result2["status"] == "success"
            mock_pr_handler.handle.assert_called_once()
            mock_comment_handler.handle.assert_called_once()

