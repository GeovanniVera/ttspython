from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

class DocumentExtractorPort(ABC):
    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """Returns True if this adapter can handle the given file type."""
        pass

    @abstractmethod
    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extracts text and metadata from a document file."""
        pass
