import pygame
import sys
from config import WIDTH, HEIGHT, FPS, PLAYER_SPEED, BULLET_SPEED, ENEMY_SPEED_INIT, ENEMY_DROP, ROWS, COLS
from sprites import Player, Bullet, Enemy
class Game:
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

        self.create_enemies()

    def create_enemies(self):
        margin_x = 100
        margin_y = 60
        spacing_x = 60
        spacing_y = 50
        for row in range(ROWS):
            for col in range(COLS):
                x = margin_x + col * spacing_x
                y = margin_y + row * spacing_y
                self.enemies.add(Enemy((x, y)))

    def reset(self):
        self.bullets.empty()
        self.enemies.empty()
        self.enemy_speed = ENEMY_SPEED_INIT
        self.enemy_direction = 1
        self.score = 0
        self.game_over = False
        self.create_enemies()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                now = pygame.time.get_ticks()
                self.player.shoot(now, self.bullets)
            if self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    def update(self, dt):
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        self.players.update(dt)
        self.bullets.update(dt)

        move_x = self.enemy_speed * self.enemy_direction
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

    def draw(self):
        self.screen.fill("black")
        self.players.draw(self.screen)
        self.bullets.draw(self.screen)
        self.enemies.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, "white")
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            msg = "YOU WIN!" if not self.enemies else "GAME OVER"
            sub = "Press R to restart"
            msg_surf = self.font.render(msg, True, "yellow")
            sub_surf = self.font.render(sub, True, "yellow")
            self.screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
            self.screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
