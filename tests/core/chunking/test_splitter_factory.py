"""Unit tests for SplitterFactory."""

import pytest

from app.core.chunking.splitter_factory import SplitterFactory
from app.core.utils.constants import Language


def test_get_splitter_returns_python_splitter():
    factory = SplitterFactory()
    splitter = factory.get_splitter(Language.PYTHON.value)
    assert splitter is not None


def test_get_splitter_unknown_language_raises():
    factory = SplitterFactory()
    with pytest.raises(ValueError, match="Unsupported"):
        factory.get_splitter("Rust")
