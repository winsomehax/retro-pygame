from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Game:
    """Represents a game in the catalog."""
    id: str # Added an ID field, as games.json uses game IDs as keys
    title: str
    platform: str  # Platform slug
    description: Optional[str] = None
    cover_image_path: Optional[str] = None

@dataclass
class Platform:
    """Represents a gaming platform."""
    platform_id: str  # Platform slug
    name: str
    manufacturer: Optional[str] = None
    release_year: Optional[int] = None
    description: Optional[str] = None

@dataclass
class Emulator:
    """Represents an emulator configuration."""
    emulator_id: str  # Emulator slug
    platform_id: str  # Platform slug this emulator belongs to
    name: str
    command: str
    description: Optional[str] = None
    website: Optional[str] = None

@dataclass
class APIKeyConfig:
    """Holds API key configurations."""
    thegamesdb_api_key: Optional[str] = None
    rawg_io_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    github_pat_token: Optional[str] = None