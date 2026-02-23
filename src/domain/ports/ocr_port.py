from abc import ABC, abstractmethod
from typing import List

class OcrPort(ABC):
    @abstractmethod
    def extract_text_from_images(self, image_paths: List[str]) -> str:
        """Recognizes text from a list of image file paths."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the OCR engine is installed and configured."""
        pass
