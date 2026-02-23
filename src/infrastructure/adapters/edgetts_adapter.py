import asyncio
import edge_tts
import os
import time
import random
from src.domain.models.voice_settings import VoiceSettings
from src.domain.ports.speech_generator import SpeechGeneratorPort

class EdgeTTSAdapter(SpeechGeneratorPort):
    def generate_speech(self, text: str, output_path: str, settings: VoiceSettings) -> None:
        """Generates MP3 directly with Exponential Backoff for resilience."""
        if not text or not text.strip():
            return
            
        # Force MP3 extension
        if output_path.endswith('.wav'):
            output_path = output_path.replace('.wav', '.mp3')

        MAX_RETRIES = 5
        base_delay = 2.0 # Start with 2 seconds

        success = False
        last_exception = None

        for attempt in range(MAX_RETRIES):
            try:
                async def _generate():
                    communicate = edge_tts.Communicate(
                        text, 
                        settings.voice_id, 
                        rate=settings.rate, 
                        pitch=settings.pitch
                    )
                    await communicate.save(output_path)

                asyncio.run(_generate())
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    success = True
                    break
                else:
                    raise Exception("Audio file is empty or missing.")
                    
            except Exception as e:
                last_exception = e
                # Exponential backoff: base * 2^attempt + jitter
                wait_time = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                
                # If it's likely a rate limit or connection issue, we log and wait
                print(f"[RETRY {attempt+1}/{MAX_RETRIES}] Error detectado: {e}. Reintentando en {wait_time:.2f}s...")
                time.sleep(wait_time)
        
        if not success:
            raise Exception(f"Fallo crítico tras {MAX_RETRIES} intentos: {last_exception}")
