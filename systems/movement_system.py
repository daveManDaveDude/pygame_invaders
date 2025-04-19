import random
import pygame
from config import WIDTH, ENEMY_DROP, ENEMY_SPEED_FACTOR, ENEMY_FIRE_CHANCE
from sprites import EnemyBullet

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