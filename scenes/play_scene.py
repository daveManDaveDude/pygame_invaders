import pygame
from config import LIVES, ENEMY_SPEED_INIT
from sprites import Player, Enemy
from engine.engine import Engine, GameState
from systems.movement_system import update_entities
from systems.collision_system import handle_collisions
from systems.rendering_system import render_play

class PlayScene:
    """Main gameplay scene: player, enemies, bullets, and game logic."""
    STATE = GameState.PLAYING

    def __init__(self, engine):
        self.engine = engine
        self.font = engine.font
        self.reset()

    def on_enter(self):
        pass

    def reset(self):
        """Initialize or reset gameplay state."""
        self.player = Player()
        self.players = pygame.sprite.GroupSingle(self.player)
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemy_direction = 1
        self.enemy_speed = ENEMY_SPEED_INIT
        self.score = 0
        self.game_over = False
        self.lives = LIVES
        self.hit = False
        self.final_death = False
        self.hit_start = 0
        self.hit_duration = 1000
        self.death_pos = None
        self._create_enemies()

    def _create_enemies(self):
        from config import ROWS, COLS, ENEMY_MARGIN_X, ENEMY_MARGIN_Y, ENEMY_SPACING_X, ENEMY_SPACING_Y
        for row in range(ROWS):
            for col in range(COLS):
                x = ENEMY_MARGIN_X + col * ENEMY_SPACING_X
                y = ENEMY_MARGIN_Y + row * ENEMY_SPACING_Y
                self.enemies.add(Enemy((x, y)))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.hit:
                now = pygame.time.get_ticks()
                self.player.shoot(now, self.bullets)

    def update(self, dt):
        now = pygame.time.get_ticks()
        # handle invulnerability timing
        if self.hit and now - self.hit_start >= self.hit_duration:
            if self.final_death:
                self.hit = False
                self.final_death = False
                self.game_over = True
            else:
                self.hit = False
                self.player.rect.midbottom = self.death_pos
                self.player.last_shot = now
        # if game over, switch state
        if self.game_over:
            self.engine.change_state(GameState.GAME_OVER)
            return
        # movement and firing
        update_entities(self, dt)
        # collisions and score
        handle_collisions(self)
        # after collisions, check game over or win
        if self.game_over:
            self.engine.change_state(GameState.GAME_OVER)

    def lose_life(self, now):
        """Handle player being hit: lives decrement and invulnerability or final death."""
        self.lives -= 1
        # common cleanup
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.hit = True
        self.hit_start = now
        self.death_pos = self.player.rect.midbottom
        self.player.last_shot = now
        # determine if final death
        if self.lives <= 0:
            self.final_death = True

    def draw(self, screen):
        render_play(self, screen)