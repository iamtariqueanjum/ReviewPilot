"""Pytest configuration and fixtures for ReviewPilot tests."""
from dotenv import load_dotenv
load_dotenv(".env.test")

import pytest
from unittest.mock import Mock, MagicMock, patch
import os
import sys

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock celery and other external dependencies before importing app modules
sys.modules['celery'] = MagicMock()
sys.modules['celery.app'] = MagicMock()
sys.modules['kombu'] = MagicMock()

# Mock the celery_app before it's imported by workers
mock_celery_app = MagicMock()
mock_celery_app.task = MagicMock(return_value=lambda x: x)
sys.modules['app.core.celery_app'] = MagicMock(celery_app=mock_celery_app)


@pytest.fixture
def mock_github_service():
    """Mock GitHub service for testing."""
    mock = MagicMock()
    mock.get_pr.return_value = {
        "number": 1,
        "title": "Test PR",
        "head": {"sha": "abc123"},
        "diff_url": "https://github.com/test/repo/pull/1.diff"
    }
    mock.get_pr_files.return_value = [
        {
            "filename": "test.py",
            "status": "modified",
            "patch": "@@-1,3 +1,4@@\n-old line\n+new line"
        }
    ]
    mock.get_pr_filepaths.return_value = ["test.py"]
    mock.get_pr_diff.return_value = "File: test.py\nStatus: modified\nChanged lines:\n..."
    mock.get_repository.return_value = {
        "name": "test-repo",
        "default_branch": "main"
    }
    mock.get_branch.return_value = {
        "commit": {"sha": "main123"}
    }
    mock.get_file_content.return_value = "def test():\n    pass"
    mock.post_comment.return_value = {"id": 1, "body": "Review comment"}
    return mock


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for testing."""
    mock = MagicMock()
    mock.get_relevant_context.return_value = "Context from repo"
    mock.create_repo_embeddings.return_value = None
    mock.generate_embeddings.return_value = [
        {
            "chunk_id": "1",
            "chunk_content": "def test(): pass",
            "embedding": [0.1, 0.2, 0.3],
            "created_at": "2026-05-04T00:00:00",
            "updated_at": "2026-05-04T00:00:00"
        }
    ]
    return mock


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = MagicMock()
    mock.invoke.return_value = {
        "issues": [{"issue": "Test issue", "suggested_fix": "Test fix"}],
        "summary": "Test summary"
    }
    mock.with_structured_output.return_value = mock
    return mock


@pytest.fixture
def mock_vectorstore_service():
    """Mock vectorstore service for testing."""
    mock = MagicMock()
    mock.upsert_chunks.return_value = None
    mock.filter_chunks_by_filepath.return_value = (
        [
            MagicMock(dict=lambda: {
                "payload": {
                    "file_path": "test.py",
                    "chunk_name": "test_function",
                    "chunk_content": "def test(): pass",
                    "chunk_index": 0
                }
            })
        ],
        []
    )
    return mock


@pytest.fixture
def mock_github_client():
    """Mock GitHub client for testing."""
    mock = MagicMock()
    mock.get_installed_token.return_value = "token123"
    return mock


@pytest.fixture
def sample_pr_payload():
    """Sample GitHub PR webhook payload."""
    return {
        "action": "opened",
        "pull_request": {
            "number": 1,
            "title": "Test PR",
            "head": {"sha": "abc123"},
        },
        "repository": {
            "owner": {"login": "testuser"},
            "name": "test-repo"
        },
        "installation": {"id": 12345}
    }


@pytest.fixture
def sample_issue_comment_payload():
    """Sample GitHub issue comment webhook payload."""
    return {
        "action": "created",
        "issue": {
            "number": 1,
            "pull_request": {"url": "https://api.github.com/repos/testuser/test-repo/pulls/1"}
        },
        "comment": {
            "id": 424242,
            "body": "@reviewpilot-ai-bot What issues do you see?"
        },
        "sender": {"login": "testuser"},
        "repository": {
            "full_name": "testuser/test-repo",
            "owner": {"login": "testuser"},
            "name": "test-repo"
        },
        "installation": {"id": 12345}
    }

