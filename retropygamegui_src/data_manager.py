import json
import os
import errno # Added for OSError check
from .models import Game, Platform, Emulator

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # Ensure data_dir exists at initialization
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
            except OSError as e: # Guard against race condition
                if e.errno != errno.EEXIST:
                    raise

        self.games_file = os.path.join(data_dir, "games.json")
        self.platforms_file = os.path.join(data_dir, "platforms.json")
        self.emulators_file = os.path.join(data_dir, "emulators.json")

        self.games = {}
        self.platforms = {}
        self.emulators = {} # Stored as {platform_id: {emulator_id: Emulator}}

        self._load_all_data()

    def _load_json_file(self, file_path, default_data=None):
        if default_data is None:
            default_data = {}
        # data_dir is created in __init__ or _save_json_file, so no need to check here
        if not os.path.exists(file_path):
            # Create the file with default data if it doesn't exist
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=4)
            return default_data
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return default_data

    def _save_json_file(self, file_path, data):
        try:
            # Ensure data_dir exists before saving (it should, but as a safeguard)
            if not os.path.exists(self.data_dir):
                try:
                    os.makedirs(self.data_dir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError:
            print(f"Error: Could not save data to {file_path}")

    def _load_all_data(self):
        games_data = self._load_json_file(self.games_file, default_data={})
        for game_id, game_dict in games_data.items():
            self.games[game_id] = Game.from_dict(game_dict)

        platforms_data = self._load_json_file(self.platforms_file, default_data={})
        for platform_id, platform_dict in platforms_data.items():
            self.platforms[platform_id] = Platform.from_dict(platform_dict)

        emulators_data = self._load_json_file(self.emulators_file, default_data={})
        for platform_id, emus in emulators_data.items():
            self.emulators.setdefault(platform_id, {})
            for emulator_id, emu_dict in emus.items():
                self.emulators[platform_id][emulator_id] = Emulator.from_dict(emu_dict)

    def _save_games(self):
        data_to_save = {game_id: game.to_dict() for game_id, game in self.games.items()}
        self._save_json_file(self.games_file, data_to_save)

    def _save_platforms(self):
        data_to_save = {platform_id: platform.to_dict() for platform_id, platform in self.platforms.items()}
        self._save_json_file(self.platforms_file, data_to_save)

    def _save_emulators(self):
        data_to_save = {}
        for platform_id, emus in self.emulators.items():
            data_to_save[platform_id] = {emu_id: emu.to_dict() for emu_id, emu in emus.items()}
        self._save_json_file(self.emulators_file, data_to_save)

    # Game Methods
    def get_all_games(self):
        return list(self.games.values())

    def get_game(self, game_id):
        return self.games.get(game_id)

    def add_game(self, game_id, game: Game):
        if game_id in self.games:
            raise ValueError(f"Game with ID {game_id} already exists.")
        self.games[game_id] = game
        self._save_games()

    def update_game(self, game_id, game: Game):
        if game_id not in self.games:
            raise ValueError(f"Game with ID {game_id} not found.")
        self.games[game_id] = game
        self._save_games()

    def delete_game(self, game_id):
        if game_id in self.games:
            del self.games[game_id]
            self._save_games()
            return True
        return False

    # Platform Methods
    def get_all_platforms(self):
        return list(self.platforms.values())

    def get_platform(self, platform_id):
        return self.platforms.get(platform_id)

    def add_platform(self, platform: Platform):
        if platform.platform_id in self.platforms:
            raise ValueError(f"Platform with ID {platform.platform_id} already exists.")
        self.platforms[platform.platform_id] = platform
        self._save_platforms()
        # Ensure there's an entry for this platform in emulators
        self.emulators.setdefault(platform.platform_id, {})
        self._save_emulators() # Save emulators in case a new platform key was added


    def update_platform(self, platform_id, platform: Platform):
        if platform_id not in self.platforms:
            raise ValueError(f"Platform with ID {platform_id} not found.")
        self.platforms[platform_id] = platform
        self._save_platforms()

    def delete_platform(self, platform_id):
        if platform_id in self.platforms:
            del self.platforms[platform_id]
            self._save_platforms()
            # Also delete associated emulators
            if platform_id in self.emulators:
                del self.emulators[platform_id]
                self._save_emulators()
            return True
        return False

    # Emulator Methods
    def get_emulators_for_platform(self, platform_id):
        return list(self.emulators.get(platform_id, {}).values())

    def get_emulator(self, platform_id, emulator_id):
        return self.emulators.get(platform_id, {}).get(emulator_id)

    def add_emulator_to_platform(self, platform_id, emulator: Emulator):
        if platform_id not in self.platforms:
            raise ValueError(f"Platform with ID {platform_id} not found. Cannot add emulator.")
        # Ensure platform specific emulator dict exists
        self.emulators.setdefault(platform_id, {})

        if emulator.emulator_id in self.emulators[platform_id]:
            raise ValueError(f"Emulator with ID {emulator.emulator_id} already exists for platform {platform_id}.")

        self.emulators[platform_id][emulator.emulator_id] = emulator
        self._save_emulators()

    def update_emulator_on_platform(self, platform_id, emulator_id, emulator: Emulator):
        if platform_id not in self.emulators or emulator_id not in self.emulators[platform_id]:
            raise ValueError(f"Emulator with ID {emulator_id} not found for platform {platform_id}.")
        self.emulators[platform_id][emulator_id] = emulator
        self._save_emulators()

    def delete_emulator_from_platform(self, platform_id, emulator_id):
        if platform_id in self.emulators and emulator_id in self.emulators[platform_id]:
            del self.emulators[platform_id][emulator_id]
            self._save_emulators()
            return True
        return False

if __name__ == '__main__':
    # data_dir is created by DataManager constructor if it doesn't exist.
    # No need for explicit os.makedirs("data") here unless running sections of this for standalone test
    # before DataManager instantiation. For this script, it's fine.

    print("Initializing DataManager...")
    data_manager = DataManager(data_dir="data")
    print("DataManager initialized.")

    # Test Platform operations
    print("\n--- Testing Platforms ---")
    try:
        new_platform = Platform(platform_id="snes", name="Super Nintendo", manufacturer="Nintendo", release_year=1990, description="A 16-bit classic.")
        data_manager.add_platform(new_platform)
        print(f"Added platform: {new_platform.name}")
    except ValueError as e:
        print(e)

    retrieved_platform = data_manager.get_platform("snes")
    if retrieved_platform:
        print(f"Retrieved platform: {retrieved_platform.name}")
        retrieved_platform.description = "A 16-bit home video game console."
        data_manager.update_platform("snes", retrieved_platform)
        print(f"Updated platform description: {data_manager.get_platform('snes').description}")

    # Test Emulator operations
    print("\n--- Testing Emulators ---")
    if retrieved_platform:
        try:
            new_emulator = Emulator(emulator_id="snes9x", name="Snes9x", command="snes9x %ROM%", description="A popular SNES emulator.", website="http://www.snes9x.com/")
            data_manager.add_emulator_to_platform("snes", new_emulator)
            print(f"Added emulator {new_emulator.name} to {retrieved_platform.name}")
        except ValueError as e:
            print(e)

        snes_emulators = data_manager.get_emulators_for_platform("snes")
        print(f"Emulators for SNES: {[emu.name for emu in snes_emulators]}")

        if snes_emulators:
            snes_emulators[0].command = "snes9x -fullscreen %ROM%"
            data_manager.update_emulator_on_platform("snes", snes_emulators[0].emulator_id, snes_emulators[0])
            print(f"Updated command for {snes_emulators[0].name}: {data_manager.get_emulator('snes', snes_emulators[0].emulator_id).command}")

    # Test Game operations
    print("\n--- Testing Games ---")
    try:
        game_id_zelda = "zelda_link_to_the_past"
        new_game = Game(title="The Legend of Zelda: A Link to the Past", description="Action-adventure game.", cover_image_path="path/to/zelda.png", platform_slug="snes")
        data_manager.add_game(game_id_zelda, new_game)
        print(f"Added game: {new_game.title}")
    except ValueError as e:
        print(e)

    retrieved_game = data_manager.get_game(game_id_zelda)
    if retrieved_game:
        print(f"Retrieved game: {retrieved_game.title}")
        retrieved_game.description = "An epic action-adventure game for the SNES."
        data_manager.update_game(game_id_zelda, retrieved_game)
        print(f"Updated game description: {data_manager.get_game(game_id_zelda).description}")

    all_games = data_manager.get_all_games()
    print(f"All games: {[game.title for game in all_games]}")

    print("\n--- Current Data (after operations) ---")
    print("Games:", {gid: g.to_dict() for gid, g in data_manager.games.items()})
    print("Platforms:", {pid: p.to_dict() for pid, p in data_manager.platforms.items()})
    print("Emulators:", {pid: {eid: e.to_dict() for eid, e in emus.items()} for pid, emus in data_manager.emulators.items()})

    print("\nRun this script directly to test DataManager functionality.")
    print("It will create/update games.json, platforms.json, and emulators.json in the 'data' subdirectory.")
