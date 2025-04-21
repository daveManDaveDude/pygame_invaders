import random
import pygame
import math
from config import WIDTH, HEIGHT, ENEMY_DROP, ENEMY_SPEED_FACTOR, ENEMY_FIRE_CHANCE, DIVE_AMPLITUDE, DIVE_MIN_AMPLITUDE, DIVE_SPEED, DIVE_FIRE_INTERVAL
from sprites import EnemyBullet

def _update_attacker(scene, dt):
    """Update the dive attacker's movement: overshoot the player then dive in."""
    attacker = scene.attacker
    # clearance phase: drop below pack before starting dive
    if getattr(attacker, 'state', None) == 'clearance':
        # follow pack horizontally
        move_x = scene.enemy_speed * scene.enemy_direction * dt
        attacker.rect.x += move_x
        # drop vertically at dive speed
        attacker.rect.y += DIVE_SPEED * dt
        # transition to dive when below pack
        if attacker.rect.top >= getattr(attacker, 'clearance_target', 0):
            # transition into the dive phase
            attacker.state = 'dive'
            # reset dive timer and record start position
            attacker.dive_t = 0.0
            attacker.start_x, attacker.start_y = attacker.rect.topleft
            # compute total dive duration based on vertical speed
            attacker.dive_T = max(0.0001, (HEIGHT - attacker.start_y) / DIVE_SPEED)
            # randomize horizontal phase offset to vary left/right entry
            attacker.phi = random.choice([0.0, math.pi])
        return
    # --- dive phase (sine‐biased oscillation toward the player) ---
    # advance dive timer and normalize
    attacker.dive_t += dt
    tau = attacker.dive_t / attacker.dive_T
    # finish dive if complete
    if tau >= 1.0:
        scene.on_attacker_finished(missed=True)
        return
    # base path: linear interpolation toward player's current X
    player_x = scene.player.rect.centerx
    base_x = attacker.start_x + (player_x - attacker.start_x) * tau
    # horizontal oscillation: sine wave with randomized phase
    x_offset = DIVE_AMPLITUDE * math.sin(2 * math.pi * tau + attacker.phi)
    new_x = int(round(base_x + x_offset))
    # vertical interpolation with ease-in (initially shallower)
    new_y = int(round(attacker.start_y + (HEIGHT - attacker.start_y) * (tau ** 2)))
    # update position
    attacker.rect.topleft = (new_x, new_y)
    # diving attacker firing: shoot every DIVE_FIRE_INTERVAL seconds
    if not hasattr(attacker, 'fire_timer'):
        attacker.fire_timer = 0.0
    attacker.fire_timer += dt
    if attacker.fire_timer >= DIVE_FIRE_INTERVAL:
        attacker.fire_timer -= DIVE_FIRE_INTERVAL
        scene.enemy_bullets.add(EnemyBullet(attacker.rect.midbottom))

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