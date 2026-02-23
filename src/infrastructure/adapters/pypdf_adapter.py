from pypdf import PdfReader
import os
import tempfile
from typing import Tuple, Dict, Any
from pdf2image import convert_from_path
from src.domain.ports.document_extractor import DocumentExtractorPort
from src.infrastructure.env_manager import env_manager

class PyPdfAdapter(DocumentExtractorPort):
    def __init__(self, ocr_adapter=None):
        self.ocr_adapter = ocr_adapter

    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        try:
            reader = PdfReader(file_path)
            text_content = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            full_text = "\n".join(text_content).strip()
            
            # Si no hay texto, es un escaneo: Activamos OCR local
            if not full_text and len(reader.pages) > 0 and self.ocr_adapter:
                full_text = self._perform_ocr_local(file_path)

            metadata = {
                "num_pages": len(reader.pages),
                "success": True,
                "method": "OCR" if not text_content and full_text else "Direct"
            }
            return full_text, metadata
            
        except Exception as e:
            return "", {"error": str(e), "success": False}

    def _perform_ocr_local(self, pdf_path: str) -> str:
        """Convierte PDF a imagen usando Poppler local y aplica OCR."""
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(
                pdf_path, 
                output_folder=temp_dir,
                poppler_path=env_manager.get_poppler_path() # Inyectamos Poppler local
            )
            
            image_paths = []
            for i, image in enumerate(images):
                img_path = os.path.join(temp_dir, f"page_{i}.png")
                image.save(img_path, "PNG")
                image_paths.append(img_path)
            
            return self.ocr_adapter.extract_text_from_images(image_paths)
