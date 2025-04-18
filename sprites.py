import pygame
from config import WIDTH, HEIGHT, PLAYER_SPEED, BULLET_SPEED, PLAYER_COLOR, BULLET_COLOR, ENEMY_COLOR

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 40))
        self.reload_delay = 300  # ms between shots
        self.last_shot = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED * dt
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

    def shoot(self, now, bullets_group):
        if now - self.last_shot >= self.reload_delay:
            bullet = Bullet(self.rect.midtop)
            bullets_group.add(bullet)
            self.last_shot = now

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self, dt):
        self.rect.y -= BULLET_SPEED * dt
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((40, 25))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect(topleft=pos)