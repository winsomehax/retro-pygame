from .base_plugin import BasePlugin

class MockDataPlugin(BasePlugin):
    def __init__(self, api_key=None, config=None):
        super().__init__(api_key, config)
        self.name = "Mock Data"
        self.mock_games = {
            "Super Mock Game": [
                {'title': 'Super Mock Game', 'source_game_id': 'mock_smg1', 'platform_name': 'Mock Console', 'description': 'A fun mock game.'}
            ],
            "Another Mock Game": [
                {'title': 'Another Mock Game', 'source_game_id': 'mock_amg1', 'platform_name': 'Mock System X', 'description': 'The sequel.'}
            ]
        }
        self.mock_platforms = {
           "Mock Console": [{'name': 'Mock Console', 'source_platform_id': 'mock_mc1', 'manufacturer': 'Mock Corp', 'release_year': 2024}]
        }


    def search_game_info(self, game_title: str) -> list[dict]:
        print(f"{self.name}: Searching for game '{game_title}'")
        return self.mock_games.get(game_title, [])

    def search_platform_info(self, platform_name: str) -> list[dict]:
        print(f"{self.name}: Searching for platform '{platform_name}'")
        return self.mock_platforms.get(platform_name, [])

    def get_game_details(self, source_game_id: str) -> dict | None:
        for games in self.mock_games.values():
            for game in games:
                if game['source_game_id'] == source_game_id:
                    return game
        return None

    def get_platform_details(self, source_platform_id: str) -> dict | None:
       for platforms in self.mock_platforms.values():
            for platform in platforms:
                if platform['source_platform_id'] == source_platform_id:
                    return platform
       return None

    def generate_game_description_ai(self, game_title: str, existing_description: str = None) -> str | None:
        return f"This is a mock AI generated description for '{game_title}'. Original: {existing_description if existing_description else 'N/A'}"
