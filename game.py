import pygame
import sys
from config import WIDTH, HEIGHT, FPS, PLAYER_SPEED, BULLET_SPEED, ENEMY_SPEED_INIT, ENEMY_DROP, ROWS, COLS, ENEMY_MARGIN_X, ENEMY_MARGIN_Y, ENEMY_SPACING_X, ENEMY_SPACING_Y, BG_COLOR, TEXT_COLOR, MSG_COLOR
from sprites import Player, Bullet, Enemy
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

        move_x = self.enemy_speed * self.enemy_direction * dt
        descend = False
        for enemy in self.enemies:
            enemy.rect.x += move_x
            if enemy.rect.right >= WIDTH - 10 or enemy.rect.left <= 10:
                descend = True
        if descend:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                enemy.rect.y += ENEMY_DROP
            self.enemy_speed *= 1.05

        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        self.score += len(hits) * 10

        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break

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
