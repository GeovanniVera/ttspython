import subprocess
import os
import sys
import datetime

# Voice Configuration
VOICE = "es-CL-LorenzoNeural"
#VOICE = "es-MX-JorgeNeural"
# Edge TTS uses this underlying endpoint via websocket (wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1)

class TTSEngine:
    def __init__(self):
        # Optional: Check if edge-tts is installed/runnable
        pass

    def _log_trace(self, message):
        """Standardized trace logging for external connections."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[TRACE] [{timestamp}] [EXTERNAL-NET] {message}")

    def save_to_file(self, text, filepath):
        """
        Synthesizes text using Edge TTS (Online).
        Generates MP3 and converts it to WAV for compatibility.
        """
        if not text or not text.strip():
            return

        try:
            # 1. Define temp mp3 path
            temp_mp3 = filepath.replace(".wav", ".mp3")
            
            # Traceability Log: Start
            self._log_trace(f"Connecting to Microsoft Edge TTS Service (Online)")
            self._log_trace(f"Endpoint: wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1")
            self._log_trace(f"Request: Voice='{VOICE}', TextLength={len(text)} chars")

            # 2. Run Edge TTS CLI
            # Command: edge-tts --voice es-MX-JorgeNeural --text "TEXT" --write-media output.mp3
            cmd_tts = [
                "edge-tts",
                "--voice", VOICE,
                "--text", text,
                "--write-media", temp_mp3
            ]
            
            # Run TTS process
            process = subprocess.run(cmd_tts, capture_output=True, text=True)
            
            if process.returncode != 0:
                self._log_trace(f"Status: FAILED. Error: {process.stderr}")
                raise Exception(f"EdgeTTS Error: {process.stderr}")
            
            self._log_trace("Status: SUCCESS. Media received.")

            if not os.path.exists(temp_mp3):
                 raise Exception("MP3 file was not created by EdgeTTS.")

            # 3. Convert MP3 to WAV using FFmpeg
            # We overwrite filepath (-y) if it exists
            print(f"[INTERNAL] Converting MP3 -> WAV via FFmpeg")
            cmd_ffmpeg = [
                "ffmpeg",
                "-i", temp_mp3,
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-y",
                filepath
            ]
            
            subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            
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
