"""Unit tests for LLMFactory."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.utils.constants import LLMProvider
from app.integrations.llm.llm_factory import LLMFactory


@patch("app.integrations.llm.llm_factory.ChatOpenAI")
def test_get_llm_openai(mock_chat_openai):
    mock_chat_openai.return_value = MagicMock()
    llm = LLMFactory.get_llm(LLMProvider.OPENAI.value)
    assert llm is not None
    mock_chat_openai.assert_called_once()


def test_get_llm_unsupported_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        LLMFactory.get_llm("unknown-provider")


@patch("app.integrations.llm.llm_factory.ChatOpenAI")
def test_get_llm_none_uses_default(mock_chat_openai):
    mock_chat_openai.return_value = MagicMock()
    LLMFactory.get_llm(None)
    mock_chat_openai.assert_called_once()
