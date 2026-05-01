from pathlib import Path
from threading import Lock
import sys
import toml

def resource_path(relative:str) -> Path:
    if getattr(sys,"frozen",False):
        return Path(sys._MEIPASS) / relative
    return Path(__file__).resolve().parent.parent / relative

def app_path() -> Path:
    if getattr(sys,"frozen",False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


DATA_PATH = app_path() / "data"
CONFIG_PATH = DATA_PATH / "CONFIG.toml"

DATA_PATH.mkdir(parents=True, exist_ok=True)

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

# CONFIG
CONFIG      = get_config()
UPLOAD_DIR  = Path(CONFIG['server']['upload_path'])
MODEL_NAME  = CONFIG['server']['model_name']

OLLAMA_URL  = CONFIG['server']['model_url']
PERSIST_DIR = CONFIG['chroma']['PERSIST_DIR']
EMBED_MODEL = CONFIG['chroma']['EMBED_MODEL']

CHUNK_SIZE_CHARS    = int(CONFIG['text_chunking']['chunk_size_chars'])
CHUNK_OVERLAP_CHARS = int(CONFIG['text_chunking']['chuck_overlap_chars'])