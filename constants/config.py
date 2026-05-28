
MOVE_COST   = 1
LOAD_COST   = 1 
UNLOAD_COST = 1


GRID_WIDTH  = 3
GRID_HEIGHT = 3


MAX_STATES_EXPANDED = 50_000  
MAX_FRONTIER_SIZE   = 100_000  

HEURISTIC_WEIGHT = 1.0

PRINT_SEARCH_TREE   = True 
PRINT_SOLUTION_PATH = True   
PRINT_ASCII_MAP     = True   
VERBOSE_RULES       = False  

DIRECTIONS = [
    (-1,  0, "UP"),
    ( 1,  0, "DOWN"),
    ( 0, -1, "LEFT"),
    ( 0,  1, "RIGHT"),
]

FLOWER_TYPES = ["rose", "tulip", "lily", "daisy", "orchid"]
FLOWER_COLORS = ["red", "white", "yellow", "pink", "purple"]