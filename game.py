import pygame
import sys
import random
from config import WIDTH, HEIGHT, FPS, PLAYER_SPEED, BULLET_SPEED, ENEMY_SPEED_INIT, ENEMY_DROP, ENEMY_SPEED_FACTOR, ENEMY_FIRE_CHANCE, ROWS, COLS, ENEMY_MARGIN_X, ENEMY_MARGIN_Y, ENEMY_SPACING_X, ENEMY_SPACING_Y, BG_COLOR, TEXT_COLOR, MSG_COLOR, LIVES
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
        # initialize player lives
        self.lives = LIVES
        # blinking / invulnerability state after hit or final death flash
        self.hit = False
        self.hit_start = 0
        self.hit_duration = 1000  # milliseconds
        self.death_pos = None
        # flag to indicate final-life flash before game over
        self.final_death = False

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
        # reset player lives
        self.lives = LIVES
        # reset player sprite and position
        self.players.empty()
        self.player = Player()
        self.players.add(self.player)
        # clear any final-death state
        self.final_death = False
        # recreate enemies
        self.create_enemies()

    def lose_life(self, now):
        """Decrease life count; if lives remain, start invulnerability; otherwise flash then game over."""
        self.lives -= 1
        # still have lives: normal invulnerability blink
        if self.lives > 0:
            self.bullets.empty()
            self.enemy_bullets.empty()
            self.hit = True
            self.hit_start = now
            self.death_pos = self.player.rect.midbottom
            self.player.last_shot = now
        # final life lost: flash before game over
        else:
            self.bullets.empty()
            self.enemy_bullets.empty()
            self.hit = True
            self.hit_start = now
            self.death_pos = self.player.rect.midbottom
            self.final_death = True
            # ensure shoot timer reset (no shooting expected)
            self.player.last_shot = now

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
                # during invulnerability blinking, do not accept shoot input
                if not self.hit and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
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
        # finish blinking/invulnerability or final-death flash if duration elapsed
        if self.hit and now - self.hit_start >= self.hit_duration:
            # if this was the final death, transition to game over
            if self.final_death:
                self.hit = False
                self.final_death = False
                self.state = self.STATE_GAME_OVER
            else:
                # end invulnerability, respawn player
                self.hit = False
                self.player.rect.midbottom = self.death_pos
                self.player.last_shot = now
        # update player movement if not blinking
        if not self.hit:
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
            # allow any invader with no blocker below in its column to fire
            if not self.enemy_bullets and random.random() < ENEMY_FIRE_CHANCE * dt:
                cols = {}
                for e in enemies:
                    key = e.rect.x
                    if key not in cols or e.rect.y > cols[key].rect.y:
                        cols[key] = e
                shooters = list(cols.values())
                shooter = random.choice(shooters)
                self.enemy_bullets.add(EnemyBullet(shooter.rect.midbottom))

        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        self.score += len(hits) * 10

        for enemy in self.enemies:
            if enemy.rect.bottom >= self.player.rect.top:
                self.game_over = True
                break
        # enemy bullets hitting player
        if not self.hit and pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.lose_life(now)

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
            # draw player (blinking effect if hit)
            if self.hit:
                # flashing random colors during invulnerability
                blink_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                pygame.draw.rect(self.screen, blink_color, self.player.rect)
            else:
                self.players.draw(self.screen)
            self.bullets.draw(self.screen)
            # draw invader-fired bullets
            self.enemy_bullets.draw(self.screen)
            self.enemies.draw(self.screen)
            score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
            self.screen.blit(score_text, (10, 10))
            lives_text = self.font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
            self.screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
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
