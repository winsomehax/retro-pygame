# RetroNode System Documentation

## Overview
RetroNode is a web application for managing retro games, platforms, and emulators. It provides a user-friendly interface for 
cataloging games, organizing them by platform, and configuring emulators for each platform. The style should be an arcade machine with
fancy 2D graphics (or pseudo-3d) making the selection of games, or platform attractive and hypermodern. Ideally it can be controlled with
a keyboard, a mouse or a console-type controller.

## System Architecture

### Tech stack
Python
Pygame


### Frontend
- **Icons**: Font Awesome
- **Fonts**: Orbitron (headings), Roboto (body text)

## Core Files


### Data Storage
- `.env`: Environment variables for API keys
- `data/games.json`: Game catalog in object format with game IDs as keys
- `data/platforms.json`: Platform definitions
- `data/emulators.json`: Emulator configurations organized by platform

### Frontend
Main games page - shows which games are currently configured
Platforms management page - allows you to add new platforms (c64, amiga etc) and edit them
Under each platform is listed the emulators for that platform, the user can add new emulators to a platform or edit existing ones

As the user is editing games, platforms or emulators, they can query TheGamesDB get a list of entries matching that title and select. they can also query RAWG.io. These two provide structured database information. Calls to these AIs and databases should be abstracted away as if they are plugins. So a plugin for Gemini, GitHub models, TheGamesDB, RAWG.io and a plugin for returning mock data for testing.

And fall back on asking Gemini or Github models for information on that title - which is unstructured.

There also needs to be a way for the user to input/edit the API Keys they have for TheGamesDB, RAWG.io, Gemini and GitHub.

## Data Models

### Game
```json
{
  "title": "Game Title",
  "description": "Game description",
  "cover_image_path": "URL to cover image",
  "platform": "<platform slug>"
}
```

### Platform
```json
{
  "platform_id": "<platform slug>",
  "name": "Platform Name",
  "manufacturer": "Manufacturer",
  "release_year": 1985,
  "description": "Platform description"
}
```

### Emulator
```json
{
  "emulator_id": "<emulator slug>",
  "name": "Emulator Name",
  "command": "emulator %ROM%",
  "description": "Emulator description",
  "website": "https://emulator-website.com"
}
```

### Search Panels

Returing the results of searches of databases and questions to AI

## Key Features

### Game Management
- Add, edit, and delete games
- Search and filter games by title or platform
- Sort games by title or platform
- Import game data from TheGamesDB or RAWG.io
- Generate game descriptions using AI (Gemini or Github models)

### Platform Management
- Add, edit, and delete platforms
- Search platforms by name or manufacturer
- Import platform data from TheGamesDB, RAWG.ioo, or other sources


### Emulator Management
- Add, edit, and delete emulators for each platform
- Configure emulator commands with ROM path placeholders
- Import emulator data from TheGamesDB, RAWG.ioo, or other sources

## Implementation Details

### Game Info Layout
- **Card Size**: Game cards should be approximately 3x larger than initially conceptualized to enhance visual impact and improve usability with controllers.
- **Game Title**:
    - Displayed below the game's cover image for better visual hierarchy.
    - Uses **Orbitron** font (as a heading).
- **Platform Name**:
    - Displayed under the game title.
    - Uses **Roboto** font.
- **Description Section**:
    - The heading "Description" (if present) uses **Orbitron** font.
    - The description text itself uses **Roboto** font.
    - Limited to 3 lines with an ellipsis (...) for overflow.
- **Text Alignment**: All text within the game card should be left-aligned for improved readability.

### Platform Info Layout
- Platform details at the top
- Emulators section with add button
- List of configured emulators with edit buttons

### Modal Design
- Consistent styling w
- Form validation for required fields
- Cancel and save buttons

### API Integration
- Error handling for failed API requests
- Loading indicators during API calls
- Fallback for missing images or data

## Required API Keys
- TheGamesDB API Key
- RAWG.io API Key
- Gemini API Key
- GitHub PAT Token
