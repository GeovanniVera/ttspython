from src.infrastructure.adapters.pypdf_adapter import PyPdfAdapter
from src.infrastructure.adapters.edgetts_adapter import EdgeTTSAdapter
from src.infrastructure.adapters.ffmpeg_adapter import FFmpegAdapter
from src.infrastructure.adapters.tesseract_adapter import TesseractAdapter
from src.infrastructure.repositories.config_repository import ConfigRepository
from src.infrastructure.repositories.cache_repository import CacheRepository
from src.infrastructure.adapters.journal_adapter import JournalAdapter
from src.domain.services.text_service import TextService
from src.application.use_cases.process_pdf_to_speech import ProcessPdfToSpeechUseCase

class Container:
    def __init__(self):
        # Repositories & Adapters
        self.config_repo = ConfigRepository()
        self.cache_repo = CacheRepository() # Persistent Cache
        self.journal_adapter = JournalAdapter()
        
        self.ocr_adapter = TesseractAdapter()
        self.pdf_extractor = PyPdfAdapter(ocr_adapter=self.ocr_adapter)
        
        self.speech_generator = EdgeTTSAdapter()
        self.audio_processor = FFmpegAdapter()
        
        # Domain Services
        self.text_service = TextService()
        
        # Use Cases
        self.process_pdf_use_case = ProcessPdfToSpeechUseCase(
            extractor=self.pdf_extractor,
            generator=self.speech_generator,
            processor=self.audio_processor,
            text_service=self.text_service,
            journal=self.journal_adapter,
            max_workers=4
        )

# Singleton instance
container = Container()
