"""Unit tests for embeddings worker."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.parametrize("owner,repo", [("u", "r"), ("org-name", "repo_name")])
@patch("app.core.celery_app.celery_app")
def test_create_repo_embeddings_calls_service(mock_celery_app, owner, repo):
    from app.workers.embeddings_worker import create_repo_embeddings

    mock_embedding = MagicMock()
    with patch(
        "app.workers.embeddings_worker.EmbeddingService", return_value=mock_embedding
    ):
        create_repo_embeddings(
            self=MagicMock(), installation_id=99, owner=owner, repo=repo
        )

    mock_embedding.create_repo_embeddings.assert_called_once()
