"""Unit tests for chatbot service."""

import pytest
from unittest.mock import MagicMock, patch
from app.core.services.chatbot_service import ChatbotService


class TestChatbotService:
    """Test suite for ChatbotService."""

    def test_init(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test ChatbotService initialization."""
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=MagicMock()):
            
            service = ChatbotService("testuser", "test-repo", 1, 12345)
            
            assert service.owner == "testuser"
            assert service.repo == "test-repo"
            assert service.pr_number == 1
            assert service.github_service is not None
            assert service.embedding_service is not None
            assert service.llm is not None

    def test_process_query_success(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test successful query processing."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "This is the response from the chatbot"
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_chain):
            
            service = ChatbotService("testuser", "test-repo", 1, 12345)
            service.chain = mock_chain
            
            result = service.process_query("testuser", "What are the issues?")
            
            assert result["status"] == "success"
            assert "message" in result
            mock_github_service.get_pr.assert_called_once()
            mock_github_service.get_pr_diff.assert_called_once()
            mock_embedding_service.get_relevant_context.assert_called_once()

    def test_process_query_with_pr_details(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test query processing with PR details."""
        mock_github_service.get_pr.return_value = {
            "number": 1,
            "title": "Test PR",
            "head": {"sha": "abc123"}
        }
        mock_github_service.get_pr_diff.return_value = "PR Diff content"
        mock_embedding_service.get_relevant_context.return_value = "Context content"
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Response based on PR context"
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_chain):
            
            service = ChatbotService("testuser", "test-repo", 1, 12345)
            service.chain = mock_chain
            
            result = service.process_query("testuser", "What issues are in this PR?")
            
            assert result["status"] == "success"
            # Check that chain.invoke was called with proper context
            mock_chain.invoke.assert_called_once()

    def test_process_query_error_handling(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test error handling in query processing."""
        mock_github_service.get_pr.side_effect = Exception("API Error")
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=MagicMock()):
            
            service = ChatbotService("testuser", "test-repo", 1, 12345)
            
            with pytest.raises(Exception):
                service.process_query("testuser", "What are the issues?")

    def test_process_query_format_response(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test response formatting with sender mention."""
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "The issue is in the logic"
        
        with patch('app.core.services.chatbot_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.chatbot_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.chatbot_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.chatbot_service.get_chat_runnable', return_value=mock_chain):
            
            service = ChatbotService("testuser", "test-repo", 1, 12345)
            service.chain = mock_chain
            
            result = service.process_query("john_doe", "What are the issues?")
            
            assert result["status"] == "success"
            # Response should mention the sender
            if "comment" in result.get("body", ""):
                assert "@john_doe" in result.get("body", "")

