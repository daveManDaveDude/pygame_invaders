# Game configuration constants
WIDTH, HEIGHT = 800, 600
FPS = 60
# Speeds are now in pixels per second; original px/frame multiplied by FPS
PLAYER_SPEED = 5 * FPS
BULLET_SPEED = 8 * FPS
ENEMY_SPEED_INIT = 1.0 * FPS      # starts slow, accelerates
ENEMY_DROP = 20             # pixels enemies descend when they hit an edge
ENEMY_SPEED_FACTOR = 1.05    # multiplier applied to enemy speed each time they descend
ENEMY_FIRE_CHANCE = 0.5     # probability invader fires when eligible
ROWS, COLS = 4, 8           # enemy formation

# Enemy formation layout
ENEMY_MARGIN_X = 100
ENEMY_MARGIN_Y = 60
ENEMY_SPACING_X = 60
ENEMY_SPACING_Y = 50

# Colors
BG_COLOR = "black"
TEXT_COLOR = "white"
MSG_COLOR = "yellow"
PLAYER_COLOR = "white"
BULLET_COLOR = "cyan"
ENEMY_COLOR = "lime"