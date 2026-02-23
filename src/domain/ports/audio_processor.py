from abc import ABC, abstractmethod
from typing import List

class AudioProcessorPort(ABC):
    @abstractmethod
    def merge_wavs(self, wav_paths: List[str], output_path: str) -> str:
        """Merges multiple WAV files into one."""
        pass

    @abstractmethod
    def mix_with_bgm(self, voice_path: str, bgm_path: str, output_path: str, voice_vol: float, bgm_vol: float) -> str:
        """Mixes voice audio with background music."""
        pass

    @abstractmethod
    def convert_to_mp3(self, input_path: str) -> str:
        """Converts an audio file to MP3 format."""
        pass

    @abstractmethod
    def generate_silence(self, duration: float, output_path: str) -> str:
        """Generates a silent audio file (MP3)."""
        pass
