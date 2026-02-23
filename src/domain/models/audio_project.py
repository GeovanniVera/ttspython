from dataclasses import dataclass, field
from typing import List, Optional
from src.domain.models.voice_settings import VoiceSettings

@dataclass
class AudioProject:
    pdf_path: str
    output_dir: str
    voice_settings: VoiceSettings
    base_name: str
    extracted_text: Optional[str] = None
    chunks: List[str] = field(default_factory=list)
    generated_files: List[str] = field(default_factory=list)
    final_mp3_path: Optional[str] = None
    bgm_path: Optional[str] = None
    bgm_volume: float = 0.2
