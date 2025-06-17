import json

class Game:
    def __init__(self, title, description, cover_image_path, platform_slug):
        self.title = title
        self.description = description
        self.cover_image_path = cover_image_path
        self.platform_slug = platform_slug

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "cover_image_path": self.cover_image_path,
            "platform": self.platform_slug
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            cover_image_path=data.get("cover_image_path"),
            platform_slug=data.get("platform")
        )

class Platform:
    def __init__(self, platform_id, name, manufacturer, release_year, description):
        self.platform_id = platform_id
        self.name = name
        self.manufacturer = manufacturer
        self.release_year = release_year
        self.description = description

    def to_dict(self):
        return {
            "platform_id": self.platform_id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "release_year": self.release_year,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            platform_id=data.get("platform_id"),
            name=data.get("name"),
            manufacturer=data.get("manufacturer"),
            release_year=data.get("release_year"),
            description=data.get("description")
        )

class Emulator:
    def __init__(self, emulator_id, name, command, description, website):
        self.emulator_id = emulator_id
        self.name = name
        self.command = command
        self.description = description
        self.website = website

    def to_dict(self):
        return {
            "emulator_id": self.emulator_id,
            "name": self.name,
            "command": self.command,
            "description": self.description,
            "website": self.website
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            emulator_id=data.get("emulator_id"),
            name=data.get("name"),
            command=data.get("command"),
            description=data.get("description"),
            website=data.get("website")
        )

if __name__ == '__main__':
    # Example Usage (optional - for testing purposes)
    game_data = {
        "title": "Super Game",
        "description": "An awesome retro game.",
        "cover_image_path": "path/to/image.png",
        "platform": "console-x"
    }
    game = Game.from_dict(game_data)
    print(f"Game: {game.title}, Platform: {game.platform_slug}")
    print(f"Game Dict: {game.to_dict()}")

    platform_data = {
        "platform_id": "console-x",
        "name": "Console X",
        "manufacturer": "Retro Corp",
        "release_year": 1990,
        "description": "A popular gaming console."
    }
    platform = Platform.from_dict(platform_data)
    print(f"Platform: {platform.name}, Manufacturer: {platform.manufacturer}")
    print(f"Platform Dict: {platform.to_dict()}")

    emulator_data = {
        "emulator_id": "emu-x",
        "name": "EmulatorX",
        "command": "emux %ROM%",
        "description": "The best emulator for Console X.",
        "website": "http://emux.example.com"
    }
    emulator = Emulator.from_dict(emulator_data)
    print(f"Emulator: {emulator.name}, Command: {emulator.command}")
    print(f"Emulator Dict: {emulator.to_dict()}")
