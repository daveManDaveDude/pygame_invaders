import pygame
from sprites import Explosion

def handle_collisions(scene):
    """
    Handle collisions: bullets vs enemies, enemy bullets vs player,
    and check game over conditions.
    scene must have attributes: bullets, enemies, enemy_bullets, player,
    hit, score, game_over, lose_life.
    """
    # diving attacker vs player
    attacker = getattr(scene, 'attacker', None)
    if attacker and not scene.hit:
        # if attacker collides with player
        if attacker.rect.colliderect(scene.player.rect):
            now = pygame.time.get_ticks()
            # lose life only if not invulnerable
            if not getattr(scene, 'invulnerable', False):
                scene.lose_life(now)
                scene.on_attacker_finished(missed=False)
            else:
                # invulnerable: treat as missed dive
                scene.on_attacker_finished(missed=True)
    # allow player to shoot the diving attacker
    attacker = getattr(scene, 'attacker', None)
    if attacker:
        # bullets that hit the attacker are removed
        hits = pygame.sprite.spritecollide(attacker, scene.bullets, True)
        if hits:
            # spawn explosion at attacker position with pack velocity
            vx = getattr(scene, 'enemy_speed', 0) * getattr(scene, 'enemy_direction', 0)
            explosion = Explosion(attacker.rect.center, velocity=(vx, 0))
            scene.explosions.add(explosion)
            # award points for attacker kill
            scene.score += len(hits) * 10
            # finish attack (no respawn)
            scene.on_attacker_finished(missed=False)
    # player bullets vs enemies
    hits = pygame.sprite.groupcollide(scene.enemies, scene.bullets, True, True)
    # spawn explosion for each enemy hit with pack velocity
    vx = getattr(scene, 'enemy_speed', 0) * getattr(scene, 'enemy_direction', 0)
    for enemy in hits:
        explosion = Explosion(enemy.rect.center, velocity=(vx, 0))
        scene.explosions.add(explosion)
    scene.score += len(hits) * 10
    # enemy bullets vs player
    if not scene.hit:
        # bullets that hit the player are removed
        hits = pygame.sprite.spritecollide(scene.player, scene.enemy_bullets, True)
        if hits:
            # only lose life if not invulnerable
            if not getattr(scene, 'invulnerable', False):
                scene.lose_life(pygame.time.get_ticks())