# Space Invaders (Pygame)

A simple Space Invaders clone built with Python and Pygame.

## Features
 - Classic Space Invaders gameplay: control a ship, shoot descending aliens.
 - Enemy dive attacks and randomized sprite visuals.
 - Animated explosions and basic scoring system.
 - Pause, invulnerability cheat, and level progression.

## Requirements
 - Python 3.6 or higher
 - Pygame library

## Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```
2. Install dependencies:
   ```bash
   pip install pygame
   ```

## Usage
Run the game with:
```bash
python game.py
```

## Controls
 - Left / Right Arrows: Move the player ship
 - Space: Shoot
 - P: Pause / Unpause
 - Q: Quit to main menu
 - L: Toggle invulnerability (cheat)
 - D: Force an enemy dive (debug)

## Configuration
Game parameters (screen size, speeds, colors, etc.) are defined in `config.json`. You can tweak values to adjust difficulty or appearance.

## Assets
- `spritesheet.png`: Sprite sheet for player, enemies, and lasers
- `explosion_sheet.png`: Frames for explosion animations

## License
This project is released under the MIT License.