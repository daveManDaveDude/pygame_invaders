import pygame
import random
from config import LIVES, ENEMY_SPEED_INIT, HEIGHT, DIVE_SPEED, DIVE_MIN_X_SEP, DIVE_MAX_X_SEP, ENEMY_DROP
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
        # paused state
        self.paused = False
        self.hit = False
        self.final_death = False
        self.hit_start = 0
        self.hit_duration = 1000
        self.death_pos = None
        self._create_enemies()
        # attacker dive state
        self.attacker = None
        now = pygame.time.get_ticks()
        # schedule the first attack (5–10 seconds)
        self.next_attack_at = now + random.randint(5000, 10000)
        self.attacker_original_pos = None
        # invulnerability toggle (cheat): if True, player cannot lose lives from shots
        self.invulnerable = False

    def _create_enemies(self):
        from config import ROWS, COLS, ENEMY_MARGIN_X, ENEMY_MARGIN_Y, ENEMY_SPACING_X, ENEMY_SPACING_Y
        for row in range(ROWS):
            for col in range(COLS):
                x = ENEMY_MARGIN_X + col * ENEMY_SPACING_X
                y = ENEMY_MARGIN_Y + row * ENEMY_SPACING_Y
                enemy = Enemy((x, y))
                # tag with grid coordinates for respawn positioning
                enemy.grid_pos = (row, col)
                self.enemies.add(enemy)
    
    def spawn_attacker(self):
        """Detach a random invader from the pack to begin a dive attack."""
        # only one attacker at a time
        if self.attacker is not None or not self.enemies:
            return
        # prevent diving when pack is too close to player vertically
        player_y = self.player.rect.top
        pack_bottom = max(e.rect.bottom for e in self.enemies)
        if player_y - pack_bottom <= ENEMY_DROP * 3:
            return
        # pick a random enemy that has no invaders below it in its column to attack
        # group enemies by grid column and select the bottom-most in each column
        if not self.enemies:
            return
        bottom_by_col = {}
        for e in self.enemies:
            r, c = e.grid_pos
            # choose the enemy with the largest grid row (farthest down) per column
            if c not in bottom_by_col or r > bottom_by_col[c].grid_pos[0]:
                bottom_by_col[c] = e
        # apply horizontal‑range filtering based on vertical separation
        player_x = self.player.rect.centerx
        player_y = self.player.rect.top
        candidates = list(bottom_by_col.values())
        # distance filter: allow only invaders within an adaptive X window
        filtered = []
        for e in candidates:
            y_sep = player_y - e.rect.y
            f = max(0.0, min(1.0, y_sep / HEIGHT))
            max_dx = DIVE_MIN_X_SEP + f * (DIVE_MAX_X_SEP - DIVE_MIN_X_SEP)
            if abs(e.rect.centerx - player_x) <= max_dx:
                filtered.append(e)
        if filtered:
            candidates = filtered
        # randomize side of attack: prefer spawning left or right of player
        side = random.choice([-1, 1])
        side_candidates = [e for e in candidates if (e.rect.centerx - player_x) * side >= 0]
        if side_candidates:
            candidates = side_candidates
        attacker = random.choice(candidates)
        # determine vertical clearance target (pack bottom including this attacker)
        pack_bottom = max(e.rect.bottom for e in self.enemies)
        attacker.clearance_target = pack_bottom
        attacker.state = 'clearance'
        # remove from pack and set as current attacker
        self.enemies.remove(attacker)
        self.attacker = attacker

    def on_attacker_finished(self, missed):
        """Handle end of a dive attack: respawn if missed, schedule next attack."""
        now = pygame.time.get_ticks()
        # if missed, put attacker back into pack at its grid position with current pack offset
        if missed and self.attacker:
            # compute current pack offset
            dx = dy = 0
            if self.enemies:
                # any remaining enemy shares pack offset
                sample = next(iter(self.enemies))
                r0, c0 = sample.grid_pos
                from config import ENEMY_MARGIN_X, ENEMY_MARGIN_Y, ENEMY_SPACING_X, ENEMY_SPACING_Y
                init_x0 = ENEMY_MARGIN_X + c0 * ENEMY_SPACING_X
                init_y0 = ENEMY_MARGIN_Y + r0 * ENEMY_SPACING_Y
                dx = sample.rect.x - init_x0
                dy = sample.rect.y - init_y0
            # compute respawn position based on grid
            row, col = self.attacker.grid_pos
            from config import ENEMY_MARGIN_X, ENEMY_MARGIN_Y, ENEMY_SPACING_X, ENEMY_SPACING_Y
            init_x = ENEMY_MARGIN_X + col * ENEMY_SPACING_X
            init_y = ENEMY_MARGIN_Y + row * ENEMY_SPACING_Y
            self.attacker.rect.topleft = (init_x + dx, init_y + dy)
            self.enemies.add(self.attacker)
        # clear attacker state
        self.attacker = None
        self.attacker_original_pos = None
        # schedule next attack in 5-10 seconds
        self.next_attack_at = now + random.randint(5000, 10000)

    def handle_events(self, events):
        for event in events:
            # shoot when not paused or hit
            if event.type == pygame.KEYDOWN:
                # cheat toggle: invulnerability to enemy bullets
                if event.key == pygame.K_l:
                    self.invulnerable = not self.invulnerable
                    continue
                # debug: force spawn attacker dive
                elif event.key == pygame.K_d:
                    if self.attacker is None:
                        self.spawn_attacker()
                    continue
                if event.key == pygame.K_SPACE and not self.hit and not self.paused:
                    now = pygame.time.get_ticks()
                    self.player.shoot(now, self.bullets)
                # toggle pause
                elif event.key == pygame.K_p:
                    # only allow pause during active play
                    if not self.hit and not self.game_over:
                        self.paused = not self.paused
                # quit to intro
                elif event.key == pygame.K_q:
                    # immediately go to start scene
                    self.engine.change_state(GameState.START)

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
        # if paused, skip movement and collisions
        if self.paused:
            return
        # spawn attacker when timer elapses
        if self.attacker is None and now >= self.next_attack_at:
            self.spawn_attacker()
        # movement and firing
        update_entities(self, dt)
        # collisions (including bullets vs enemies)
        handle_collisions(self)
        # check if pack reached player's level: lose a life and start new wave
        pack_bottom = max((e.rect.bottom for e in self.enemies), default=0)
        if pack_bottom >= self.player.rect.top:
            now = pygame.time.get_ticks()
            # lose a life only if not in invulnerable (cheat) mode
            if not getattr(self, 'invulnerable', False):
                self.lose_life(now)
            # reset wave without ending game
            self.bullets.empty()
            self.enemy_bullets.empty()
            self.attacker = None
            self.enemies.empty()
            self._create_enemies()
            self.next_attack_at = now + random.randint(5000, 10000)
            return
        # check win condition: all enemies cleared
        if not self.enemies:
            # start next level
            now = pygame.time.get_ticks()
            self.bullets.empty()
            self.enemy_bullets.empty()
            self.attacker = None
            self._create_enemies()
            self.next_attack_at = now + random.randint(5000, 10000)
            return

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