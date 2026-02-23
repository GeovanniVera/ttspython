import pytesseract
from PIL import Image
from typing import List
import concurrent.futures
from src.domain.ports.ocr_port import OcrPort
from src.infrastructure.env_manager import env_manager

class TesseractAdapter(OcrPort):
    def __init__(self):
        # Aplicar configuración local desde el env_manager
        env_manager.setup_ocr_environment()

    def _process_single_image(self, img_path: str) -> str:
        """Internal helper to process one image."""
        try:
            return pytesseract.image_to_string(Image.open(img_path), lang='spa+eng')
        except:
            return ""

    def extract_text_from_images(self, image_paths: List[str]) -> str:
        """Processes multiple images in parallel to optimize OCR speed."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map processing to multiple threads
            results = list(executor.map(self._process_single_image, image_paths))
        
        return "\n".join(results)

    def is_available(self) -> bool:
        try:
            # Validamos que el ejecutable responda
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
