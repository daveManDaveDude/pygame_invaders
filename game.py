import pygame
import sys
import random
from config import WIDTH, HEIGHT, FPS, PLAYER_SPEED, BULLET_SPEED, ENEMY_SPEED_INIT, ENEMY_DROP, ENEMY_SPEED_FACTOR, ENEMY_FIRE_CHANCE, ROWS, COLS, ENEMY_MARGIN_X, ENEMY_MARGIN_Y, ENEMY_SPACING_X, ENEMY_SPACING_Y, BG_COLOR, TEXT_COLOR, MSG_COLOR
from sprites import Player, Bullet, Enemy, EnemyBullet
class Game:
    # game states
    STATE_START = "START"
    STATE_PLAYING = "PLAYING"
    STATE_GAME_OVER = "GAME_OVER"
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        pygame.display.set_caption("Space Invaders – Pygame Basics")

        self.player = Player()
        self.players = pygame.sprite.GroupSingle(self.player)
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        # group for enemy-fired bullets
        self.enemy_bullets = pygame.sprite.Group()

        self.enemy_direction = 1
        self.enemy_speed = ENEMY_SPEED_INIT
        self.score = 0
        self.game_over = False
        # initial state: show start screen
        self.state = self.STATE_START

        self.create_enemies()

    def create_enemies(self):
        for row in range(ROWS):
            for col in range(COLS):
                x = ENEMY_MARGIN_X + col * ENEMY_SPACING_X
                y = ENEMY_MARGIN_Y + row * ENEMY_SPACING_Y
                self.enemies.add(Enemy((x, y)))

    def reset(self):
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.enemies.empty()
        self.enemy_speed = ENEMY_SPEED_INIT
        self.enemy_direction = 1
        self.score = 0
        self.game_over = False
        # reset player sprite and position
        self.players.empty()
        self.player = Player()
        self.players.add(self.player)
        # recreate enemies
        self.create_enemies()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # start screen: wait for SPACE to begin
            if self.state == self.STATE_START:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.reset()
                    self.state = self.STATE_PLAYING
            # playing: handle shooting
            elif self.state == self.STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    now = pygame.time.get_ticks()
                    self.player.shoot(now, self.bullets)
            # game over: return to start screen
            elif self.state == self.STATE_GAME_OVER:
                # use Enter key to return to start menu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = self.STATE_START

    def update(self, dt):
        # only update game logic when playing
        if self.state != self.STATE_PLAYING:
            return

        now = pygame.time.get_ticks()
        self.players.update(dt)
        self.bullets.update(dt)
        # update invader-fired bullets
        self.enemy_bullets.update(dt)

        # Enemy block movement: compute group bounds once, then branch on edges
        move_x = self.enemy_speed * self.enemy_direction * dt
        enemies = self.enemies.sprites()
        if enemies:
            # compute bounding rect of the enemy group
            group_rect = enemies[0].rect.copy()
            for e in enemies[1:]:
                group_rect.union_ip(e.rect)
            # check if next horizontal move would hit screen edges (10px margin)
            if group_rect.right + move_x >= WIDTH - 10 or group_rect.left + move_x <= 10:
                # descend and reverse direction, then accelerate
                for e in enemies:
                    e.rect.y += ENEMY_DROP
                self.enemy_direction *= -1
                self.enemy_speed *= ENEMY_SPEED_FACTOR
                # recalc horizontal movement after reversing
                move_x = self.enemy_speed * self.enemy_direction * dt
            # apply horizontal movement
            for e in enemies:
                e.rect.x += move_x
            # random invader firing independent of bounce
            if enemies and not self.enemy_bullets and random.random() < ENEMY_FIRE_CHANCE * dt:
                bottom_y = max(e.rect.y for e in enemies)
                bottom_enemies = [e for e in enemies if e.rect.y == bottom_y]
                shooter = random.choice(bottom_enemies)
                self.enemy_bullets.add(EnemyBullet(shooter.rect.midbottom))

        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        self.score += len(hits) * 10

        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break
        # enemy bullets hitting player
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.game_over = True

        if not self.enemies:
            self.game_over = True
        # transition to game over state
        if self.game_over:
            self.state = self.STATE_GAME_OVER

    def draw(self):
        self.screen.fill(BG_COLOR)
        # start screen
        if self.state == self.STATE_START:
            title = self.font.render("SPACE INVADERS", True, TEXT_COLOR)
            title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
            self.screen.blit(title, title_rect)
            instr1 = self.font.render("Left/Right: Move", True, TEXT_COLOR)
            instr2 = self.font.render("Space: Shoot", True, TEXT_COLOR)
            instr3 = self.font.render("Press SPACE to Start", True, TEXT_COLOR)
            self.screen.blit(instr1, instr1.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
            self.screen.blit(instr2, instr2.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
            self.screen.blit(instr3, instr3.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))
        # game screen
        elif self.state == self.STATE_PLAYING:
            self.players.draw(self.screen)
            self.bullets.draw(self.screen)
            # draw invader-fired bullets
            self.enemy_bullets.draw(self.screen)
            self.enemies.draw(self.screen)
            score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
            self.screen.blit(score_text, (10, 10))
        # game over screen
        elif self.state == self.STATE_GAME_OVER:
            msg = "YOU WIN!" if not self.enemies else "GAME OVER"
            sub = "Press ENTER to return to menu"
            msg_surf = self.font.render(msg, True, MSG_COLOR)
            sub_surf = self.font.render(sub, True, MSG_COLOR)
            self.screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
            self.screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))

    def run(self):
        while True:
            # cap frame rate and get elapsed time in milliseconds
            dt_ms = self.clock.tick(FPS)
            # convert ms to seconds for consistent movement
            dt = dt_ms / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
