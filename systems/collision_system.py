import pygame

def handle_collisions(scene):
    """
    Handle collisions: bullets vs enemies, enemy bullets vs player,
    and check game over conditions.
    scene must have attributes: bullets, enemies, enemy_bullets, player,
    hit, score, game_over, lose_life.
    """
    # diving attacker collision detection disabled for now
    # allow player to shoot the diving attacker
    if getattr(scene, 'attacker', None):
        # bullets that hit the attacker are removed
        hits = pygame.sprite.spritecollide(scene.attacker, scene.bullets, True)
        if hits:
            # award points for attacker kill
            scene.score += len(hits) * 10
            # finish attack (no respawn)
            scene.on_attacker_finished(missed=False)
    # player bullets vs enemies
    hits = pygame.sprite.groupcollide(scene.enemies, scene.bullets, True, True)
    scene.score += len(hits) * 10
    # enemies reaching player
    for enemy in scene.enemies:
        if enemy.rect.bottom >= scene.player.rect.top:
            scene.game_over = True
            break
    # enemy bullets vs player
    if not scene.hit:
        # bullets that hit the player are removed
        hits = pygame.sprite.spritecollide(scene.player, scene.enemy_bullets, True)
        if hits:
            # only lose life if not invulnerable
            if not getattr(scene, 'invulnerable', False):
                scene.lose_life(pygame.time.get_ticks())
    # win condition: all enemies destroyed
    if not scene.enemies:
        scene.game_over = True