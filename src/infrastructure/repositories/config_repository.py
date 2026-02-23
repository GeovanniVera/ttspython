import json
import os

CONFIG_FILE = "settings.json"

class ConfigRepository:
    def __init__(self):
        self.config = self.load_config()

    def _get_default_music_path(self):
        """Returns the default Windows Music folder path."""
        try:
            return os.path.join(os.environ['USERPROFILE'], 'Music')
        except:
            return os.path.join(os.getcwd(), 'output')

    def load_config(self):
        default_path = self._get_default_music_path()
        base_config = {
            "voice": "es-MX-JorgeNeural",
            "rate_val": 0,
            "pitch_val": 0,
            "output_path": default_path
        }
        
        if not os.path.exists(CONFIG_FILE):
            return base_config
        
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Merge saved with defaults for missing keys
                for k, v in base_config.items():
                    if k not in saved:
                        saved[k] = v
                return saved
        except Exception as e:
            print(f"Error loading config: {e}")
            return base_config

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
