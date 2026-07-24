import pytest
from unittest.mock import MagicMock
from src.infrastructure.adapters.document_extractor_resolver import DocumentExtractorResolver
from src.domain.exceptions import UnsupportedFileTypeError


class TestDocumentExtractorResolver:
    def _make_adapter(self, supports_ext, text="extracted"):
        adapter = MagicMock()
        adapter.supports.return_value = supports_ext
        adapter.extract_text.return_value = (text, {"success": True})
        return adapter

    def test_supports_when_one_adapter_matches(self):
        a1 = self._make_adapter(False)
        a2 = self._make_adapter(True)
        resolver = DocumentExtractorResolver([a1, a2])
        assert resolver.supports("file.pdf") is True

    def test_supports_false_when_none_match(self):
        a1 = self._make_adapter(False)
        a2 = self._make_adapter(False)
        resolver = DocumentExtractorResolver([a1, a2])
        assert resolver.supports("file.xyz") is False

    def test_delegates_to_correct_adapter(self):
        a1 = self._make_adapter(False)
        a2 = self._make_adapter(True, text="from a2")
        resolver = DocumentExtractorResolver([a1, a2])
        text, meta = resolver.extract_text("file.pdf")
        a2.extract_text.assert_called_once_with("file.pdf")
        assert text == "from a2"

    def test_raises_when_no_adapter_matches(self):
        a1 = self._make_adapter(False)
        resolver = DocumentExtractorResolver([a1])
        with pytest.raises(UnsupportedFileTypeError):
            resolver.extract_text("file.xyz")

    def test_first_adapter_wins(self):
        a1 = self._make_adapter(True, text="from a1")
        a2 = self._make_adapter(True, text="from a2")
        resolver = DocumentExtractorResolver([a1, a2])
        text, _ = resolver.extract_text("file.pdf")
        a1.extract_text.assert_called_once()
        a2.extract_text.assert_not_called()
        assert text == "from a1"
