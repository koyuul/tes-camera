import json

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ConfigManager]: Error loading config: {e}")
            return {}
    
    def _save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"[ConfigManager]: Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a config value by dot notation (e.g., 'camera_health.enable_mask')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value else default
    
    def set(self, key, value):
        """Set a config value by dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        return self._save_config()