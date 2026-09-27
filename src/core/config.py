"""
Centralized Configuration Manager using Pydantic Settings.
Safely loads and validates environment variables from .env.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = DATA_DIR / "temp"
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
MUSIC_DIR = ASSETS_DIR / "music"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Google Gemini 2.0 Flash
    gemini_api_key: Optional[str] = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", validation_alias="GEMINI_MODEL")

    # Ssemble AI Clipping API
    ssemble_api_key: Optional[str] = Field(default=None, validation_alias="SSEMBLE_API_KEY")
    ssemble_base_url: str = Field(default="https://aiclipping.ssemble.com/api/v1", validation_alias="SSEMBLE_BASE_URL")
    ssemble_default_template: str = Field(default="hormozi1", validation_alias="SSEMBLE_DEFAULT_TEMPLATE")

    # Free Stock Footage APIs
    pexels_api_key: Optional[str] = Field(default=None, validation_alias="PEXELS_API_KEY")
    pixabay_api_key: Optional[str] = Field(default=None, validation_alias="PIXABAY_API_KEY")

    # Microsoft Edge Neural TTS Voice
    default_voice: str = Field(default="en-US-ChristopherNeural", validation_alias="DEFAULT_VOICE")
    voice_rate: str = Field(default="+10%", validation_alias="VOICE_RATE")
    voice_pitch: str = Field(default="+0Hz", validation_alias="VOICE_PITCH")

    # YouTube Data API v3
    youtube_client_secrets_file: str = Field(default="config/client_secret.json", validation_alias="YOUTUBE_CLIENT_SECRETS_FILE")
    youtube_token_file: str = Field(default="data/youtube_token.pickle", validation_alias="YOUTUBE_TOKEN_FILE")
    youtube_default_privacy: str = Field(default="unlisted", validation_alias="YOUTUBE_DEFAULT_PRIVACY")
    youtube_category_id: str = Field(default="27", validation_alias="YOUTUBE_CATEGORY_ID")

    # Web Dashboard Settings
    studio_host: str = Field(default="127.0.0.1", validation_alias="STUDIO_HOST")
    studio_port: int = Field(default=8000, validation_alias="STUDIO_PORT")

    @property
    def abs_client_secrets_path(self) -> Path:
        return ROOT_DIR / self.youtube_client_secrets_file

    @property
    def abs_token_path(self) -> Path:
        return ROOT_DIR / self.youtube_token_file


# Global singleton settings instance
settings = Settings()
