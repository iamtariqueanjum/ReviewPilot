"""Unit tests for chatbot service."""

import pytest
from unittest.mock import MagicMock, patch
from app.core.services.chatbot_service import ChatbotService


class TestChatbotService:
    """Test suite for ChatbotService."""

    def test_init(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test ChatbotService initialization."""
        mock_runnable = MagicMock()
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_runnable):
            
            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)
            
            assert service.owner == "testuser"
            assert service.repo == "test-repo"
            assert service.pr_number == 1
            assert service.github_service is not None
            assert service.embedding_service is not None
            assert service.llm is not None

    def test_init_conversation_id_generation(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test that conversation_id is generated correctly."""
        import hashlib
        mock_runnable = MagicMock()
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_runnable):
            
            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)
            
            expected_id = hashlib.sha256(
                "test-repo:pr:1".encode()
            ).hexdigest()[:16]
            assert service.conversation_id == expected_id

    def test_init_with_different_providers(self, mock_github_service, mock_embedding_service):
        """Test initialization with different LLM providers."""
        mock_runnable = MagicMock()
        mock_llm = MagicMock()
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm) as mock_factory, \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_runnable):
            
            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345, provider="openai")
            
            mock_factory.assert_called_once_with("openai")

    def test_process_query_success(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test successful query processing."""
        mock_github_service.get_pr.return_value = {
            "number": 1,
            "title": "Test PR",
            "head": {"sha": "abc123"}
        }
        mock_github_service.get_pr_diff.return_value = "PR Diff content"
        mock_github_service.get_pr_filepaths.return_value = ["test.py"]
        mock_embedding_service.get_relevant_context.return_value = "Context content"
        
        mock_llm_response = MagicMock()
        mock_llm_response.content = "This is the response from the chatbot"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_llm):
            
            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)
            
            result = service.process_query("testuser", "What are the issues?")
            
            assert result["status"] == "success"
            assert "message" in result
            assert result["message"] == "Query answer comment posted successfully"
            mock_github_service.get_pr.assert_called_once_with(1)
            mock_github_service.get_pr_diff.assert_called_once()
            mock_github_service.get_pr_filepaths.assert_called_once_with(1)
            mock_embedding_service.get_relevant_context.assert_called_once()
            mock_github_service.post_comment.assert_called_once()

    def test_process_query_with_pr_details(self, mock_github_service, mock_embedding_service):
        """Test query processing with PR details."""
        mock_github_service.get_pr.return_value = {
            "number": 1,
            "title": "Test PR",
            "head": {"sha": "abc123"}
        }
        mock_github_service.get_pr_diff.return_value = "PR Diff content"
        mock_github_service.get_pr_filepaths.return_value = ["test.py", "utils.py"]
        mock_embedding_service.get_relevant_context.return_value = "Context content"
        
        mock_llm_response = MagicMock()
        mock_llm_response.content = "Response based on PR context"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_llm):
            
            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)
            
            result = service.process_query("testuser", "What issues are in this PR?")
            
            assert result["status"] == "success"
            # Verify context was passed to embedding service
            mock_embedding_service.get_relevant_context.assert_called_once_with(["test.py", "utils.py"])

    def test_process_query_error_handling(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test error handling in query processing."""
        mock_github_service.get_pr.side_effect = Exception("API Error")
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=MagicMock()):
            
            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)
            
            with pytest.raises(Exception) as exc_info:
                service.process_query("testuser", "What are the issues?")
            
            assert "API Error" in str(exc_info.value)

    def test_process_query_format_response(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test response formatting with sender mention."""
        mock_llm_response = MagicMock()
        mock_llm_response.content = "The issue is in the logic"
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_llm_response
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_chain):

            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)

            result = service.process_query("john_doe", "What are the issues?")

            assert result["status"] == "success"
            posted = mock_github_service.post_comment.call_args[0][1]
            assert "@john_doe" in posted
            assert "The issue is in the logic" in posted

    def test_process_query_long_response(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test processing query with very long response."""
        mock_llm_response = MagicMock()
        mock_llm_response.content = "This is a detailed analysis " * 100
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_llm_response

        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_chain):

            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)

            result = service.process_query("testuser", "Analyze everything")

            assert result["status"] == "success"

    def test_process_query_multiple_calls(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test multiple queries in sequence."""
        mock_llm_response = MagicMock()
        mock_llm_response.content = "Response"
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_llm_response

        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_chain):

            service = ChatbotService("testuser", "test-repo", 1, installation_id=12345)

            result1 = service.process_query("user1", "First question?")
            result2 = service.process_query("user2", "Second question?")

            assert result1["status"] == "success"
            assert result2["status"] == "success"
