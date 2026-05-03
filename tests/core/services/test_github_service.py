"""Unit tests for github service."""

import pytest
from unittest.mock import MagicMock, patch
from app.core.services.github_service import GithubService


class TestGithubService:
    """Test suite for GithubService."""

    def test_init(self, mock_github_client):
        """Test GithubService initialization."""
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client):
            service = GithubService("testuser", "test-repo", 12345)
            
            assert service.owner == "testuser"
            assert service.repo == "test-repo"
            assert service.client is not None
            assert service.pr_service is not None
            assert service.repo_service is not None
            assert service.comment_service is not None

    def test_get_pr_filepaths_success(self, mock_github_client):
        """Test successful retrieval of PR file paths."""
        mock_pr_service = MagicMock()
        mock_pr_service.get_pr_files.return_value = [
            {"filename": "test1.py"},
            {"filename": "test2.py"},
            {"filename": "docs/readme.md"}
        ]
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService', return_value=mock_pr_service), \
             patch('app.core.services.github_service.RepoService'), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.pr_service = mock_pr_service
            
            filepaths = service.get_pr_filepaths(1)
            
            assert len(filepaths) == 3
            assert "test1.py" in filepaths
            assert "test2.py" in filepaths
            assert "docs/readme.md" in filepaths

    def test_get_pr_filepaths_error(self, mock_github_client):
        """Test error handling in get_pr_filepaths."""
        mock_pr_service = MagicMock()
        mock_pr_service.get_pr_files.side_effect = Exception("API Error")
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService', return_value=mock_pr_service), \
             patch('app.core.services.github_service.RepoService'), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.pr_service = mock_pr_service
            
            with pytest.raises(ValueError) as exc_info:
                service.get_pr_filepaths(1)
            
            assert "Error while fetching PR file paths" in str(exc_info.value)

    def test_get_pr_diff_success(self, mock_github_client):
        """Test successful retrieval of PR diff."""
        mock_pr_service = MagicMock()
        mock_pr_service.get_pr_files.return_value = [
            {
                "filename": "test.py",
                "status": "modified",
                "patch": "@@-1,3 +1,4@@\n-old\n+new"
            }
        ]
        
        mock_repo_service = MagicMock()
        mock_repo_service.get_file_content.return_value = "line1\nline2\nnew line\nline3"
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService', return_value=mock_pr_service), \
             patch('app.core.services.github_service.RepoService', return_value=mock_repo_service), \
             patch('app.core.services.github_service.CommentService'), \
             patch('app.core.services.github_service.parse_new_lines', return_value=[{"line": 1, "content": "new line"}]), \
             patch('app.core.services.github_service.get_new_file_line_number', return_value=3), \
             patch('app.core.services.github_service.prepare_changed_lines_text', return_value="1: new line"):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.pr_service = mock_pr_service
            service.repo_service = mock_repo_service
            
            diff = service.get_pr_diff(1, "abc123")
            
            assert diff is not None
            assert "test.py" in diff

    def test_get_pr_diff_error(self, mock_github_client):
        """Test error handling in get_pr_diff."""
        mock_pr_service = MagicMock()
        mock_pr_service.get_pr_files.side_effect = Exception("API Error")
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService', return_value=mock_pr_service), \
             patch('app.core.services.github_service.RepoService'), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.pr_service = mock_pr_service
            
            with pytest.raises(ValueError) as exc_info:
                service.get_pr_diff(1, "abc123")
            
            assert "Error while fetching PR diff" in str(exc_info.value)

    def test_post_comment(self, mock_github_client):
        """Test posting a comment."""
        mock_comment_service = MagicMock()
        mock_comment_service.post_comment.return_value = {"id": 1, "body": "Test comment"}
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService'), \
             patch('app.core.services.github_service.RepoService'), \
             patch('app.core.services.github_service.CommentService', return_value=mock_comment_service):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.comment_service = mock_comment_service
            
            result = service.post_comment(1, "Test comment")
            
            assert result is not None
            mock_comment_service.post_comment.assert_called_once_with(1, "Test comment")

