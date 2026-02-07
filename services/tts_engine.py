import pyttsx3
import os

class TTSEngine:
    def __init__(self):
        # We will initialize the engine per call to avoid COM threading issues
        # when running in a secondary thread.
        pass

    def save_to_file(self, text, filepath):
        """
        Synthesizes text to a WAV file.
        This is a blocking call.
        """
        engine = None
        try:
            # Initialize a fresh engine for each chunk to ensure clean COM context
            engine = pyttsx3.init()
            engine.save_to_file(text, filepath)
            engine.runAndWait()
            
            if not os.path.exists(filepath):
                 raise Exception("File was not created by TTS engine.")
                 
        except Exception as e:
            # Re-raise to be caught by caller
             raise Exception(f"TTS Generation failed: {str(e)}")
        finally:
            if engine:
                engine.stop()
                del engine
