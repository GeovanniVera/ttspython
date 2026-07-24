import os
import pytest
from src.infrastructure.adapters.plain_text_adapter import PlainTextAdapter


class TestPlainTextAdapter:
    def setup_method(self):
        self.adapter = PlainTextAdapter()

    def test_supports_txt(self):
        assert self.adapter.supports("document.txt") is True
        assert self.adapter.supports("DOCUMENT.TXT") is True

    def test_not_supports_pdf(self):
        assert self.adapter.supports("document.pdf") is False

    def test_not_supports_md(self):
        assert self.adapter.supports("document.md") is False

    def test_extract_utf8(self, tmp_path):
        txt = tmp_path / "sample.txt"
        txt.write_text("Hola mundo, este es un archivo UTF-8.", encoding="utf-8")
        text, meta = self.adapter.extract_text(str(txt))
        assert text == "Hola mundo, este es un archivo UTF-8."
        assert meta["success"] is True
        assert meta["method"] == "plain_text"
        assert "encoding" in meta

    def test_extract_latin1(self, tmp_path):
        txt = tmp_path / "latin.txt"
        txt.write_bytes("Café con acento: áéíóúñ".encode("latin-1"))
        text, meta = self.adapter.extract_text(str(txt))
        assert meta["success"] is True
        assert len(text) > 0

    def test_extract_nonexistent_file(self):
        text, meta = self.adapter.extract_text("/no/such/file.txt")
        assert text == ""
        assert meta["success"] is False
        assert "error" in meta
