from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..models import Game, Platform # Assuming models are one level up

class DataProviderPlugin(ABC):
    """Abstract base class for data provider plugins."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the plugin."""
        pass

    @abstractmethod
    def search_games(self, title: str) -> List[Dict[str, Any]]:
        """Search for games by title. Returns a list of game data dictionaries."""
        pass

    @abstractmethod
    def get_game_details(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific game. Returns a game data dictionary."""
        pass

    @abstractmethod
    def search_platforms(self, name: str) -> List[Dict[str, Any]]:
        """Search for platforms by name. Returns a list of platform data dictionaries."""
        pass