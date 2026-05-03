"""Unit tests for review worker."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from sys import modules

# Mock celery before importing
modules['celery'] = MagicMock()
modules['celery.app'] = MagicMock()


class TestReviewWorker:
    """Test suite for review_worker."""

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_success(self, mock_celery_app):
        """Test successful PR review task."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {
            "status": "success",
            "message": "Review completed"
        }
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            assert result["status"] == "success"
            mock_service.review_pr.assert_called_once_with(
                pr_number=1,
                head_sha="abc123"
            )

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_with_different_repo(self, mock_celery_app):
        """Test PR review for different repository."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {
            "status": "success",
            "message": "Review completed"
        }
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="anotheruser",
                repo="another-repo",
                pr_number=42,
                head_sha="def456"
            )
            
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_error_handling(self, mock_celery_app):
        """Test error handling in review_pr task."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.side_effect = Exception("Review failed")
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            with pytest.raises(Exception) as exc_info:
                review_pr(
                    self=MagicMock(),
                    installation_id=12345,
                    owner="testuser",
                    repo="test-repo",
                    pr_number=1,
                    head_sha="abc123"
                )
            
            assert "Review failed" in str(exc_info.value)

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_initializes_service_correctly(self, mock_celery_app):
        """Test that ReviewService is initialized with correct parameters."""
        from app.workers.review_worker import review_pr
        
        mock_service_class = MagicMock()
        mock_service_instance = MagicMock()
        mock_service_class.return_value = mock_service_instance
        mock_service_instance.review_pr.return_value = {"status": "success"}
        
        with patch('app.workers.review_worker.ReviewService', mock_service_class):
            review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            mock_service_class.assert_called_once_with(
                "testuser",
                "test-repo",
                12345
            )

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_multiple_calls(self, mock_celery_app):
        """Test multiple PR reviews in sequence."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {"status": "success"}
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            # Test first PR
            result1 = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            # Test second PR
            result2 = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=2,
                head_sha="def456"
            )
            
            assert result1["status"] == "success"
            assert result2["status"] == "success"
            assert mock_service.review_pr.call_count == 2

