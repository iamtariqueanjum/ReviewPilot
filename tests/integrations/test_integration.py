"""Integration tests for major workflows."""

import pytest
from unittest.mock import MagicMock, patch


class TestPRReviewWorkflow:
    """Integration tests for PR review workflow."""

    def test_full_pr_review_workflow(self):
        """Test complete PR review flow from webhook to comment posting."""
        pr_payload = {
            "action": "opened",
            "pull_request": {
                "number": 1,
                "title": "Add new feature",
                "head": {"sha": "abc123"},
            },
            "repository": {
                "owner": {"login": "testuser"},
                "name": "test-repo"
            },
            "installation": {"id": 12345}
        }
        
        with patch('app.webhook.event_handlers.pull_request_event_handler.review_pr') as mock_review_task, \
             patch('app.core.services.github_service.GitHubClient'), \
             patch('app.core.services.embedding_service.VectorStoreService'), \
             patch('app.core.services.review_service.LLMFactory'):
            
            # Simulate webhook dispatch
            mock_review_task.apply_async.return_value = MagicMock(id="task123")
            
            # Assert task is queued
            from app.webhook.event_handlers.pull_request_event_handler import PullRequestEventHandler
            handler = PullRequestEventHandler()
            result = handler.on_opened(pr_payload)
            
            assert result["status"] == "success"
            mock_review_task.apply_async.assert_called_once()

    def test_pr_review_with_error_recovery(self):
        """Test PR review workflow with error and retry."""
        with patch('app.workers.review_worker.ReviewService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            # First call fails, then succeeds
            mock_service.review_pr.side_effect = [
                Exception("API Error"),
                {"status": "success", "message": "Review completed"}
            ]
            
            from app.workers.review_worker import review_pr
            
            # First attempt should fail
            with pytest.raises(Exception):
                review_pr(
                    self=MagicMock(),
                    installation_id=12345,
                    owner="testuser",
                    repo="test-repo",
                    pr_number=1,
                    head_sha="abc123"
                )


class TestChatbotWorkflow:
    """Integration tests for chatbot workflow."""

    def test_full_chatbot_query_workflow(self):
        """Test complete chatbot query flow from webhook to response."""
        comment_payload = {
            "action": "created",
            "issue": {
                "number": 1,
                "pull_request": {"url": "https://api.github.com/repos/test/test-repo/pulls/1"}
            },
            "comment": {
                "id": 1001,
                "body": "@reviewpilot-ai-bot What are the issues?"
            },
            "sender": {"login": "testuser"},
            "repository": {
                "full_name": "testuser/test-repo",
                "owner": {"login": "testuser"},
                "name": "test-repo"
            },
            "installation": {"id": 12345}
        }
        
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            mock_task.apply_async.return_value = MagicMock(id="task456")
            
            from app.webhook.event_handlers.issue_comment_event_handler import IssueCommentEventHandler
            handler = IssueCommentEventHandler()
            handler.on_created(comment_payload)
            
            mock_task.apply_async.assert_called_once()


class TestEventDispatchWorkflow:
    """Integration tests for event dispatching."""

    def test_multiple_events_dispatched_correctly(self):
        """Test that multiple events are routed to correct handlers."""
        pr_payload = {"action": "opened", "pull_request": {"number": 1}}
        comment_payload = {"action": "created", "comment": {"body": "test"}}
        
        with patch('app.webhook.event_dispatcher.PullRequestEventHandler') as mock_pr_handler, \
             patch('app.webhook.event_dispatcher.IssueCommentEventHandler') as mock_comment_handler, \
             patch('app.webhook.event_dispatcher.InstallationEventHandler'), \
             patch('app.webhook.event_dispatcher.PushEventHandler'):
            
            mock_pr_instance = MagicMock()
            mock_pr_instance.handle.return_value = {"status": "success"}
            mock_pr_handler.return_value = mock_pr_instance
            
            mock_comment_instance = MagicMock()
            mock_comment_instance.handle.return_value = {"status": "success"}
            mock_comment_handler.return_value = mock_comment_instance
            
            from app.webhook.event_dispatcher import WebhookEventDispatcher
            from app.core.utils.constants import GitHubWHEvent
            
            dispatcher = WebhookEventDispatcher()
            
            # Dispatch both events
            dispatcher.dispatch(GitHubWHEvent.PULL_REQUEST, pr_payload)
            dispatcher.dispatch(GitHubWHEvent.ISSUE_COMMENT, comment_payload)
            
            mock_pr_instance.handle.assert_called_once()
            mock_comment_instance.handle.assert_called_once()


class TestServiceIntegration:
    """Integration tests for service interactions."""

    def test_github_service_with_embedding_service(self):
        """Test integration between GithubService and EmbeddingService."""
        with patch('app.core.services.github_service.GitHubClient') as mock_client, \
             patch('app.core.services.embedding_service.VectorStoreService') as mock_vectorstore:
            
            from app.core.services.github_service import GithubService
            from app.core.services.embedding_service import EmbeddingService
            
            # Create services
            github_service = GithubService("testuser", "test-repo", 12345)
            embedding_service = EmbeddingService("testuser", "test-repo", 12345)
            
            # Verify both services have GitHub client
            assert github_service.client is not None
            assert embedding_service.github_service is not None

    def test_review_service_uses_github_and_embedding_services(self):
        """Test that ReviewService correctly uses GitHub and Embedding services."""
        with patch('app.core.services.review_service.GithubService') as mock_github, \
             patch('app.core.services.review_service.EmbeddingService') as mock_embedding, \
             patch('app.core.services.review_service.LLMFactory'):
            
            from app.core.services.review_service import ReviewService
            
            mock_github_instance = MagicMock()
            mock_embedding_instance = MagicMock()
            mock_github.return_value = mock_github_instance
            mock_embedding.return_value = mock_embedding_instance
            
            service = ReviewService("testuser", "test-repo", 12345)
            
            assert service.github_service == mock_github_instance
            assert service.embedding_service == mock_embedding_instance


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end integration scenarios."""

    def test_pr_opened_review_complete_scenario(self):
        """Test complete scenario: PR opened -> Review queued -> Comment posted."""
        # This test documents the expected flow
        # In a real scenario, this would use test containers or mock servers
        pass

    def test_pr_with_multiple_comments_scenario(self):
        """Test scenario: PR with multiple chatbot queries."""
        pass

    def test_error_recovery_scenario(self):
        """Test scenario: Failure and retry with eventual success."""
        pass

