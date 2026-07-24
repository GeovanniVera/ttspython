from typing import Tuple, Dict, Any
from markdown_it import MarkdownIt
from src.domain.ports.document_extractor import DocumentExtractorPort


class MarkdownAdapter(DocumentExtractorPort):
    def supports(self, file_path: str) -> bool:
        lowered = file_path.lower()
        return lowered.endswith('.md') or lowered.endswith('.markdown')

    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()

            md = MarkdownIt()
            tokens = md.parse(raw)
            parts = []
            heading_level = 0

            for token in tokens:
                if token.type == "fence":
                    parts.append("[bloque de código]")
                    continue
                if token.type == "code_block":
                    parts.append("[bloque de código]")
                    continue

                if token.type == "heading_open":
                    heading_level = int(token.tag[1])
                    continue
                if token.type == "heading_close":
                    heading_level = 0
                    continue

                if token.type == "inline" and token.children:
                    inline_text = self._render_inline(token.children)
                    if heading_level == 1:
                        parts.append(f"Título: {inline_text}")
                    elif heading_level >= 2:
                        parts.append(f"Subtítulo: {inline_text}")
                    else:
                        parts.append(inline_text)
                    continue

                if token.type == "paragraph_open" or token.type == "paragraph_close":
                    continue

                if token.type in ("bullet_list_open", "bullet_list_close",
                                  "ordered_list_open", "ordered_list_close",
                                  "list_item_open", "list_item_close"):
                    continue

                if token.type in ("blockquote_open", "blockquote_close"):
                    continue

                if token.type == "image":
                    alt = token.content or ""
                    parts.append(f"imagen: {alt}")
                    continue

            text = "\n".join(p for p in parts if p).strip()
            return text, {"method": "markdown", "success": True}
        except Exception as e:
            return "", {"error": str(e), "success": False}

    def _render_inline(self, children) -> str:
        parts = []
        for child in children:
            if child.type == "text":
                parts.append(child.content)
            elif child.type == "softbreak":
                parts.append("\n")
            elif child.type == "code_inline":
                parts.append(child.content)
            elif child.type == "image":
                alt = child.content or ""
                parts.append(f"imagen: {alt}")
            elif child.type == "link_open":
                continue
            elif child.type == "link_close":
                continue
            elif child.type == "em_open" or child.type == "em_close":
                continue
            elif child.type == "strong_open" or child.type == "strong_close":
                continue
            elif child.type == "softbreak":
                parts.append("\n")
            elif child.type == "hardbreak":
                parts.append("\n")
            elif child.type == "s_open" or child.type == "s_close":
                continue
            else:
                if child.content:
                    parts.append(child.content)
        return "".join(parts)
