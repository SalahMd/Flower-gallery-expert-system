GRID_ROWS = 5
GRID_COLS = 5

WAREHOUSE_POS = (1, 2)

ROBOT_START = (0, 2)

PAVILIONS = {
    "p1": (3, 1),
    "p2": (2, 3),
    "p3": (4, 3),
    "p4": (1, 4),

}

PAVILION_NEEDS = {
    "p1": [
        ("rose", "red", 1),
        ("rose", "pink", 1),
        ("rose", "white", 1),
    ],
    "p2": [
        ("tulip", "yellow", 1,),
        ("tulip", "red", 3,),
    ],
    "p3": [
        ("orchid", "purple", 2),
        ("orchid", "pink", 1),
    ],
    "p4": [
        ("juliet", "gold", 2),
        ("juliet", "pink", 2),
    ]
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
    ('orchid', 'purple'),
    ('orchid', 'pink'),
]
