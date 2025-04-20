import pygame
import os
import random
from config import WIDTH, HEIGHT, PLAYER_SPEED, BULLET_SPEED

# threshold for alpha when detecting sprite regions (for cropping lasers)
ALPHA_THRESHOLD = 64

# Sprite sheet constants (deferred loading until after display init)
_SPRITE_SHEET_PATH = os.path.join(os.path.dirname(__file__), 'spritesheet.png')
_SPRITE_SHEET = None
_SPRITE_CACHE = {}
_SHEET_COLS = 4  # legacy: number of grid columns (used for thresholding)
_SHEET_ROWS = 4  # legacy: number of grid rows (used for thresholding)
_CELL_WIDTH = None  # unused in dynamic extraction
_CELL_HEIGHT = None  # unused in dynamic extraction

def _load_sheet():
    """Load and convert the sprite sheet once the display is initialized."""
    global _SPRITE_SHEET, _CELL_WIDTH, _CELL_HEIGHT
    if _SPRITE_SHEET is None:
        sheet = pygame.image.load(_SPRITE_SHEET_PATH)
        _SPRITE_SHEET = sheet.convert_alpha()
        _CELL_WIDTH = _SPRITE_SHEET.get_width() // _SHEET_COLS
        _CELL_HEIGHT = _SPRITE_SHEET.get_height() // _SHEET_ROWS
    return _SPRITE_SHEET

def _get_sprite(col, row):
    """Extract a single sprite cell from the sheet."""
    key = (col, row)
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]
    sheet = _load_sheet()
    rect = pygame.Rect(col * _CELL_WIDTH, row * _CELL_HEIGHT, _CELL_WIDTH, _CELL_HEIGHT)
    temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    temp.blit(sheet, (0, 0), rect)
    # trim any transparent border around the sprite
    bbox = temp.get_bounding_rect()
    if bbox.width and bbox.height:
        image = temp.subsurface(bbox).copy()
    else:
        image = temp
    _SPRITE_CACHE[key] = image
    return image
# Basic grid-based sprite grouping (4x4 cells)
def _extract_sprite_groups():
    """Return the sprite sheet cells as a list of rows of images."""
    sheet = _load_sheet()
    groups = []
    for row in range(_SHEET_ROWS):
        imgs = []
        for col in range(_SHEET_COLS):
            imgs.append(_get_sprite(col, row))
        groups.append(imgs)
    return groups

def get_enemy_sprite():
    """Crisp scaling for enemy: randomly pick one of the 8 sprites in the first two rows."""
    # choose a random column (0.._SHEET_COLS-1) and row (0 or 1)
    col = random.randrange(_SHEET_COLS)
    row = random.randrange(2)
    orig = _get_sprite(col, row)
    # scale to uniform size (square) to avoid vertical squashing
    size = 40
    return pygame.transform.smoothscale(orig, (size, size))

def get_player_sprite():
    # crisp scaling for player
    return pygame.transform.smoothscale(_get_sprite(0, 2), (50, 30))

def get_enemy_laser_sprite():
    """Extract a single enemy laser sprite, crop out one beam, then scale and brighten."""
    # ensure sheet loaded
    sheet = _load_sheet()
    # full cell at column 2 of last row
    cw, ch = _CELL_WIDTH, _CELL_HEIGHT
    cell_rect = pygame.Rect(2 * cw, 3 * ch, cw, ch)
    cell = sheet.subsurface(cell_rect).copy()
    # trim transparent border
    br = cell.get_bounding_rect()
    bs = cell.subsurface(br).copy()
    # find contiguous x-runs of non-transparent pixels
    w, h = bs.get_size()
    runs = []
    start = None
    for x in range(w):
        non_empty = False
        for y in range(h):
            if bs.get_at((x, y)).a > ALPHA_THRESHOLD:
                non_empty = True
                break
        if non_empty:
            if start is None:
                start = x
        else:
            if start is not None:
                runs.append((start, x - 1))
                start = None
    if start is not None:
        runs.append((start, w - 1))
    # pick first run for enemy
    if runs:
        xs, xe = runs[0]
        beam = bs.subsurface(pygame.Rect(xs, 0, xe - xs + 1, h)).copy()
    else:
        beam = bs
    # scale down and brighten enemy laser
    sprite = pygame.transform.smoothscale(beam, (8, 24))
    bright = sprite.copy()
    bright.fill((150, 150, 150), special_flags=pygame.BLEND_RGB_ADD)
    return bright

def get_player_laser_sprite():
    """Extract a single player laser sprite, crop out one beam, then scale and brighten."""
    sheet = _load_sheet()
    cw, ch = _CELL_WIDTH, _CELL_HEIGHT
    cell_rect = pygame.Rect(3 * cw, 3 * ch, cw, ch)
    cell = sheet.subsurface(cell_rect).copy()
    # trim transparent border
    br = cell.get_bounding_rect()
    bs = cell.subsurface(br).copy()
    # split right half for player laser
    w, h = bs.get_size()
    half = w // 2
    beam = bs.subsurface(pygame.Rect(half, 0, w - half, h)).copy()
    # scale down to slightly smaller laser
    sprite = pygame.transform.smoothscale(beam, (6, 18))
    # moderate brighten: add to both color and alpha for visibility
    bright = sprite.copy()
    bright.fill((150, 150, 150, 150), special_flags=pygame.BLEND_RGBA_ADD)
    # ensure any visible pixel is fully opaque
    bw, bh = bright.get_size()
    for bx in range(bw):
        for by in range(bh):
            r, g, b, a = bright.get_at((bx, by))
            if a != 0:
                bright.set_at((bx, by), (r, g, b, 255))
    return bright

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = get_player_sprite()
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
        self.image = get_player_laser_sprite()
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self, dt):
        self.rect.y -= BULLET_SPEED * dt
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = get_enemy_sprite()
        self.rect = self.image.get_rect(topleft=pos)
        
# Enemy bullet fired by invaders
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = get_enemy_laser_sprite()
        self.rect = self.image.get_rect(midtop=pos)

    def update(self, dt):
        self.rect.y += BULLET_SPEED * dt
        if self.rect.top > HEIGHT:
            self.kill()