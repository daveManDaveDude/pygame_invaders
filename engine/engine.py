import pygame
import sys
from enum import Enum, auto


class GameState(Enum):
    """Enumeration of possible game states."""
    START = auto()
    PLAYING = auto()
    GAME_OVER = auto()

class Engine:
    """Core game engine handling loop and state transitions."""

    def __init__(self, width, height, fps, scene_classes, initial_state):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        pygame.display.set_caption("Space Invaders – Pygame Basics")
        self.fps = fps
        # instantiate scenes
        self.scenes = {state: cls(self) for state, cls in scene_classes.items()}
        self.state = initial_state
        self.current_scene = self.scenes[self.state]

    def change_state(self, new_state):
        """Switch to a new scene state, calling exit/enter hooks."""
        # call on_exit of current scene if available
        exit_hook = getattr(self.current_scene, 'on_exit', None)
        if callable(exit_hook):
            self.current_scene.on_exit()
        # switch
        self.state = new_state
        self.current_scene = self.scenes[new_state]
        # call on_enter of new scene if available
        enter_hook = getattr(self.current_scene, 'on_enter', None)
        if callable(enter_hook):
            self.current_scene.on_enter()

    def run(self):
        """Main loop: handle events, update, draw."""
        while True:
            dt_ms = self.clock.tick(self.fps)
            dt = dt_ms / 1000.0
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.current_scene.handle_events(events)
            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)
            pygame.display.flip()