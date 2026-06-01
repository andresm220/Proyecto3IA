from typing import Final

EMPTY: Final[int] = 0
BLACK: Final[int] = 1
WHITE: Final[int] = 2

BOARD_SIZE: Final[int] = 8

DIRECTIONS: Final[list[tuple[int, int]]] = [
    (-1, -1), (-1, 0), (-1, 1),
    (0,  -1),           (0,  1),
    (1,  -1), (1,  0), (1,  1),
]

WEIGHTS: Final[list[list[int]]] = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120],
]

CORNERS: Final[list[tuple[int, int]]] = [(0, 0), (0, 7), (7, 0), (7, 7)]

X_SQUARES: Final[list[tuple[int, int]]] = [(1, 1), (1, 6), (6, 1), (6, 6)]

C_SQUARES: Final[list[tuple[int, int]]] = [
    (0, 1), (1, 0),
    (0, 6), (1, 7),
    (6, 0), (7, 1),
    (6, 7), (7, 6),
]

# Mapea cada X/C-square a la esquina que protege
CORNER_NEIGHBORS: Final[dict[tuple[int, int], tuple[int, int]]] = {
    (0, 1): (0, 0), (1, 0): (0, 0), (1, 1): (0, 0),
    (0, 6): (0, 7), (1, 7): (0, 7), (1, 6): (0, 7),
    (6, 0): (7, 0), (7, 1): (7, 0), (6, 1): (7, 0),
    (6, 7): (7, 7), (7, 6): (7, 7), (6, 6): (7, 7),
}
