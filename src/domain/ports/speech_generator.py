from abc import ABC, abstractmethod
from src.domain.models.voice_settings import VoiceSettings

class SpeechGeneratorPort(ABC):
    @abstractmethod
    def generate_speech(self, text: str, output_path: str, settings: VoiceSettings) -> None:
        """Generates audio from text and saves it to a file."""
        pass
