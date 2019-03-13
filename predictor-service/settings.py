import json


class Settings:
    # Settings keys
    MODEL_PATH = 'model_path'
    SCALER_PATH = 'scaler_path'

    # Other constants
    CONFIG_PATH = 'config/config.json'

    def __init__(self):
        with open(Settings.CONFIG_PATH) as f:
            self.settings = json.load(f)

    def __getitem__(self, key):
        return self.settings.get(key, '')
