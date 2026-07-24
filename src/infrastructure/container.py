from src.infrastructure.adapters.pypdf_adapter import PyPdfAdapter
from src.infrastructure.adapters.plain_text_adapter import PlainTextAdapter
from src.infrastructure.adapters.markdown_adapter import MarkdownAdapter
from src.infrastructure.adapters.document_extractor_resolver import DocumentExtractorResolver
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
        self.journal_adapter = JournalAdapter()
        self.config_repo = ConfigRepository(journal=self.journal_adapter)
        self.cache_repo = CacheRepository(
            cache_dir=self.config_repo.get("cache_path")
        )
        
        self.ocr_adapter = TesseractAdapter(journal=self.journal_adapter)
        self.pdf_extractor = PyPdfAdapter(ocr_adapter=self.ocr_adapter)
        self.plain_text_adapter = PlainTextAdapter()
        self.markdown_adapter = MarkdownAdapter()
        
        self.extractor = DocumentExtractorResolver(
            adapters=[self.pdf_extractor, self.plain_text_adapter, self.markdown_adapter]
        )
        
        self.speech_generator = EdgeTTSAdapter(journal=self.journal_adapter)
        self.audio_processor = FFmpegAdapter()
        
        # Domain Services
        self.text_service = TextService()
        
        # Use Cases
        self.process_pdf_use_case = ProcessPdfToSpeechUseCase(
            extractor=self.extractor,
            generator=self.speech_generator,
            processor=self.audio_processor,
            text_service=self.text_service,
            cache_repo=self.cache_repo,
            journal=self.journal_adapter,
            max_workers=4
        )

# Singleton instance
container = Container()
