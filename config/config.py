GRID_ROWS = 3
GRID_COLS = 3

WAREHOUSE_POS = (1, 2)
ROBOT_START = (0, 2)

PAVILIONS = {
    "p1": (0, 0),
    "p2": (1, 0),
    "p3": (2, 0),
}

PAVILION_NEEDS = {
    "p1": [
        ("rose", "red", 1),
        ("rose", "pink", 1),
        ("rose", "white", 1),
    ],
    "p2": [
        ("tulip", "yellow", 1),
        ("tulip", "red", 3),
    ],
    "p3": [
        ("orchid", "purple", 2),
        ("orchid", "pink", 1),
    ],
    
}

WAREHOUSE_STOCK = [
    ("rose", "red"),
    ("rose", "pink"),
    ("rose", "white"),
    ("tulip", "yellow"),
    ("tulip", "red"),
    ("lily", "white"),
    ("juliet", "gold"),
    ("juliet", "pink"),
    ("orchid", "purple"),
    ("orchid", "pink"),
]