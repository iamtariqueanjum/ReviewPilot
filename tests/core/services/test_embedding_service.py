"""Unit tests for embedding service."""

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from app.core.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test suite for EmbeddingService."""

    def test_init(self, mock_github_service, mock_vectorstore_service):
        """Test EmbeddingService initialization."""
        with patch('app.core.services.embedding_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.embedding_service.VectorStoreService', return_value=mock_vectorstore_service):
            
            service = EmbeddingService("testuser", "test-repo", 12345)
            
            assert service.owner == "testuser"
            assert service.repo == "test-repo"
            assert service.installation_id == 12345
            assert service.github_service is not None
            assert service.vectorstore_service is not None

    def test_create_repo_embeddings_success(self, mock_github_service, mock_vectorstore_service):
        """Test successful repo embeddings creation."""
        mock_github_service.get_repository.return_value = {
            "name": "test-repo",
            "default_branch": "main"
        }
        mock_github_service.get_branch.return_value = {
            "commit": {"sha": "main123"}
        }
        mock_github_service.get_tree_recursive.return_value = {
            "tree": [
                {
                    "type": "blob",
                    "size": 1000,
                    "path": "test.py",
                    "sha": "blob123"
                }
            ]
        }
        mock_github_service.get_blob_content.return_value = "def test():\n    pass"
        
        with patch('app.core.services.embedding_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.embedding_service.VectorStoreService', return_value=mock_vectorstore_service), \
             patch('app.core.services.embedding_service.SplitterFactory') as mock_splitter_factory, \
             patch.object(EmbeddingService, 'generate_embeddings', return_value=[]):
            
            mock_splitter = MagicMock()
            mock_splitter.split.return_value = [
                {"chunk_id": "1", "chunk_content": "def test(): pass"}
            ]
            mock_splitter_factory.return_value.get_splitter.return_value = mock_splitter
            
            service = EmbeddingService("testuser", "test-repo", 12345)
            service.create_repo_embeddings()
            
            mock_vectorstore_service.upsert_chunks.assert_called_once()

    def test_generate_embeddings(self, mock_github_service, mock_vectorstore_service):
        """Test generating embeddings for chunks."""
        chunks = [
            {"chunk_id": "1", "chunk_content": "def test(): pass"},
            {"chunk_id": "2", "chunk_content": "class TestClass: pass"}
        ]
        
        with patch('app.core.services.embedding_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.embedding_service.VectorStoreService', return_value=mock_vectorstore_service), \
             patch('app.core.services.embedding_service.EmbeddingService.call_openai_embeddings') as mock_embed:
            
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_embed.return_value = mock_response
            
            service = EmbeddingService("testuser", "test-repo", 12345)
            result = service.generate_embeddings(chunks)
            
            assert len(result) == 2
            assert "embedding" in result[0]
            assert "created_at" in result[0]
            assert "updated_at" in result[0]

    def test_get_relevant_context(self, mock_github_service, mock_vectorstore_service):
        """Test getting relevant context from vectorstore."""
        file_paths = ["test.py", "src/main.py"]
        
        with patch('app.core.services.embedding_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.embedding_service.VectorStoreService', return_value=mock_vectorstore_service):
            
            service = EmbeddingService("testuser", "test-repo", 12345)
            context = service.get_relevant_context(file_paths)
            
            assert context is not None
            assert "File Path:" in context
            assert "Function:" in context
            assert "Code:" in context

    def test_generate_code_summaries(self, mock_github_service, mock_vectorstore_service):
        """Test generating code summaries."""
        chunks = [
            {"chunk_id": "1", "chunk_content": "def test(): pass"}
        ]
        
        with patch('app.core.services.embedding_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.embedding_service.VectorStoreService', return_value=mock_vectorstore_service), \
             patch('app.core.services.embedding_service.LLMFactory.get_llm') as mock_llm_factory, \
             patch('app.core.services.embedding_service.ChatPromptTemplate.from_template') as mock_prompt:
            
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="This is a test function")
            mock_llm_factory.return_value = mock_llm
            
            mock_prompt_template = MagicMock()
            mock_prompt_template.__or__ = MagicMock(return_value=mock_llm)
            mock_prompt.return_value = mock_prompt_template
            
            result = EmbeddingService.generate_code_summaries(chunks)
            
            assert "summary" in result[0]

    def test_call_openai_embeddings_success(self, mock_github_service, mock_vectorstore_service):
        """Test calling OpenAI embeddings API."""
        with patch('app.core.services.embedding_service.GithubService', return_value=mock_github_service), \
             patch('app.core.services.embedding_service.VectorStoreService', return_value=mock_vectorstore_service), \
             patch('app.core.services.embedding_service.OpenAI') as mock_openai:
            
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            result = EmbeddingService.call_openai_embeddings("test content")
            
            assert result is not None
            mock_client.embeddings.create.assert_called_once()

