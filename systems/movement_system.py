import random
import pygame
import math
from config import WIDTH, HEIGHT, ENEMY_DROP, ENEMY_SPEED_FACTOR, ENEMY_FIRE_CHANCE, DIVE_AMPLITUDE, DIVE_MIN_AMPLITUDE, DIVE_SPEED
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
            # initialize dive parameters and freeze target variables
            attacker.state = 'dive'
            attacker.dive_t = 0.0
            start_x, start_y = attacker.rect.topleft
            attacker.start_x, attacker.start_y = start_x, start_y
            attacker.dive_T = max(0.0001, (HEIGHT - attacker.start_y) / DIVE_SPEED)
            # capture static dive parameters: when the invader reaches player's y
            player_y0 = scene.player.rect.top
            if HEIGHT != start_y:
                tau_hit = (player_y0 - start_y) / (HEIGHT - start_y)
            else:
                tau_hit = 1.0
            attacker.tau_hit = max(0.0, min(1.0, tau_hit))
            attacker.overshoot_end = min(0.5, attacker.tau_hit * 0.5)
            # capture static overshoot x based on player's position at dive start
            player_x0 = scene.player.rect.centerx
            amp = DIVE_MIN_AMPLITUDE + attacker.tau_hit * (DIVE_AMPLITUDE - DIVE_MIN_AMPLITUDE)
            chase_dir = math.copysign(1.0, player_x0 - start_x)
            attacker.overshoot_x = player_x0 + chase_dir * amp
        return
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
    # horizontal movement: fixed overshoot then dynamic tracking
    player_x = scene.player.rect.centerx
    start_x = attacker.start_x
    overshoot_x = attacker.overshoot_x
    tau_hit = attacker.tau_hit
    overshoot_end = attacker.overshoot_end
    if tau < overshoot_end and overshoot_end > 0:
        # phase 1: fly toward static overshoot point
        sub_tau = tau / overshoot_end
        base_x = start_x + (overshoot_x - start_x) * sub_tau
    elif tau < tau_hit and tau_hit > overshoot_end:
        # phase 2: swoop back toward player's current position
        sub_tau = (tau - overshoot_end) / (tau_hit - overshoot_end)
        base_x = overshoot_x + (player_x - overshoot_x) * sub_tau
    else:
        # aligned or past alignment: hold at player's current x
        base_x = player_x
    new_x = int(round(base_x))
    # vertical interpolation with ease-in (initially shallower)
    new_y = int(round(attacker.start_y + (HEIGHT - attacker.start_y) * (tau ** 2)))
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