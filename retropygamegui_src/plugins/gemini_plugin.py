from .base_plugin import BasePlugin

class GeminiPlugin(BasePlugin):
    def __init__(self, api_key=None, config=None):
        super().__init__(api_key, config)
        self.name = "Gemini"

    def generate_game_description_ai(self, game_title: str, existing_description: str = None) -> str | None:
        print(f"{self.name}: Generating description for '{game_title}' (Not Implemented)")
        return f"AI generated description for {game_title} from {self.name}." # Example mock
