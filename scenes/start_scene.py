import pygame
import sys
from engine.engine import Engine, GameState
from systems.rendering_system import render_start

class StartScene:
    """Start screen: shows title and instructions."""
    STATE = GameState.START

    def __init__(self, engine):
        self.engine = engine
        self.font = engine.font

    def on_enter(self):
        pass

    def handle_events(self, events):
        for event in events:
            # start game on SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # reset play scene before starting
                play_scene = self.engine.scenes[GameState.PLAYING]
                if hasattr(play_scene, 'reset'):
                    play_scene.reset()
                self.engine.change_state(GameState.PLAYING)
            # quit application on Q
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        pass

    def draw(self, screen):
        render_start(self, screen)