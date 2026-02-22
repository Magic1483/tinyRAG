from pathlib import Path
from threading import Lock

import toml


CONFIG_PATH = Path(__file__).resolve().parent / "CONFIG.toml"
_config_lock = Lock()

def get_config():
    with _config_lock:
        return toml.load(CONFIG_PATH)

def update_config(model:str = None, embedded_model:str = None, model_url:str = None):
    with _config_lock:
        config = toml.load(CONFIG_PATH)
        if model:
            config['server']['model_name'] = model
        if model_url:
            config['server']['model_url'] = model_url
        if embedded_model:
            config['chroma']['EMBED_MODEL'] = embedded_model

        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            toml.dump(config, f)
