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

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_with_long_query(self, mock_celery):
        """Test processing very long queries."""
        from app.workers.chatbot_worker import process_chat_message
        
        mock_service = MagicMock()
        long_query = "Can you explain " * 100 + "this code?"
        mock_service.process_query.return_value = {"status": "success", "response": "Long response"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query=long_query
            )
            
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_with_different_installation_ids(self, mock_celery):
        """Test processing queries from different installations."""
        from app.workers.chatbot_worker import process_chat_message
        
        mock_service = MagicMock()
        mock_service.process_query.return_value = {"status": "success"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result1 = process_chat_message(
                self=MagicMock(),
                installation_id=11111,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query="Query 1"
            )
            
            result2 = process_chat_message(
                self=MagicMock(),
                installation_id=22222,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query="Query 2"
            )
            
            assert result1["status"] == "success"
            assert result2["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_verifies_service_call(self, mock_celery):
        """Test that process_query is called with correct arguments."""
        from app.workers.chatbot_worker import process_chat_message
        
        mock_service = MagicMock()
        mock_service.process_query.return_value = {"status": "success"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=5,
                sender="alice",
                query="How does this work?"
            )
            
            # Verify process_query was called with sender and query
            mock_service.process_query.assert_called_once_with("alice", "How does this work?")

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_with_unicode_characters(self, mock_celery):
        """Test processing queries with unicode characters."""
        from app.workers.chatbot_worker import process_chat_message
        
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
                query="What about 你好 مرحبا привет こんにちは?"
            )
            
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_with_code_snippet(self, mock_celery):
        """Test processing queries containing code snippets."""
        from app.workers.chatbot_worker import process_chat_message
        
        mock_service = MagicMock()
        mock_service.process_query.return_value = {"status": "success"}
        
        code_query = """
        Can you review this code:
        ```python
        def calculate(x, y):
            return x + y
        ```
        Is it correct?
        """
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query=code_query
            )
            
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_returns_response_structure(self, mock_celery):
        """Test that response has expected structure."""
        from app.workers.chatbot_worker import process_chat_message
        
        expected_response = {
            "status": "success",
            "message": "Query processed successfully",
            "response_id": "resp123"
        }
        
        mock_service = MagicMock()
        mock_service.process_query.return_value = expected_response
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query="Test?"
            )
            
            assert result == expected_response
            assert "status" in result
            assert "message" in result

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_with_empty_query(self, mock_celery):
        """Test handling of empty query."""
        from app.workers.chatbot_worker import process_chat_message
        
        mock_service = MagicMock()
        mock_service.process_query.return_value = {"status": "error", "message": "Empty query"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            result = process_chat_message(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                sender="john_doe",
                query=""
            )
            
            mock_service.process_query.assert_called_once_with("john_doe", "")

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_with_mention_in_query(self, mock_celery):
        """Test processing query with @mentions."""
        from app.workers.chatbot_worker import process_chat_message
        
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
                query="@alice @bob what do you think about this?"
            )
            
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_concurrent_calls(self, mock_celery):
        """Test multiple concurrent chat message processing."""
        from app.workers.chatbot_worker import process_chat_message
        
        mock_service = MagicMock()
        mock_service.process_query.return_value = {"status": "success"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', return_value=mock_service):
            # Simulate concurrent calls
            results = []
            for i in range(5):
                result = process_chat_message(
                    self=MagicMock(),
                    installation_id=12345,
                    owner="testuser",
                    repo="test-repo",
                    pr_number=i,
                    sender=f"user_{i}",
                    query=f"Query {i}?"
                )
                results.append(result)
            
            assert len(results) == 5
            assert all(r["status"] == "success" for r in results)
            assert mock_service.process_query.call_count == 5

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_with_url_in_query(self, mock_celery):
        """Test processing query containing URLs."""
        from app.workers.chatbot_worker import process_chat_message
        
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
                query="Check https://github.com/user/repo/issues/123 please"
            )
            
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_process_chat_message_service_initialization_parameters(self, mock_celery):
        """Verify ChatbotService receives correct initialization parameters."""
        from app.workers.chatbot_worker import process_chat_message
        
        mock_service_class = MagicMock()
        mock_instance = MagicMock()
        mock_service_class.return_value = mock_instance
        mock_instance.process_query.return_value = {"status": "success"}
        
        with patch('app.workers.chatbot_worker.ChatbotService', mock_service_class):
            process_chat_message(
                self=MagicMock(),
                installation_id=99999,
                owner="another_user",
                repo="another_repo",
                pr_number=42,
                sender="sender_name",
                query="test query"
            )
            
            # Verify service was initialized with correct parameters
            mock_service_class.assert_called_once_with(
                "another_user",
                "another_repo",
                42,
                installation_id=99999
            )


