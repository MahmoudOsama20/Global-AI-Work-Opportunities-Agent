from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project Root Directory Resolution
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database configuration
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'database' / 'opportunities.db'}"
    DATABASE_SYNC_URL: str = f"sqlite:///{DATA_DIR / 'database' / 'opportunities.db'}"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "none"  # "none", "gemini", "openai", "anthropic", "groq"
    LLM_MODEL: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Search Provider Configuration for Discovery
    SEARCH_PROVIDER: str = "duckduckgo"
    SEARCH_API_KEY: Optional[str] = None
    SEARXNG_BASE_URL: Optional[str] = None

    # Browser Automation & User Profile
    PLAYWRIGHT_USER_DATA_DIR: str = str(DATA_DIR / "browser_profiles" / "default")
    PLAYWRIGHT_HEADLESS: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(DATA_DIR / "logs" / "app.log")

    # Pipeline limits
    MAX_CONCURRENT_CONNECTORS: int = 5
    CONNECTOR_TIMEOUT_SECONDS: int = 30
    REQUEST_TIMEOUT_SECONDS: int = 20
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )


class ConfigManager:
    """Loads and caches YAML configurations from the config/ directory."""

    def __init__(self, config_dir: Path = CONFIG_DIR):
        self.config_dir = config_dir
        self._profile: Optional[Dict[str, Any]] = None
        self._sources: Optional[Dict[str, Any]] = None
        self._scoring: Optional[Dict[str, Any]] = None
        self._exclusions: Optional[Dict[str, Any]] = None

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        file_path = self.config_dir / filename
        if not file_path.exists():
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get_profile(self, reload: bool = False) -> Dict[str, Any]:
        if self._profile is None or reload:
            self._profile = self._load_yaml("profile.yaml")
        return self._profile

    def get_sources(self, reload: bool = False) -> List[Dict[str, Any]]:
        if self._sources is None or reload:
            data = self._load_yaml("sources.yaml")
            self._sources = data.get("sources", [])
        return self._sources

    def get_scoring(self, reload: bool = False) -> Dict[str, Any]:
        if self._scoring is None or reload:
            self._scoring = self._load_yaml("scoring.yaml")
        return self._scoring

    def get_exclusions(self, reload: bool = False) -> Dict[str, Any]:
        if self._exclusions is None or reload:
            self._exclusions = self._load_yaml("exclusions.yaml")
        return self._exclusions


settings = AppSettings()
config_manager = ConfigManager()
