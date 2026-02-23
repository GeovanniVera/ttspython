import os
import hashlib
import shutil

class CacheRepository:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_key(self, text: str, voice_id: str, rate: str, pitch: str) -> str:
        """Generates a unique hash for a specific text and voice configuration."""
        data = f"{text}|{voice_id}|{rate}|{pitch}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def get_audio(self, text: str, voice_id: str, rate: str, pitch: str) -> str:
        """Returns the path to the cached audio if it exists, otherwise None."""
        key = self._generate_key(text, voice_id, rate, pitch)
        cache_path = os.path.join(self.cache_dir, f"{key}.mp3")
        return cache_path if os.path.exists(cache_path) else None

    def save_audio(self, text: str, voice_id: str, rate: str, pitch: str, source_path: str):
        """Copies a generated audio file to the cache, overwriting if exists."""
        key = self._generate_key(text, voice_id, rate, pitch)
        cache_path = os.path.join(self.cache_dir, f"{key}.mp3")
        shutil.copy2(source_path, cache_path)

    def clear(self):
        """Deletes all cached files."""
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
