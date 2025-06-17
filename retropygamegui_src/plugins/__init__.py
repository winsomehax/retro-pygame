# retropygamegui_src/plugins/__init__.py
from .base_plugin import BasePlugin
from .thegamesdb_plugin import TheGamesDBPlugin
from .rawg_plugin import RAWGPlugin
from .gemini_plugin import GeminiPlugin
from .github_models_plugin import GitHubModelsPlugin
from .mock_data_plugin import MockDataPlugin

# Optional: A list of available plugin classes for easier instantiation later
AVAILABLE_PLUGIN_CLASSES = {
    "thegamesdb": TheGamesDBPlugin,
    "rawg": RAWGPlugin,
    "gemini": GeminiPlugin,
    "github_models": GitHubModelsPlugin,
    "mock": MockDataPlugin,
}

# Example: Function to get a plugin instance by name
def get_plugin_instance(plugin_name: str, api_key=None, config=None):
    plugin_class = AVAILABLE_PLUGIN_CLASSES.get(plugin_name.lower())
    if plugin_class:
        return plugin_class(api_key=api_key, config=config)
    return None

__all__ = [
    "BasePlugin",
    "TheGamesDBPlugin",
    "RAWGPlugin",
    "GeminiPlugin",
    "GitHubModelsPlugin",
    "MockDataPlugin",
    "AVAILABLE_PLUGIN_CLASSES",
    "get_plugin_instance"
]
