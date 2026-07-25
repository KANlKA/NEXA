# we will load nexa's config from config.yaml into a single config object. This keeps settings centralised.
from dataclasses import dataclass, field
from pathlib import Path
import yaml

# Config.yaml->load_config()->reads yaml if present, else defaults->creates config obj if present->creates config instance->get_config()
DATA_DIR = Path.home() / ".nexa"
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

@dataclass
class Config:
    user_name: str = "User"
    wake_word: str = "hey nexa"
    speaker_similarity_threshold: float = 0.75  # how strictly to match your voice
    data_dir: Path = field(default_factory=lambda: DATA_DIR) # default_factory creates the value when a new Config instance is made
    db_path: Path = field(default_factory=lambda: DATA_DIR / "nexa.db")
    log_path: Path = field(default_factory=lambda: DATA_DIR / "nexa.log")

def load_config() -> Config:
    cfg = Config()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            raw = yaml.safe_load(f) or {} # converts yaml into dict
        # Only override fields that are actually present in the file
        for key, value in raw.items():
            if hasattr(cfg, key):
                setattr(cfg, key, value)

    # Make sure Nexa's data folder exists before anything tries to write to it
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    return cfg

# Singleton pattern: load config once, reuse everywhere.
# Avoids re-reading the YAML file every time a module needs a setting.
_config_instance = None

def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance
