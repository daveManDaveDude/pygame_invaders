import random
import pygame
import math
from config import WIDTH, HEIGHT, ENEMY_DROP, ENEMY_SPEED_FACTOR, ENEMY_FIRE_CHANCE, DIVE_AMPLITUDE, DIVE_SPEED
from sprites import EnemyBullet

def _update_attacker(scene, dt):
    """Update the dive attacker's aiming dive with a single sine oscillation."""
    attacker = scene.attacker
    # initialize dive parameters on first call
    if not hasattr(attacker, 'dive_t'):
        attacker.dive_t = 0.0
        attacker.start_x, attacker.start_y = attacker.rect.topleft
        # total dive duration based on vertical speed
        attacker.dive_T = max(0.0001, (HEIGHT - attacker.start_y) / DIVE_SPEED)
    # advance dive timer
    attacker.dive_t += dt
    # normalized progress [0..1]
    tau = attacker.dive_t / attacker.dive_T
    # finish dive when complete
    if tau >= 1.0:
        scene.on_attacker_finished(missed=True)
        return
    # horizontal base aiming directly toward current player position
    player_x = scene.player.rect.centerx
    base_x = attacker.start_x + (player_x - attacker.start_x) * tau
    # single sine oscillation about the base path
    x_offset = DIVE_AMPLITUDE * math.sin(2 * math.pi * tau)
    new_x = int(round(base_x + x_offset))
    # vertical interpolation down to bottom
    new_y = int(round(attacker.start_y + (HEIGHT - attacker.start_y) * tau))
    # update position
    attacker.rect.topleft = (new_x, new_y)

def update_entities(scene, dt):
    """
    Update movement for player, bullets, enemy bullets, and enemies (including drop and firing).
    scene must have attributes: hit, players, bullets, enemy_bullets, enemies,
    enemy_direction, enemy_speed.
    """
    if not scene.hit:
        scene.players.update(dt)
    scene.bullets.update(dt)
    scene.enemy_bullets.update(dt)
    # horizontal enemy movement
    move_x = scene.enemy_speed * scene.enemy_direction * dt
    enemies = scene.enemies.sprites()
    if enemies:
        # compute bounding rect
        group_rect = enemies[0].rect.copy()
        for e in enemies[1:]:
            group_rect.union_ip(e.rect)
        # check edges
        if group_rect.right + move_x >= WIDTH - 10 or group_rect.left + move_x <= 10:
            # descend and reverse
            for e in enemies:
                e.rect.y += ENEMY_DROP
            scene.enemy_direction *= -1
            scene.enemy_speed *= ENEMY_SPEED_FACTOR
            move_x = scene.enemy_speed * scene.enemy_direction * dt
        # apply movement
        for e in enemies:
            e.rect.x += move_x
        # random firing
        if not scene.enemy_bullets and random.random() < ENEMY_FIRE_CHANCE * dt:
            cols = {}
            for e in enemies:
                key = e.rect.x
                if key not in cols or e.rect.y > cols[key].rect.y:
                    cols[key] = e
            shooter = random.choice(list(cols.values()))
            scene.enemy_bullets.add(EnemyBullet(shooter.rect.midbottom))
    # update the dive attacker if present
    if getattr(scene, 'attacker', None):
        _update_attacker(scene, dt)