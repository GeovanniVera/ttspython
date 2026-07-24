import json
import os
from pathlib import Path

CONFIG_FILE = "settings.json"

class ConfigRepository:
    def __init__(self, journal=None):
        self.journal = journal
        self.config = self.load_config()

    def _get_default_music_path(self):
        """Returns the default Windows Music folder path."""
        try:
            return os.path.join(os.environ['USERPROFILE'], 'Music')
        except:
            return os.path.join(os.getcwd(), 'output')

    def _get_default_cache_path(self):
        """Returns the default cache directory based on the OS."""
        return str(Path.home() / ".cache" / "pdf-to-speech")

    @staticmethod
    def _clamp(val, lo, hi):
        """Clamp value to [lo, hi] range, returning the default if conversion fails."""
        try:
            return max(lo, min(hi, float(val)))
        except (TypeError, ValueError):
            return lo

    def _merge_with_defaults(self, saved):
        """Fill missing keys from base_config and clamp volume values."""
        defaults = self._default_config()
        for k, v in defaults.items():
            if k not in saved:
                saved[k] = v
        # Clamp volume values from legacy/migrated configs
        saved["voice_vol"] = self._clamp(saved.get("voice_vol", 1.0), 0.0, 1.0)
        saved["bgm_vol"]   = self._clamp(saved.get("bgm_vol", 0.2), 0.0, 1.0)
        return saved

    def _default_config(self):
        default_path = self._get_default_music_path()
        return {
            "voice": "es-MX-JorgeNeural",
            "rate_val": 0,
            "pitch_val": 0,
            "output_path": default_path,
            "cache_path": self._get_default_cache_path(),
            "voice_vol": 1.0,
            "bgm_vol": 0.2,
            "appearance_mode": "Dark",
        }

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return self._default_config()
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return self._merge_with_defaults(saved)
        except Exception as e:
            if self.journal:
                self.journal.warning(f"Error al cargar configuración: {e}")
            return self._default_config()

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            if self.journal:
                self.journal.warning(f"Error al guardar configuración: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
