import pygame
from config import BG_COLOR, TEXT_COLOR, MSG_COLOR

def render_start(scene, screen):
    """Draw the start screen."""
    screen.fill(BG_COLOR)
    w, h = screen.get_width(), screen.get_height()
    title = scene.font.render("SPACE INVADERS", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(w//2, h//2 - 60)))
    instr1 = scene.font.render("Left/Right: Move", True, TEXT_COLOR)
    instr2 = scene.font.render("Space: Shoot", True, TEXT_COLOR)
    instr3 = scene.font.render("Press SPACE to Start", True, TEXT_COLOR)
    screen.blit(instr1, instr1.get_rect(center=(w//2, h//2 - 20)))
    screen.blit(instr2, instr2.get_rect(center=(w//2, h//2 + 10)))
    screen.blit(instr3, instr3.get_rect(center=(w//2, h//2 + 40)))
    # quit instruction
    instr4 = scene.font.render("Press Q to Quit", True, TEXT_COLOR)
    screen.blit(instr4, instr4.get_rect(center=(w//2, h//2 + 70)))

def render_play(scene, screen):
    """Draw the playing screen: entities and HUD."""
    screen.fill(BG_COLOR)
    # draw player sprite if not hit; explosion animation handles hit state
    if not scene.hit:
        scene.players.draw(screen)
    scene.bullets.draw(screen)
    scene.enemy_bullets.draw(screen)
    scene.enemies.draw(screen)
    # draw the diving attacker separately (detached from pack)
    if getattr(scene, 'attacker', None) is not None:
        screen.blit(scene.attacker.image, scene.attacker.rect)
    # draw explosions
    if hasattr(scene, 'explosions'):
        scene.explosions.draw(screen)
    # HUD
    score_text = scene.font.render(f"Score: {scene.score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))
    w = screen.get_width()
    # render lives, with a * if invulnerability cheat is active
    lives_str = f"Lives: {scene.lives}"
    if getattr(scene, 'invulnerable', False):
        lives_str += "*"
    lives_text = scene.font.render(lives_str, True, TEXT_COLOR)
    screen.blit(lives_text, (w - lives_text.get_width() - 10, 10))
    # pause indicator
    if getattr(scene, 'paused', False):
        # render pause text without dimming background
        w, h = screen.get_size()
        pause_surf = scene.font.render("PAUSED", True, TEXT_COLOR)
        screen.blit(pause_surf, pause_surf.get_rect(center=(w//2, h//2)))

def render_game_over(scene, screen):
    """Draw the game over screen."""
    screen.fill(BG_COLOR)
    w, h = screen.get_width(), screen.get_height()
    # Determine win/loss displayed (GameOverScene should set `win` flag on enter)
    win = getattr(scene, 'win', False)
    msg = "YOU WIN!" if win else "GAME OVER"
    sub = "Press ENTER to return to menu"
    msg_surf = scene.font.render(msg, True, MSG_COLOR)
    sub_surf = scene.font.render(sub, True, MSG_COLOR)
    screen.blit(msg_surf, msg_surf.get_rect(center=(w//2, h//2 - 20)))
    screen.blit(sub_surf, sub_surf.get_rect(center=(w//2, h//2 + 20)))