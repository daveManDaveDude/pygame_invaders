# Pygame Invaders

The entire project apart from this line and a couple of edits below are AI generated using codex cli.

*A modern, fully‑configurable Space Invaders clone written in ****Python 3**** and ****Pygame***.

---

## 🚀 Gameplay at a Glance

- Pilot your star‑fighter across the bottom of the screen and blast waves of descending invaders.
- Each level gets faster; invaders occasionally peel off the pack and **dive‑bomb** your ship.
- You have **3 lives** by default—lose them all and it’s game over.

## ✨ Why This Project Is Interesting   <<< Its not LOL

This repo is a test, I asked o3 to give me a basic space invaders in python using pygame. I then worked with Openai's codex client to create the demo game.

## 🔑 Features

- **Scene system** with *Start Menu*, *Playing*, and *Game‑Over* scenes, orchestrated by a minimal `Engine` class ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/engine/engine.py))
- **Config‑first design** – tweak difficulty, colours, speeds, window size, and more in `config.json` without touching code ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/config.json))
- **Procedural dive attacks** – the bottom‑most invader in a column may detach and swoop toward the player when there’s enough vertical clearance ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/scenes/play_scene.py))
- **Cheats & debug tools** — press **L** for invulnerability or **D** to force a dive, handy when testing new waves ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/scenes/play_scene.py))
- **Smooth 60 FPS update loop**, delta‑time aware movement, and simple ECS‑style separation of *systems* and *sprites*.
- **Animated explosions** and sprite‑sheet based graphics prepared at runtime ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/sprites.py))

## 🎮 Controls

| Key       | Action                                                                                                                           |
| --------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **← / →** | Move ship horizontally ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/sprites.py))                   |
| **Space** | Shoot laser                                                                                                                      |
| **P**     | Pause / unpause                                                                                                                  |
| **Q**     | Quit to main menu                                                                                                                |
| **L**     | Toggle invulnerability (cheat) ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/scenes/play_scene.py)) |
| **D**     | Force enemy dive (debug) ([github.com](https://github.com/daveManDaveDude/pygame_invaders/blob/main/scenes/play_scene.py))       |

## 🛠️ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/daveManDaveDude/pygame_invaders.git
   cd pygame_invaders
   ```
2. **Create a virtual environment** *(optional but recommended)*
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install pygame>=2.5
   ```
4. **Run the game**
   ```bash
   python game.py
   ```

## ⚙️ Configuration

All tunable parameters live in `` — screen size, player & enemy speeds, dive amplitude, colour palette, and more. Edit the file and restart the game to see changes instantly.

## 🗂️ Project Layout

```text
├─ assets/               # Raw sprite‑sheet(s) & sounds (add your own!)
├─ engine/               # Core engine loop and helpers
├─ scenes/               # Start, Play, GameOver scene classes
├─ systems/              # Collision detection, rendering helpers
├─ sprites.py            # Entity classes & sprite‑sheet utilities
├─ config.json           # Game settings (no code changes required)
└─ game.py               # Entry point – bootstrap Engine
```

## 🧭 Roadmap / Ideas

- Sound effects & background music
- High‑score persistence (JSON or SQLite)
- Power‑ups & different enemy types
- Mobile / touch controls via Pygbag export

*Pull requests are very welcome!* Feel free to open an issue to discuss features.

## 📄 License

Released under the **MIT License** – see [`LICENSE`](LICENSE) for details.

## 🙏 Credits

Sprites created by openai o3; explosion sheet created by o3.\
Project authored by codex cli and guided by **@daveManDaveDude**.

