# retropygamegui_src/config.py
import os
from dotenv import load_dotenv, set_key, find_dotenv

class Config:
    def __init__(self, env_path=None):
        """
        Initializes the config, loading from the specified .env file path.
        If no path is provided, it will try to find .env or create it in the project root.
        """
        self.env_path = env_path
        if self.env_path is None:
            # Try to find .env in project root or one level up if script is in src
            project_root_env = find_dotenv(usecwd=True, raise_error_if_not_found=False) # Check current dir (if running from root)
            if not project_root_env:
                 # Assuming this script is in retropygamegui_src, project root is parent
                 current_dir = os.path.dirname(os.path.abspath(__file__))
                 project_root = os.path.dirname(current_dir)
                 project_root_env = os.path.join(project_root, ".env")

            self.env_path = project_root_env if project_root_env and os.path.exists(project_root_env) else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")


        if not os.path.exists(self.env_path):
            # Create .env file if it doesn't exist
            try:
                with open(self.env_path, 'w') as f:
                    f.write("# API Keys for RetroPyGameGUI\n")
                print(f".env file created at {self.env_path}")
            except IOError as e:
                print(f"Error creating .env file at {self.env_path}: {e}")
                # Fallback to a path that might be writable in a restricted env
                self.env_path = os.path.join(os.getcwd(), ".env_fallback")
                try:
                    with open(self.env_path, 'w') as f:
                        f.write("# API Keys for RetroPyGameGUI\n")
                    print(f"Fallback .env file created at {self.env_path}")
                except IOError as fallback_e:
                    print(f"Error creating fallback .env file: {fallback_e}. API key saving may fail.")


        load_dotenv(dotenv_path=self.env_path)

        self.api_keys_map = {
            "thegamesdb": "THEGAMESDB_API_KEY",
            "rawg": "RAWG_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "github": "GITHUB_PAT_TOKEN"
        }
        self.api_keys = self._load_api_keys()
        # print(f"Config initialized. Loaded keys from: {self.env_path}") # Debug
        # print(f"Loaded API keys: {self.api_keys}") # Debug

    def _load_api_keys(self):
        keys = {}
        for key_name, env_var in self.api_keys_map.items():
            keys[key_name] = os.getenv(env_var)
        return keys

    def get_api_key(self, service_name: str) -> str | None:
        """Gets an API key for a given service name (e.g., 'thegamesdb')."""
        return self.api_keys.get(service_name.lower())

    def get_all_api_keys(self) -> dict:
        """Returns all currently loaded API keys."""
        # Reload from .env to ensure fresh values before display
        load_dotenv(dotenv_path=self.env_path, override=True)
        return self._load_api_keys()


    def save_api_key(self, service_name: str, api_key_value: str) -> bool:
        """Saves a single API key to the .env file and updates the in-memory cache."""
        service_name_lower = service_name.lower()
        if service_name_lower in self.api_keys_map:
            env_var_name = self.api_keys_map[service_name_lower]
            try:
                set_key(self.env_path, env_var_name, api_key_value)
                self.api_keys[service_name_lower] = api_key_value # Update cache
                # print(f"Saved {env_var_name} = {api_key_value} to {self.env_path}") # Debug
                return True
            except Exception as e:
                print(f"Error saving key {env_var_name} to {self.env_path}: {e}")
                return False
        return False

    def save_all_api_keys(self, keys_to_save: dict) -> bool:
        """Saves multiple API keys. keys_to_save is a dict like {'thegamesdb': 'value', ...}."""
        all_saved = True
        for service_name, key_value in keys_to_save.items():
            if not self.save_api_key(service_name, key_value if key_value is not None else ""): # Save empty string if None
                all_saved = False
        # print(f"Finished save_all_api_keys. Result: {all_saved}") # Debug
        return all_saved

# Global instance
app_config = Config()
