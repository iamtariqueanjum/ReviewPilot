"""Unit tests for chatbot worker."""

import pytest
from unittest.mock import MagicMock, patch
from app.workers.chatbot_worker import process_chat_message


class TestChatbotWorker:
    """Test suite for chatbot_worker."""

    def test_process_chat_message_success(self):
        """Test successful chat message processing."""
        mock_service = MagicMock()
        mock_service.process_query.return_value = {
            "status": "success",
            "message": "Query processed"
        }
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query="What are the issues?"
            )
            
            assert result["status"] == "success"
            mock_service.process_query.assert_called_once_with(
                "john_doe",
                "What are the issues?"
            )

    def test_process_chat_message_with_different_query(self):
        """Test processing different chat queries."""
        mock_service = MagicMock()
        mock_service.process_query.return_value = {
            "status": "success",
            "message": "Query processed"
        }
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="jane_doe",
                query="Explain this change"
            )
            
            assert result["status"] == "success"
            mock_service.process_query.assert_called_once_with(
                "jane_doe",
                "Explain this change"
            )

    def test_process_chat_message_error_handling(self):
        """Test error handling in process_chat_message."""
        mock_service = MagicMock()
        mock_service.process_query.side_effect = Exception("Processing failed")
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            with pytest.raises(Exception) as exc_info:
                process_chat_message(
                    self=MagicMock(),
                    installation_id=12345,
                    owner="testuser",
                    repo="test-repo",
                    pr_number=1,
                    sender="john_doe",
                    query="What are the issues?"
                )
            
            assert "Processing failed" in str(exc_info.value)

    def test_process_chat_message_initializes_service_correctly(self):
        """Test that ChatbotService is initialized with correct parameters."""
        mock_service_class = MagicMock()
        mock_service_instance = MagicMock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.process_query.return_value = {"status": "success"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', mock_service_class):
            process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query="What are the issues?"
            )
            
            mock_service_class.assert_called_once_with(
                "testuser",
                "test-repo",
                1,
                installation_id=12345
            )

    def test_process_chat_message_multiple_queries(self):
        """Test processing multiple chat queries."""
        mock_service = MagicMock()
        mock_service.process_query.return_value = {"status": "success"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            # First query
            result1 = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query="First question?"
            )
            
            # Second query
            result2 = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="jane_doe",
                query="Second question?"
            )
            
            assert result1["status"] == "success"
            assert result2["status"] == "success"
            assert mock_service.process_query.call_count == 2

    def test_process_chat_message_with_special_characters(self):
        """Test processing queries with special characters."""
        mock_service = MagicMock()
        mock_service.process_query.return_value = {"status": "success"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query="@bot Can you check the code? <script>alert('test')</script>"
            )
            
            assert result["status"] == "success"

