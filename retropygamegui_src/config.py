import os
from dotenv import load_dotenv
from typing import Optional
from .models import APIKeyConfig

class Config:
    """Application configuration handler."""

    def __init__(self, env_path: Optional[str] = None):
        if env_path:
            load_dotenv(dotenv_path=env_path)
        else:
            # Try to find .env in the project root (one level up from retropygamegui_src)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            load_dotenv(dotenv_path=os.path.join(project_root, ".env"))

        self.api_keys = APIKeyConfig(
            thegamesdb_api_key=os.getenv("THEGAMESDB_API_KEY"),
            rawg_io_api_key=os.getenv("RAWG_IO_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            github_pat_token=os.getenv("GITHUB_PAT_TOKEN")
        )

    def get_api_keys(self) -> APIKeyConfig:
        return self.api_keys

# Global config instance
app_config = Config()