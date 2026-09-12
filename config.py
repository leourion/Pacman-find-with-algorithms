"""
Configuration file for Pac-Man AI Game
Contains all game constants and settings
"""

# Screen dimensions
WIDTH = 900
HEIGHT = 950
FPS = 60

# Colors — base
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
BLUE   = (0, 0, 255)
RED    = (255, 0, 0)
PINK   = (255, 192, 203)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
CYAN   = (0, 255, 255)

# Modern neon palette
BG_COLOR        = (0, 0, 0)           # Nền đen tuyền như hình mẫu
MAZE_COLOR      = (33, 33, 222)       # Tường xanh cobalt — đúng màu hình mẫu
MAZE_BORDER     = (60, 60, 240)       # Viền tường
MAZE_FILL       = (33, 33, 222)       # Fill tường
MAZE_INNER      = (20, 20, 150)       # Inner shadow
DOT_COLOR       = (255, 150, 50)      # Chấm cam (khớp hình mẫu)
DOT_GLOW        = (255, 180, 80)      # Glow chấm
PELLET_COLOR    = (255, 255, 255)     # Power pellet trắng
PELLET_GLOW     = (220, 240, 255)     # Glow pellet nhạt
GATE_COLOR      = (180, 140, 255)     # Cổng ghost house
UI_BG           = (5, 5, 25)         # Nền panel UI
UI_ACCENT       = (60, 100, 255)      # Accent xanh
UI_TEXT         = (220, 220, 255)     # Text chính
UI_HIGHLIGHT    = (255, 220, 50)      # Highlight vàng
UI_GREEN        = (80, 255, 160)      # Xanh lá neon
UI_ORANGE       = (255, 140, 40)      # Cam neon
SCORE_COLOR     = (255, 220, 50)      # Màu điểm số
PACMAN_COLOR    = (255, 230, 0)       # Pacman vàng tươi
GHOST_SCARED    = (30, 60, 200)       # Ghost sợ hãi

# Game settings
PLAYER_SPEED = 2
GHOST_SPEED = 2
GHOST_SPEED_SCARED = 1
GHOST_SPEED_DEAD = 4

# Scoring
SCORE_DOT = 10
SCORE_POWER_PELLET = 50
SCORE_GHOST_BASE = 200

# Power-up duration (frames)
POWERUP_DURATION = 600
STARTUP_DURATION = 180

# Grid dimensions
TILE_HEIGHT = (HEIGHT - 50) // 32
TILE_WIDTH = WIDTH // 30

# Initial positions
PLAYER_START_X = 450
PLAYER_START_Y = 663

BLINKY_START_X = 56
BLINKY_START_Y = 58

INKY_START_X = 440
INKY_START_Y = 388

PINKY_START_X = 440
PINKY_START_Y = 438

CLYDE_START_X = 440
CLYDE_START_Y = 438

# Board tile types
TILE_EMPTY = 0
TILE_DOT = 1
TILE_POWER_PELLET = 2
TILE_VERTICAL = 3
TILE_HORIZONTAL = 4
TILE_TOP_RIGHT = 5
TILE_TOP_LEFT = 6
TILE_BOTTOM_LEFT = 7
TILE_BOTTOM_RIGHT = 8
TILE_GATE = 9

# Directions
DIR_RIGHT = 0
DIR_LEFT = 1
DIR_UP = 2
DIR_DOWN = 3

# AI Algorithm modes
MODE_MANUAL = 0
MODE_BFS = 1
MODE_DFS = 2
MODE_UCS = 3
MODE_ASTAR = 4
MODE_GBFS = 5
MODE_MINIMAX = 6

# Algorithm names for display
ALGORITHM_NAMES = {
    MODE_MANUAL: "Manual Control",
    MODE_BFS: "Breadth-First Search",
    MODE_DFS: "Depth-First Search",
    MODE_UCS: "Uniform Cost Search",
    MODE_ASTAR: "A* Search",
    MODE_GBFS: "Greedy Best-First Search",
    MODE_MINIMAX: "Minimax (Alpha-Beta)"
}

# Minimax settings
MINIMAX_DEPTH = 3
ALPHABETA_DEPTH = 4

# -------------------------------------------------------
# UCS: tile cost map (FIX #1 — UCS khác BFS bằng cost)
# Pacman không thích đi gần tường hẹp → ô trống gần
# góc/hành lang hẹp tốn chi phí cao hơn.
# Giá trị mặc định = 1 (đi bình thường),
# TILE_POWER_PELLET = 0.5 (ưu tiên ăn power pellet),
# TILE_EMPTY ở vùng ghost-house = 3 (tránh khu ghost).
# -------------------------------------------------------
UCS_TILE_COSTS = {
    TILE_EMPTY: 2,          # Ô trống trong mê cung: cost cao hơn (hành lang hẹp)
    TILE_DOT: 1,            # Ô có chấm: cost thấp nhất — ưu tiên đi qua để ăn
    TILE_POWER_PELLET: 1,   # Power pellet: ưu tiên như chấm thường
    TILE_GATE: 10,          # Cổng ghost house: rất đắt, Pacman hầu như không qua
}

# Vùng ghost house (grid rows, cols) — dùng để tăng cost UCS
# TILE_GATE nằm ở row=13, cols=14-15; interior ghost house rows 12-18, cols 11-18
GHOST_HOUSE_ROW_MIN = 12
GHOST_HOUSE_ROW_MAX = 18
GHOST_HOUSE_COL_MIN = 11
GHOST_HOUSE_COL_MAX = 18
GHOST_HOUSE_COST = 5        # Ô trong vùng ghost house tốn cost cao
