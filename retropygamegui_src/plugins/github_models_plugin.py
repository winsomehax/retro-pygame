from .base_plugin import BasePlugin

class GitHubModelsPlugin(BasePlugin): # Or a more generic name like AIModelsPlugin
    def __init__(self, api_key=None, config=None): # API key might be a PAT
        super().__init__(api_key, config)
        self.name = "GitHub Models"

    def generate_game_description_ai(self, game_title: str, existing_description: str = None) -> str | None:
        print(f"{self.name}: Generating description for '{game_title}' (Not Implemented)")
        return f"AI generated description for {game_title} from {self.name}." # Example mock
