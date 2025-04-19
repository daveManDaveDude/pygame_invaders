import pygame
from engine.engine import Engine, GameState
from systems.rendering_system import render_game_over

class GameOverScene:
    """Game over screen: win/lose display and return to menu."""
    STATE = GameState.GAME_OVER

    def __init__(self, engine):
        self.engine = engine
        self.font = engine.font

    def on_enter(self):
        """Called when entering game over: determine win/loss based on play scene state."""
        # Inspect PlayScene to see if any enemies remain
        play_scene = self.engine.scenes[GameState.PLAYING]
        # Win if no enemies left
        try:
            remaining = len(play_scene.enemies)
        except Exception:
            remaining = 0
        self.win = (remaining == 0)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.engine.change_state(GameState.START)

    def update(self, dt):
        pass

    def draw(self, screen):
        render_game_over(self, screen)