
import json
import os

CONFIG_FILE = "settings.json"

class ConfigManager:
    DEFAULT_CONFIG = {
        "voice": "Jorge (México)",
        "rate": 12.0,
        "pitch": -7.0,
        "last_folder": ""
    }

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.DEFAULT_CONFIG.copy()

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
