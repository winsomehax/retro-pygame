# retropygamegui_src/plugins/base_plugin.py
class BasePlugin:
    def __init__(self, api_key=None, config=None):
        self.api_key = api_key
        self.config = config # For more complex configurations
        self.name = self.__class__.__name__ # Default name

    def search_game_info(self, game_title: str) -> list[dict]:
        """
        Search for games by title.
        Returns a list of dicts, each representing a game.
        Example: [{'title': 'Super Game', 'source_game_id': 'sg123', 'platform_name': 'Console X', ...}]
        """
        raise NotImplementedError(f"{self.name} must implement search_game_info")

    def search_platform_info(self, platform_name: str) -> list[dict]:
        """
        Search for platforms by name.
        Returns a list of dicts, each representing a platform.
        Example: [{'name': 'Console X', 'source_platform_id': 'cx789', 'manufacturer': 'Retro Corp', ...}]
        """
        raise NotImplementedError(f"{self.name} must implement search_platform_info")

    def get_game_details(self, source_game_id: str) -> dict | None:
        """
        Fetch detailed information for a specific game ID from this plugin's source.
        Returns a dict or None if not found.
        Example: {'title': ..., 'description': ..., 'cover_image_url': ..., 'release_date': ...}
        """
        raise NotImplementedError(f"{self.name} must implement get_game_details")

    def get_platform_details(self, source_platform_id: str) -> dict | None:
        """
        Fetch detailed information for a specific platform ID from this plugin's source.
        Returns a dict or None if not found.
        Example: {'name': ..., 'manufacturer': ..., 'release_year': ..., 'description': ...}
        """
        raise NotImplementedError(f"{self.name} must implement get_platform_details")

    def generate_game_description_ai(self, game_title: str, existing_description: str = None) -> str | None:
        """
        For AI plugins: Generate a game description.
        Returns a string description or None.
        """
        raise NotImplementedError(f"{self.name} does not support AI description generation")

    def get_name(self) -> str:
        return self.name
