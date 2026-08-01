"""
FlexBit AI - User Configuration & Profile Persistence Manager
Manages ~/.flexbit_config.json for persistent user profile, safety tiers, and vision model settings.
"""

import os
import json

CONFIG_FILE_PATH = os.path.expanduser("~/.flexbit_config.json")

DEFAULT_CONFIG = {
    "user_name": "Explorer",
    "user_tier": "Normal",  # "Newbie", "Normal", "Power User"
    "app_launch_count": 1,
    "model_provider": "embedded",  # "embedded", "local_gguf", "lm_studio", "ollama"
    "local_gguf_path": "",
    "server_url": "http://localhost:1234/v1",
    "selected_model": "",
    "n_threads": 4,
    "max_image_dim": 768,
    "sidebar_mode": "dynamic",  # "dynamic", "expanded", "compact"
    "update_mode": "auto_download",  # "notify", "auto_download", "auto_update", "disabled"
    "auto_check_on_startup": True,
    "last_update_check": "",
    "first_run_completed": False
}


class ConfigManager:
    def __init__(self, filepath=CONFIG_FILE_PATH):
        self.filepath = filepath
        self.config = self.load_config()
        self.config["app_launch_count"] = self.config.get("app_launch_count", 0) + 1
        self.save_config()

    def load_config(self):
        """Loads configuration from JSON file, merging with defaults if missing keys."""
        cfg = dict(DEFAULT_CONFIG)
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    cfg.update(loaded)
            except Exception as e:
                print(f"[ConfigManager] Error reading config file: {e}")
        return cfg

    def save_config(self, new_data=None):
        """Saves current configuration to JSON file."""
        if new_data:
            self.config.update(new_data)
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ConfigManager] Error writing config file: {e}")
            return False

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def is_first_run(self):
        return not self.config.get("first_run_completed", False)

    def reset_config(self):
        """Wipes config file and restores defaults."""
        self.config = dict(DEFAULT_CONFIG)
        self.save_config()
        return self.config
