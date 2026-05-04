"""Unit tests for pull request event handler."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.webhook.event_handlers.pull_request_event_handler import PullRequestEventHandler


class TestPullRequestEventHandler:
    """Test suite for PullRequestEventHandler."""

    def test_validate_payload_success(self, sample_pr_payload):
        """Test successful payload validation."""
        installation_id, owner, repo, pr_number, head_sha = PullRequestEventHandler.validate_payload(sample_pr_payload)
        
        assert installation_id == 12345
        assert owner == "testuser"
        assert repo == "test-repo"
        assert pr_number == 1
        assert head_sha == "abc123"

    def test_validate_payload_missing_installation_id(self):
        """Test payload validation with missing installation_id."""
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 1,
                "head": {"sha": "abc123"},
            },
            "repository": {
                "owner": {"login": "testuser"},
                "name": "test-repo"
            },
            "installation": {}  # Missing id
        }
        
        with pytest.raises(HTTPException) as exc_info:
            PullRequestEventHandler.validate_payload(payload)
        
        assert exc_info.value.status_code == 400

    def test_validate_payload_missing_owner(self):
        """Test payload validation with missing owner."""
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 1,
                "head": {"sha": "abc123"},
            },
            "repository": {
                "owner": {},  # Missing login
                "name": "test-repo"
            },
            "installation": {"id": 12345}
        }
        
        with pytest.raises(HTTPException) as exc_info:
            PullRequestEventHandler.validate_payload(payload)
        
        assert exc_info.value.status_code == 400

    def test_on_opened_success(self, sample_pr_payload):
        """Test successful handling of opened PR."""
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'), \
             patch('app.webhook.event_handlers.pull_request_event_handler.review_pr') as mock_review_pr:
            
            handler = PullRequestEventHandler()
            result = handler.on_opened(sample_pr_payload)
            
            assert result["status"] == "success"
            mock_review_pr.apply_async.assert_called_once()

    def test_on_opened_queue_parameters(self, sample_pr_payload):
        """Test that on_opened queues task with correct parameters."""
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'), \
             patch('app.webhook.event_handlers.pull_request_event_handler.review_pr') as mock_review_pr:
            
            handler = PullRequestEventHandler()
            handler.on_opened(sample_pr_payload)
            
            # Verify apply_async was called with correct args
            call_kwargs = mock_review_pr.apply_async.call_args[1]
            assert call_kwargs["args"] == (12345, "testuser", "test-repo", 1, "abc123")
            assert call_kwargs["countdown"] == 10
            assert call_kwargs["retry"] is True

    def test_on_synchronize(self, sample_pr_payload):
        """Test handling of synchronized PR."""
        sample_pr_payload["action"] = "synchronize"
        
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'):
            handler = PullRequestEventHandler()
            # on_synchronize doesn't return anything, just verify it doesn't raise
            handler.on_synchronize(sample_pr_payload)

    def test_on_reopened_success(self, sample_pr_payload):
        """Test successful handling of reopened PR."""
        sample_pr_payload["action"] = "reopened"

        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'), \
             patch('app.webhook.event_handlers.pull_request_event_handler.review_pr') as mock_review_pr:

            handler = PullRequestEventHandler()
            result = handler.on_reopened(sample_pr_payload)

            assert result is None
            mock_review_pr.apply_async.assert_called_once()

    def test_on_closed_merged(self, sample_pr_payload):
        """Test handling of merged PR."""
        sample_pr_payload["action"] = "closed"
        sample_pr_payload["pull_request"]["merged"] = True
        
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'):
            handler = PullRequestEventHandler()
            handler.embedding_service = MagicMock()
            handler.on_closed(sample_pr_payload)
            
            # Verify embedding update was triggered
            handler.embedding_service.update_repo_embeddings.assert_called_once_with(
                "testuser", "test-repo"
            )

    def test_on_closed_not_merged(self, sample_pr_payload):
        """Test handling of closed but not merged PR."""
        sample_pr_payload["action"] = "closed"
        sample_pr_payload["pull_request"]["merged"] = False
        
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'):
            handler = PullRequestEventHandler()
            handler.embedding_service = MagicMock()
            handler.on_closed(sample_pr_payload)
            
            # Verify embedding update was NOT triggered
            handler.embedding_service.update_repo_embeddings.assert_not_called()

    def test_handle_opened_action(self, sample_pr_payload):
        """Test handle method with opened action."""
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'), \
             patch('app.webhook.event_handlers.pull_request_event_handler.review_pr') as mock_review_pr:
            
            handler = PullRequestEventHandler()
            handler.handle(sample_pr_payload)
            
            mock_review_pr.apply_async.assert_called_once()

    def test_handle_synchronize_action(self, sample_pr_payload):
        """Test handle method with synchronize action."""
        sample_pr_payload["action"] = "synchronize"
        
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'):
            handler = PullRequestEventHandler()
            # Should not raise any exception
            handler.handle(sample_pr_payload)

    def test_handle_unknown_action(self, sample_pr_payload):
        """Test handle method with unknown action."""
        sample_pr_payload["action"] = "unknown_action"
        
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'):
            handler = PullRequestEventHandler()
            # Should not raise any exception, just not process anything
            handler.handle(sample_pr_payload)

    def test_validate_payload_with_special_characters(self):
        """Test payload validation with special characters in names."""
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 1,
                "head": {"sha": "abc123"},
            },
            "repository": {
                "owner": {"login": "test_user-123"},
                "name": "test-repo_name"
            },
            "installation": {"id": 12345}
        }
        
        installation_id, owner, repo, pr_number, head_sha = PullRequestEventHandler.validate_payload(payload)
        
        assert installation_id == 12345
        assert owner == "test_user-123"
        assert repo == "test-repo_name"

    def test_validate_payload_with_large_numbers(self):
        """Test payload validation with large numbers."""
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 999999,
                "head": {"sha": "abc123"},
            },
            "repository": {
                "owner": {"login": "testuser"},
                "name": "test-repo"
            },
            "installation": {"id": 9999999}
        }
        
        installation_id, owner, repo, pr_number, head_sha = PullRequestEventHandler.validate_payload(payload)
        
        assert installation_id == 9999999
        assert pr_number == 999999

    def test_init(self):
        """Test PullRequestEventHandler initialization."""
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'):
            handler = PullRequestEventHandler()
            
            assert handler is not None
            assert handler.api_client is not None

    def test_on_opened_message_format(self, sample_pr_payload):
        """Test message format in on_opened response."""
        with patch('app.webhook.event_handlers.pull_request_event_handler.APIClient'), \
             patch('app.webhook.event_handlers.pull_request_event_handler.review_pr') as mock_review_pr:
            
            handler = PullRequestEventHandler()
            result = handler.on_opened(sample_pr_payload)
            
            assert "message" in result
            assert "status" in result
            assert "Review for PR" in result["message"]
            assert "#1" in result["message"]
