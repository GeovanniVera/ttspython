from dataclasses import dataclass

@dataclass(frozen=True)
class VoiceSettings:
    voice_id: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: float = 1.0
