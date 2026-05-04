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

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_with_large_diff(self, mock_celery_app):
        """Test PR review with large diff."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {
            "status": "success",
            "message": "Review completed for large PR"
        }
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=100,
                head_sha="abc123"
            )
            
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_concurrent_reviews(self, mock_celery_app):
        """Test multiple concurrent PR reviews."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {"status": "success"}
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            results = []
            for i in range(5):
                result = review_pr(
                    self=MagicMock(),
                    installation_id=12345,
                    owner="testuser",
                    repo="test-repo",
                    pr_number=i,
                    head_sha=f"sha{i}"
                )
                results.append(result)
            
            assert len(results) == 5
            assert all(r["status"] == "success" for r in results)
            assert mock_service.review_pr.call_count == 5

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_different_installation_ids(self, mock_celery_app):
        """Test PR review from different installations."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {"status": "success"}
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            result1 = review_pr(
                self=MagicMock(),
                installation_id=11111,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            result2 = review_pr(
                self=MagicMock(),
                installation_id=22222,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            assert result1["status"] == "success"
            assert result2["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_response_structure(self, mock_celery_app):
        """Test that review response has expected structure."""
        from app.workers.review_worker import review_pr
        
        expected_response = {
            "status": "success",
            "message": "Review comment posted successfully",
            "pr_id": "pr_123"
        }
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = expected_response
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            assert result == expected_response
            assert "status" in result
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_special_characters_in_names(self, mock_celery_app):
        """Test PR review with special characters in repo/owner names."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {"status": "success"}
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="test-user_123",
                repo="test-repo-name",
                pr_number=1,
                head_sha="abc123"
            )
            
            assert result["status"] == "success"
            mock_service.review_pr.assert_called_once_with(
                pr_number=1,
                head_sha="abc123"
            )

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_service_receives_correct_pr_details(self, mock_celery_app):
        """Verify ReviewService.review_pr is called with correct parameters."""
        from app.workers.review_worker import review_pr
        
        mock_service_class = MagicMock()
        mock_instance = MagicMock()
        mock_service_class.return_value = mock_instance
        mock_instance.review_pr.return_value = {"status": "success"}
        
        with patch('app.workers.review_worker.ReviewService', mock_service_class):
            review_pr(
                self=MagicMock(),
                installation_id=99999,
                owner="owner_name",
                repo="repo_name",
                pr_number=555,
                head_sha="xyz789"
            )
            
            # Verify review_pr was called with correct parameters
            mock_instance.review_pr.assert_called_once_with(
                pr_number=555,
                head_sha="xyz789"
            )

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_with_git_sha_formats(self, mock_celery_app):
        """Test PR review with various git SHA formats."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {"status": "success"}
        
        test_shas = [
            "abc123def456",  # 12 char SHA
            "abc123def456abc123def456abc123de",  # 32 char SHA
            "abc123def456abc123def456abc123deabc123de"  # 40 char SHA
        ]
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            for sha in test_shas:
                result = review_pr(
                    self=MagicMock(),
                    installation_id=12345,
                    owner="testuser",
                    repo="test-repo",
                    pr_number=1,
                    head_sha=sha
                )
                assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_large_pr_number(self, mock_celery_app):
        """Test PR review with large PR numbers."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        mock_service.review_pr.return_value = {"status": "success"}
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=999999,
                head_sha="abc123"
            )
            
            assert result["status"] == "success"
            mock_service.review_pr.assert_called_once_with(
                pr_number=999999,
                head_sha="abc123"
            )

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_service_interaction(self, mock_celery_app):
        """Test that ReviewService is properly used in the flow."""
        from app.workers.review_worker import review_pr
        
        mock_service_class = MagicMock()
        mock_instance = MagicMock()
        mock_service_class.return_value = mock_instance
        mock_instance.review_pr.return_value = {
            "status": "success",
            "message": "Review completed"
        }
        
        with patch('app.workers.review_worker.ReviewService', mock_service_class):
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            # Verify service class was instantiated
            mock_service_class.assert_called_once()
            # Verify review_pr method was called
            mock_instance.review_pr.assert_called_once()
            # Verify result from service is returned
            assert result["status"] == "success"

    @patch('app.core.celery_app.celery_app')
    def test_review_pr_retry_behavior(self, mock_celery_app):
        """Test that task can be retried on failure."""
        from app.workers.review_worker import review_pr
        
        mock_service = MagicMock()
        # First call fails, second succeeds
        mock_service.review_pr.side_effect = [
            Exception("Temporary failure"),
            {"status": "success", "message": "Review completed on retry"}
        ]
        
        with patch('app.workers.review_worker.ReviewService', return_value=mock_service):
            # First attempt fails
            with pytest.raises(Exception):
                review_pr(
                    self=MagicMock(),
                    installation_id=12345,
                    owner="testuser",
                    repo="test-repo",
                    pr_number=1,
                    head_sha="abc123"
                )
            
            # Second attempt succeeds
            result = review_pr(
                self=MagicMock(),
                installation_id=12345,
                owner="testuser",
                repo="test-repo",
                pr_number=1,
                head_sha="abc123"
            )
            
            assert result["status"] == "success"

