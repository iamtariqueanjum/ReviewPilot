"""Unit tests for vector store Qdrant client wrapper."""

from unittest.mock import MagicMock, patch

from app.integrations.vectorstore.client import QdrantClientWrapper


@patch("app.integrations.vectorstore.client.QdrantClient")
def test_qdrant_wrapper_stores_host_port_and_exposes_client(mock_qdrant_cls):
    mock_inner = MagicMock()
    mock_qdrant_cls.return_value = mock_inner

    wrapper = QdrantClientWrapper()

    assert wrapper.host == "localhost"
    assert wrapper.port == 6333
    mock_qdrant_cls.assert_called_once_with(host="localhost", port=6333)
    assert wrapper.get_client() is mock_inner
