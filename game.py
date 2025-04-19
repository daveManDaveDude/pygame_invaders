import pygame
import config
from engine.engine import Engine, GameState
from scenes.start_scene import StartScene
from scenes.play_scene import PlayScene
from scenes.game_over_scene import GameOverScene

def main():
    """Entry point: set up engine and run game."""
    scene_classes = {
        GameState.START: StartScene,
        GameState.PLAYING: PlayScene,
        GameState.GAME_OVER: GameOverScene,
    }
    engine = Engine(config.WIDTH, config.HEIGHT, config.FPS, scene_classes, GameState.START)
    engine.run()

if __name__ == "__main__":
    main()