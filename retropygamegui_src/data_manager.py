import json
import os
import dataclasses
from typing import Dict, List, TypeVar, Type, Optional, overload, Literal
from .models import Game, Platform, Emulator

T = TypeVar('T')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
GAMES_FILE = os.path.join(DATA_DIR, "games.json")
PLATFORMS_FILE = os.path.join(DATA_DIR, "platforms.json")
EMULATORS_FILE = os.path.join(DATA_DIR, "emulators.json")

# Overload for when is_dict_of_items is True (default)
@overload
def _load_json_data(file_path: str, data_type: Type[T], is_dict_of_items: Literal[True] = True) -> Dict[str, T]: ...

# Overload for when is_dict_of_items is False
@overload
def _load_json_data(file_path: str, data_type: Type[T], is_dict_of_items: Literal[False]) -> List[T]: ...

# Actual implementation
def _load_json_data(file_path: str, data_type: Type[T], is_dict_of_items: bool = True) -> Dict[str, T] | List[T]:
    """Helper to load JSON data and convert to specified model type."""
    loaded_data: Dict[str, T] = {} # Initialized for the dict case

    if not os.path.exists(file_path):
        return {} if is_dict_of_items else []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        if is_dict_of_items:
            if not isinstance(raw_data, dict):
                print(f"Warning: Expected a dictionary in {file_path}, got {type(raw_data)}. Returning empty dict.")
                return {}
            
            dataclass_fields_info = dataclasses.fields(data_type) # type: ignore
            # Expected keyword argument names are all field names EXCEPT the first one
            # (convention: first field is the ID, passed positionally as 'key')
            expected_kwarg_names = {f.name for f in dataclass_fields_info[1:]} if len(dataclass_fields_info) > 1 else set()

            # Process if raw_data is a dictionary
            for key, original_json_item_dict in raw_data.items():
                if not isinstance(original_json_item_dict, dict):
                    print(f"Warning: Expected a dictionary for key '{key}' in {file_path}, got {type(original_json_item_dict)}. Skipping.")
                    continue
                
                # Filter the JSON item dictionary to only include keys that are expected as keyword arguments
                # by the dataclass constructor (i.e., fields other than the ID field).
                constructor_kwargs = {
                    k: v for k, v in original_json_item_dict.items() if k in expected_kwarg_names
                }

                try:
                    # 'key' is the ID (first positional argument to constructor)
                    # 'constructor_kwargs' are the subsequent keyword arguments
                    instance = data_type(key, **constructor_kwargs) # type: ignore
                    loaded_data[key] = instance
                except TypeError as e:
                    # This can catch missing required arguments (if not in constructor_kwargs)
                    # or type mismatches for field values.
                    print(f"Error instantiating {data_type.__name__} for key '{key}'. "
                          f"Attempted with ID='{key}' and kwargs={constructor_kwargs} (derived from JSON: {original_json_item_dict}). "
                          f"Error: {e}. Skipping this item.")
                    continue # Continue to the next item instead of returning
            return loaded_data
        else: # is_dict_of_items is False
            if not isinstance(raw_data, list):
                print(f"Warning: Expected a list in {file_path}, got {type(raw_data)}. Returning empty list.")
                return []

            loaded_data_list: List[T] = []
            # Process if raw_data is a list
            for item_dict in raw_data:
                if not isinstance(item_dict, dict):
                    print(f"Warning: Expected a dictionary for item in list in {file_path}, got {type(item_dict)}. Skipping.")
                    continue
                try:
                    # Pylance may issue a false positive here with unconstrained Type[T](**kwargs)
                    loaded_data_list.append(data_type(**item_dict)) # type: ignore
                except TypeError as e:
                    print(f"Error instantiating {data_type.__name__} with data {item_dict} in {file_path}: {e}")
                    # Optionally, decide how to handle this error, e.g., skip item or return partial list
            return loaded_data_list
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        # Return an empty structure of the appropriate type based on is_dict_of_items
        return {} if is_dict_of_items else []

def _save_json_data(file_path: str, data: Dict[str, T] | List[T], is_dict_of_items: bool = True):
    """Helper to save data to JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            if is_dict_of_items and isinstance(data, dict):
                # Convert model instances back to dicts for JSON serialization
                # Exclude the 'id' field if it was the key.
                serializable_data = {
                    key: {k: v for k, v in value.__dict__.items() if k != 'id' and k != value.__annotations__.get('id_field', list(value.__annotations__.keys())[0])}
                    for key, value in data.items()
                }
                json.dump(serializable_data, f, indent=2)
            elif not is_dict_of_items and isinstance(data, list):
                json.dump([item.__dict__ for item in data], f, indent=2)
            else:
                 json.dump(data, f, indent=2) # Fallback for simple structures

    except IOError as e:
        print(f"Error saving {file_path}: {e}")

class DataManager:
    def __init__(self):
        self.games: Dict[str, Game] = _load_json_data(GAMES_FILE, Game, is_dict_of_items=True) or {}
        self.platforms: Dict[str, Platform] = _load_json_data(PLATFORMS_FILE, Platform, is_dict_of_items=True) or {}
        self.emulators: Dict[str, Emulator] = _load_json_data(EMULATORS_FILE, Emulator, is_dict_of_items=True) or {}
        # Adjusting models.py to ensure dataclasses can be initialized with their ID field from the dict key.
        # For Game, the key is game_id, for Platform platform_id, for Emulator emulator_id.
        # The _load_json_data function needs to map the dict key to the correct ID field in the dataclass.
        # For simplicity, I'll assume the first field in the dataclass is its ID field if not 'id'.
        # This is a bit fragile; a more robust solution would involve explicit mapping or a convention.
        # For now, I've updated Game to have 'id'. Platform has 'platform_id', Emulator has 'emulator_id'.
        # The _load_json_data logic was simplified to assume the key is passed as the first arg or 'id'.

    def save_all_data(self):
        _save_json_data(GAMES_FILE, self.games, is_dict_of_items=True)
        _save_json_data(PLATFORMS_FILE, self.platforms, is_dict_of_items=True)
        _save_json_data(EMULATORS_FILE, self.emulators, is_dict_of_items=True)