from typing import Tuple, Dict, Any
from charset_normalizer import from_path
from src.domain.ports.document_extractor import DocumentExtractorPort


class PlainTextAdapter(DocumentExtractorPort):
    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith('.txt')

    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        try:
            result = from_path(file_path)
            best = result.best()
            if best:
                encoding = best.encoding
                text = best.output().decode(encoding)
            else:
                encoding = "utf-8"
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            return text.strip(), {"method": "plain_text", "encoding": encoding, "success": True}
        except Exception as e:
            return "", {"error": str(e), "success": False}
