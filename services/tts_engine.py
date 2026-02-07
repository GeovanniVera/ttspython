import subprocess
import os
import sys
import shutil
import datetime
import asyncio
import edge_tts

# Voice Configuration
VOICE = "es-CL-LorenzoNeural"
#VOICE = "es-MX-JorgeNeural"
# Edge TTS uses this underlying endpoint via websocket (wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1)

class TTSEngine:
    def __init__(self, log_callback=None):
        # Optional: Check if edge-tts is installed/runnable
        self.log_callback = log_callback

    def _log_trace(self, message):
        """Standardized trace logging for external connections."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[TRACE] [{timestamp}] [EXTERNAL-NET] {message}"
        print(full_msg)
        if self.log_callback:
            self.log_callback(full_msg + "\n")

    def save_to_file(self, text, filepath, voice=VOICE, rate="+0%", pitch="+0Hz"):
        """
        Synthesizes text using Edge TTS (Online).
        Args:
            text (str): Input text.
            filepath (str): Output path (.wav).
            voice (str): Voice ID (e.g. es-MX-JorgeNeural).
            rate (str): Speech rate (e.g. +10%, -20%).
            pitch (str): Speech pitch (e.g. +5Hz, -2Hz).
        """
        if not text or not text.strip():
            return

        try:
            # 1. Define temp mp3 path
            temp_mp3 = filepath.replace(".wav", ".mp3")
            
            # Traceability Log: Start
            self._log_trace(f"Connecting to Microsoft Edge TTS Service (Online)")
            self._log_trace(f"Request: Voice='{voice}', Rate='{rate}', Pitch='{pitch}'")

            # 2. Generate Audio using Python Library (No subprocess)
            # This is safe for PyInstaller/Production
            
            async def _generate():
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                await communicate.save(temp_mp3)

            # blocked run 
            asyncio.run(_generate())
            
            self._log_trace("Status: SUCCESS. Media received.")

            if not os.path.exists(temp_mp3):
                 raise Exception("MP3 file was not created by API.")

            # 3. Convert MP3 to WAV using FFmpeg
            # Always prefer imageio_ffmpeg if available for consistency
            ffmpeg_exe = "ffmpeg"
            try:
                import imageio_ffmpeg
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            except ImportError:
                pass # Fallback to system PATH

            print(f"[INTERNAL] Converting MP3 -> WAV via FFmpeg")
            cmd_ffmpeg = [
                ffmpeg_exe,
                "-i", temp_mp3,
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-y",
                filepath
            ]
            
            # CREATE_NO_WINDOW = 0x08000000
            subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, creationflags=0x08000000)
            
            # 4. Cleanup
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)

            if not os.path.exists(filepath):
                 raise Exception("WAV file was not created after conversion.")

        except subprocess.CalledProcessError as e:
             # FFmpeg error usually
             raise Exception(f"Conversion failed: {str(e)}")
        except Exception as e:
             print(f"[EdgeTTS] Error: {e}")
             raise Exception(f"TTS Generation failed: {str(e)}")

    def speak_to_file(self, text, filepath):
        self.save_to_file(text, filepath)
