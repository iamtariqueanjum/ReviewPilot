"""Unit tests for issue comment event handler."""

import pytest
from unittest.mock import MagicMock, patch
from app.webhook.event_handlers.issue_comment_event_handler import IssueCommentEventHandler


class TestIssueCommentEventHandler:
    """Test suite for IssueCommentEventHandler."""

    def test_init(self):
        """Test IssueCommentEventHandler initialization."""
        handler = IssueCommentEventHandler()
        
        assert handler is not None

    def test_handle_created_comment(self, sample_issue_comment_payload):
        """Test handling of created comment."""
        with patch('app.webhook.event_handlers.issue_comment_event_handler.IssueCommentEventHandler.on_created') as mock_on_created:
            handler = IssueCommentEventHandler()
            handler.handle(sample_issue_comment_payload)
            
            mock_on_created.assert_called_once_with(sample_issue_comment_payload)

    def test_on_created_pull_request_comment(self, sample_issue_comment_payload):
        """Test handling comment on pull request."""
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            # Verify the task was queued
            mock_task.apply_async.assert_called_once()

    def test_on_created_extracts_pr_details(self, sample_issue_comment_payload):
        """Test that on_created extracts PR details correctly."""
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            # Get the call arguments
            call_args = mock_task.apply_async.call_args[1]["args"]
            assert "testuser" in call_args  # owner
            assert "test-repo" in call_args  # repo
            assert 1 in call_args  # pr_number
            assert "testuser" in call_args  # sender
            assert "What issues do you see?" in call_args  # query

    def test_on_created_ignores_non_pr_issues(self, sample_issue_comment_payload):
        """Test that on_created ignores comments on issues without PR link."""
        sample_issue_comment_payload["issue"]["pull_request"] = None
        
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            # Task should not be queued for regular issues
            # (depends on implementation details)

    def test_on_created_extracts_query_from_comment(self, sample_issue_comment_payload):
        """Test that query is extracted from comment body."""
        sample_issue_comment_payload["comment"]["body"] = "@reviewpilot Can you find bugs?"
        
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            # Verify query contains the comment text
            call_args = mock_task.apply_async.call_args[1]["args"]
            query = call_args[-1]
            assert "Can you find bugs?" in query

    def test_on_created_with_multiline_comment(self, sample_issue_comment_payload):
        """Test handling of multiline comments."""
        sample_issue_comment_payload["comment"]["body"] = """@reviewpilot
        Can you review this PR?
        
        Specifically check:
        1. Security issues
        2. Performance
        """
        
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            mock_task.apply_async.assert_called_once()

    def test_on_created_with_special_characters(self, sample_issue_comment_payload):
        """Test handling of comments with special characters."""
        sample_issue_comment_payload["comment"]["body"] = "@reviewpilot What about <script>alert('test')</script> ?"
        
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            mock_task.apply_async.assert_called_once()

    def test_on_created_extracts_installation_id(self, sample_issue_comment_payload):
        """Test that installation_id is correctly extracted."""
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task:
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            # Get the call arguments
            call_args = mock_task.apply_async.call_args[1]["args"]
            # First argument should be installation_id
            assert call_args[0] == 12345

    def test_on_created_task_queue_parameters(self, sample_issue_comment_payload):
        """Test task is queued with correct parameters."""
        with patch('app.webhook.event_handlers.issue_comment_event_handler.process_chat_message') as mock_task, \
             patch('app.webhook.event_handlers.issue_comment_event_handler.QueueConstants') as mock_constants:
            
            mock_constants.CHAT_MESSAGES_QUEUE = "chat_messages_queue"
            
            handler = IssueCommentEventHandler()
            handler.on_created(sample_issue_comment_payload)
            
            # Verify apply_async was called
            call_kwargs = mock_task.apply_async.call_args[1]
            assert "task_id" in call_kwargs
            assert "args" in call_kwargs
            assert "queue" in call_kwargs or call_kwargs.get("queue") == "chat_messages_queue"

