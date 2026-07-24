import pytest
from src.infrastructure.adapters.markdown_adapter import MarkdownAdapter


class TestMarkdownAdapter:
    def setup_method(self):
        self.adapter = MarkdownAdapter()

    def test_supports_md(self):
        assert self.adapter.supports("doc.md") is True
        assert self.adapter.supports("DOC.MD") is True

    def test_supports_markdown(self):
        assert self.adapter.supports("doc.markdown") is True

    def test_not_supports_pdf(self):
        assert self.adapter.supports("doc.pdf") is False

    def test_not_supports_txt(self):
        assert self.adapter.supports("doc.txt") is False

    def test_headers_to_titulo(self, tmp_path):
        md = tmp_path / "headers.md"
        md.write_text("# Título Principal\n## Subtítulo uno\n", encoding="utf-8")
        text, meta = self.adapter.extract_text(str(md))
        assert "Título: Título Principal" in text
        assert "Subtítulo: Subtítulo uno" in text
        assert meta["success"] is True

    def test_code_blocks_replaced(self, tmp_path):
        md = tmp_path / "code.md"
        md.write_text("Antes\n```python\nprint('hello')\n```\nDespués", encoding="utf-8")
        text, _ = self.adapter.extract_text(str(md))
        assert "[bloque de código]" in text
        assert "print" not in text

    def test_inline_code_no_backticks(self, tmp_path):
        md = tmp_path / "inline.md"
        md.write_text("Use `variable` here.", encoding="utf-8")
        text, _ = self.adapter.extract_text(str(md))
        assert "variable" in text
        assert "`" not in text

    def test_links_only_visible_text(self, tmp_path):
        md = tmp_path / "links.md"
        md.write_text("[Google](https://google.com)", encoding="utf-8")
        text, _ = self.adapter.extract_text(str(md))
        assert "Google" in text
        assert "https://google.com" not in text

    def test_bold_italic_stripped(self, tmp_path):
        md = tmp_path / "format.md"
        md.write_text("**negrita** e *italica*", encoding="utf-8")
        text, _ = self.adapter.extract_text(str(md))
        assert "negrita" in text
        assert "italica" in text
        assert "**" not in text
        assert "*" not in text

    def test_images_render(self, tmp_path):
        md = tmp_path / "images.md"
        md.write_text("![Descripción de foto](img.png)", encoding="utf-8")
        text, _ = self.adapter.extract_text(str(md))
        assert "imagen: Descripción de foto" in text

    def test_error_nonexistent_file(self):
        text, meta = self.adapter.extract_text("/no/such/file.md")
        assert text == ""
        assert meta["success"] is False
        assert "error" in meta
