from .base_plugin import BasePlugin

class TheGamesDBPlugin(BasePlugin):
    def __init__(self, api_key=None, config=None):
        super().__init__(api_key, config)
        self.name = "TheGamesDB"

    # Implement methods later, or keep as NotImplementedError for now
    def search_game_info(self, game_title: str) -> list[dict]:
        print(f"{self.name}: Searching for game '{game_title}' (Not Implemented)")
        return []
