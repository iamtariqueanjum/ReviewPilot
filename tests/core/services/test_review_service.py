"""Unit tests for review service."""

import pytest
from unittest.mock import MagicMock, patch, call
from app.core.services.review_service import ReviewService


class TestReviewService:
    """Test suite for ReviewService."""

    def test_init(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test ReviewService initialization."""
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm):
            
            service = ReviewService("testuser", "test-repo", 12345)
            
            assert service.owner == "testuser"
            assert service.repo == "test-repo"
            assert service.installation_id == 12345
            assert service.github_service is not None
            assert service.embedding_service is not None
            assert service.llm is not None

    def test_review_pr_success(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test successful PR review."""
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.review_service.get_markdown_review_comment', return_value="## Review\nTest issue"):
            
            service = ReviewService("testuser", "test-repo", 12345)
            service.chain = MagicMock()
            service.chain.invoke.return_value = {
                "issues": [{"issue": "Test issue", "suggested_fix": "Test fix"}],
                "summary": "Test summary"
            }
            
            result = service.review_pr(pr_number=1, head_sha="abc123")
            
            assert result["status"] == "success"
            assert "message" in result
            mock_github_service.post_comment.assert_called_once()

    def test_review_pr_get_pr_diff_error(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test PR review when getting diff fails."""
        mock_github_service.get_pr_diff.side_effect = Exception("API Error")
        
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm):
            
            service = ReviewService("testuser", "test-repo", 12345)
            
            with pytest.raises(Exception):
                service.review_pr(pr_number=1, head_sha="abc123")

    def test_review_pr_with_multiple_files(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test PR review with multiple files."""
        mock_github_service.get_pr_diff.return_value = "File: test1.py\nStatus: modified\n...\nFile: test2.py\nStatus: added\n..."
        
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.review_service.get_markdown_review_comment', return_value="## Review"):
            
            service = ReviewService("testuser", "test-repo", 12345)
            service.chain = MagicMock()
            service.chain.invoke.return_value = {"issues": [], "summary": "All good"}
            
            result = service.review_pr(pr_number=1, head_sha="abc123")
            
            assert result["status"] == "success"

    def test_review_pr_with_no_issues(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test PR review when no issues are found."""
        mock_github_service.get_pr_diff.return_value = "No significant changes"
        
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.review_service.get_markdown_review_comment', return_value="✅ All good!"):
            
            service = ReviewService("testuser", "test-repo", 12345)
            service.chain = MagicMock()
            service.chain.invoke.return_value = {"issues": [], "summary": "No issues"}
            
            result = service.review_pr(pr_number=1, head_sha="abc123")
            
            assert result["status"] == "success"
            assert "message" in result

    def test_review_pr_context_retrieval_error(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test error handling when context retrieval fails."""
        mock_embedding_service.get_relevant_context.side_effect = Exception("Context retrieval failed")
        
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm):
            
            service = ReviewService("testuser", "test-repo", 12345)
            
            with pytest.raises(Exception):
                service.review_pr(pr_number=1, head_sha="abc123")

    def test_review_pr_with_security_issues(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test PR review detecting security issues."""
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.review_service.get_markdown_review_comment', return_value="🔒 Security issues found"):
            
            service = ReviewService("testuser", "test-repo", 12345)
            service.chain = MagicMock()
            service.chain.invoke.return_value = {
                "issues": [
                    {"issue": "SQL injection vulnerability", "severity": "critical"}
                ],
                "summary": "Security issue found"
            }
            
            result = service.review_pr(pr_number=1, head_sha="abc123")
            
            assert result["status"] == "success"

    def test_review_pr_calls_all_services(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test that review_pr calls all required services."""
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.review_service.get_markdown_review_comment', return_value="Review"):
            
            service = ReviewService("testuser", "test-repo", 12345)
            service.chain = MagicMock()
            service.chain.invoke.return_value = {"issues": [], "summary": "Good"}
            
            service.review_pr(pr_number=1, head_sha="abc123")
            
            # Verify all services were called
            mock_github_service.get_pr_diff.assert_called_once()
            mock_github_service.get_pr_filepaths.assert_called_once()
            mock_embedding_service.get_relevant_context.assert_called_once()
            mock_github_service.post_comment.assert_called_once()

    def test_review_pr_with_large_pr(self, mock_github_service, mock_embedding_service, mock_llm):
        """Test PR review with large PR."""
        large_diff = "File: " + "\n---\n".join([f"file{i}.py" for i in range(100)])
        mock_github_service.get_pr_diff.return_value = large_diff
        
        with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
             patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm), \
             patch('app.core.services.review_service.get_markdown_review_comment', return_value="Review"):
            
            service = ReviewService("testuser", "test-repo", 12345)
            service.chain = MagicMock()
            service.chain.invoke.return_value = {"issues": [], "summary": "Good"}
            
            result = service.review_pr(pr_number=1, head_sha="abc123")
            
            assert result["status"] == "success"

    def test_review_pr_with_different_providers(self, mock_embedding_service):
        """Test PR review with different LLM providers."""
        providers = ["openai", "google", "anthropic"]
        
        for provider in providers:
            mock_llm = MagicMock()
            mock_github_service = MagicMock()
            
            with patch('app.core.services.review_service.GithubService', return_value=mock_github_service), \
                 patch('app.core.services.review_service.EmbeddingService', return_value=mock_embedding_service), \
                 patch('app.core.services.review_service.LLMFactory.get_llm', return_value=mock_llm), \
                 patch('app.core.services.review_service.get_markdown_review_comment', return_value="Review"):
                
                service = ReviewService("testuser", "test-repo", 12345, provider=provider)
                service.chain = MagicMock()
                service.chain.invoke.return_value = {"issues": [], "summary": "Good"}
                
                result = service.review_pr(pr_number=1, head_sha="abc123")
                
                assert result["status"] == "success"
