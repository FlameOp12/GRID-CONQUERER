from enum import Enum

# Game board dimensions
BOARD_SIZE = 8
TILE_SIZE = 80  # Size of each tile in pixels

# Colors
PLAYER1_COLOR = (33, 150, 243)  # Blue
PLAYER2_COLOR = (244, 67, 54)   # Red
GRID_BG_COLOR = (245, 245, 245) # Light gray
GRID_LINE_COLOR = (51, 51, 51)  # Dark gray
SELECTED_COLOR = (255, 235, 59) # Yellow
VALID_MOVE_COLOR = (76, 165, 80) # Green
VALID_ATTACK_COLOR = (255, 87, 34) # Red
VALID_HEAL_COLOR = (33, 150, 243) # Blue for healing

# Game states
class GameState(Enum):
    PLACEMENT_PHASE = 1
    PLAYER_1_TURN = 2
    PLAYER_2_TURN = 3
    GAME_OVER = 4

# Unit types
class UnitType(Enum):
    SOLDIER = 1
    KNIGHT = 2
    HEALER = 3
    WALL = 4
    CROWN = 5

# Unit stats
UNIT_STATS = {
    UnitType.SOLDIER: {
        'hp': 100,
        'attack': 50,
        'attack_range': 1,
        'move_range': 1,
        'symbol': '🪖'
    },
    UnitType.KNIGHT: {
        'hp': 150,
        'attack': 50,
        'attack_range': 1,
        'move_range': 1,
        'symbol': '🛡️'
    },
    UnitType.HEALER: {
        'hp': 170,
        'attack': 50,
        'attack_range': 1,
        'move_range': 1,
        'symbol': '🧙'
    },
    UnitType.WALL: {
        'hp': 200,
        'attack': 0,
        'attack_range': 0,
        'move_range': 0,
        'symbol': '🧱'
    },
    UnitType.CROWN: {
        'hp': 500,
        'attack': 0,
        'attack_range': 0,
        'move_range': 0,
        'symbol': '👑'
    }
}

# Movement directions
ORTHOGONAL_DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
DIAGONAL_DIRECTIONS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonal
ALL_DIRECTIONS = ORTHOGONAL_DIRECTIONS + DIAGONAL_DIRECTIONS

# Window settings
WINDOW_WIDTH = BOARD_SIZE * TILE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * TILE_SIZE
WINDOW_TITLE = "Grid Conquer"

# Game settings
HEAL_AMOUNT = 30
HEALER_HEAL_COST = 30 