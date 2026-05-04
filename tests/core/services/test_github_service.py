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

    def test_get_pr(self, mock_github_client):
        """Test getting PR details."""
        mock_pr_service = MagicMock()
        mock_pr_service.get_pr.return_value = {"number": 1, "title": "Test PR"}
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService', return_value=mock_pr_service), \
             patch('app.core.services.github_service.RepoService'), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.pr_service = mock_pr_service
            
            pr = service.get_pr(1)
            
            assert pr["number"] == 1
            assert pr["title"] == "Test PR"

    def test_get_repository(self, mock_github_client):
        """Test getting repository details."""
        mock_repo_service = MagicMock()
        mock_repo_service.get_repository.return_value = {"name": "test-repo", "default_branch": "main"}
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService'), \
             patch('app.core.services.github_service.RepoService', return_value=mock_repo_service), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.repo_service = mock_repo_service
            
            repo = service.get_repository()
            
            assert repo["name"] == "test-repo"
            assert repo["default_branch"] == "main"

    def test_get_branch(self, mock_github_client):
        """Test getting branch details."""
        mock_repo_service = MagicMock()
        mock_repo_service.get_branch.return_value = {"name": "main", "commit": {"sha": "abc123"}}
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService'), \
             patch('app.core.services.github_service.RepoService', return_value=mock_repo_service), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.repo_service = mock_repo_service
            
            branch = service.get_branch("main")
            
            assert branch["name"] == "main"

    def test_get_file_content(self, mock_github_client):
        """Test getting file content."""
        mock_repo_service = MagicMock()
        mock_repo_service.get_file_content.return_value = "def hello():\n    print('hello')"
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService'), \
             patch('app.core.services.github_service.RepoService', return_value=mock_repo_service), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.repo_service = mock_repo_service
            
            content = service.get_file_content("test.py", "abc123")
            
            assert "def hello()" in content

    def test_get_tree_recursive(self, mock_github_client):
        """Test getting tree recursively."""
        mock_repo_service = MagicMock()
        mock_repo_service.get_tree_recursive.return_value = {
            "tree": [
                {"path": "file1.py", "type": "blob"},
                {"path": "dir/", "type": "tree"}
            ]
        }
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService'), \
             patch('app.core.services.github_service.RepoService', return_value=mock_repo_service), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.repo_service = mock_repo_service
            
            tree = service.get_tree_recursive("abc123")
            
            assert len(tree["tree"]) == 2

    def test_get_blob_content(self, mock_github_client):
        """Test getting blob content."""
        mock_repo_service = MagicMock()
        mock_repo_service.get_blob_content.return_value = "blob content"
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService'), \
             patch('app.core.services.github_service.RepoService', return_value=mock_repo_service), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.repo_service = mock_repo_service
            
            content = service.get_blob_content("blob123")
            
            assert content == "blob content"

    def test_get_pr_filepaths_empty(self, mock_github_client):
        """Test getting PR filepaths when PR has no changes."""
        mock_pr_service = MagicMock()
        mock_pr_service.get_pr_files.return_value = []
        
        with patch('app.core.services.github_service.GitHubClient', return_value=mock_github_client), \
             patch('app.core.services.github_service.PrService', return_value=mock_pr_service), \
             patch('app.core.services.github_service.RepoService'), \
             patch('app.core.services.github_service.CommentService'):
            
            service = GithubService("testuser", "test-repo", 12345)
            service.pr_service = mock_pr_service
            
            filepaths = service.get_pr_filepaths(1)
            
            assert filepaths == []
