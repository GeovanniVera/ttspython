from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

class DocumentExtractorPort(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extracts text and metadata from a document file."""
        pass
