from __future__ import division
import const.generated_level_types as GENERATED_LEVEL_TYPE

OPTIMIZATION = True

MSG_BAR_HEIGHT = 2
STATUS_BAR_HEIGHT = 2

_N = 6

SCREEN_ROWS = 5 * _N
SCREEN_COLS = 16 * _N

LEVEL_HEIGHT = SCREEN_ROWS - MSG_BAR_HEIGHT - STATUS_BAR_HEIGHT
LEVEL_WIDTH = SCREEN_COLS

MOVEMENT_COST = 1000
ATTACK_COST = 1000
DIAGONAL_MODIFIER = 2 ** 0.5

LEVEL_TYPE = GENERATED_LEVEL_TYPE.DUNGEON

MONSTERS_PER_LEVEL = 99
LEVELS_PER_DUNGEON = 99

# in seconds
ANIMATION_DELAY = 0.02
INPUT_INTERVAL = min(ANIMATION_DELAY / 10, 0.01)

GAME_NAME = "pyrl"
DATA_FOLDER = "data"
SAVE_FILE_COMPRESSION_LEVEL = 6 # valid in range(1, 10)

ENCODING = "utf-8"

SET_LEVEL = "set-level"
NEXT_LEVEL = "next-level"
PREVIOUS_LEVEL = "previous-level"
UP = (PREVIOUS_LEVEL, None, None)
DOWN = (NEXT_LEVEL, None, None)

DUNGEON = "dungeon"
FIRST_LEVEL = (DUNGEON, 1)

PASSAGE_UP = "an exit going up"
PASSAGE_DOWN = "an exit going down"
PASSAGE_RANDOM = "random entry point"

NCURSES = "ncurses"
LIBTCOD = "libtcod"
