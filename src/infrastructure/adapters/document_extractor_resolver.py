from typing import List, Tuple, Dict, Any
from src.domain.ports.document_extractor import DocumentExtractorPort
from src.domain.exceptions import UnsupportedFileTypeError


class DocumentExtractorResolver(DocumentExtractorPort):
    def __init__(self, adapters: List[DocumentExtractorPort]):
        self.adapters = adapters

    def supports(self, file_path: str) -> bool:
        return any(adapter.supports(file_path) for adapter in self.adapters)

    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        for adapter in self.adapters:
            if adapter.supports(file_path):
                return adapter.extract_text(file_path)
        raise UnsupportedFileTypeError(
            f"No adapter found for file type: {file_path}"
        )
