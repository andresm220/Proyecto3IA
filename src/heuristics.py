from __future__ import annotations
from typing import TYPE_CHECKING
from src.constants import (
    BLACK, WHITE, EMPTY, BOARD_SIZE, WEIGHTS,
    CORNERS, X_SQUARES, C_SQUARES, CORNER_NEIGHBORS,
)

if TYPE_CHECKING:
    from src.game_engine import GameEngine


def opponent(player: int) -> int:
    return WHITE if player == BLACK else BLACK


def coin_parity(engine: "GameEngine", player: int) -> float:
    """Paridad de fichas normalizada a [-100, 100]."""
    b, w = engine.count_pieces()
    mine = b if player == BLACK else w
    opp_count = w if player == BLACK else b
    total = mine + opp_count
    if total == 0:
        return 0.0
    return 100.0 * (mine - opp_count) / total


def mobility(engine: "GameEngine", player: int) -> float:
    """Diferencia de movilidad normalizada a [-100, 100]."""
    my_moves = len(engine.get_legal_moves(player))
    opp_moves = len(engine.get_legal_moves(opponent(player)))
    total = my_moves + opp_moves
    if total == 0:
        return 0.0
    return 100.0 * (my_moves - opp_moves) / total


def corner_control(engine: "GameEngine", player: int) -> float:
    """Valor de las esquinas capturadas [-100, 100]."""
    my_corners = sum(1 for r, c in CORNERS if engine.board[r][c] == player)
    opp_corners = sum(1 for r, c in CORNERS if engine.board[r][c] == opponent(player))
    total = my_corners + opp_corners
    if total == 0:
        return 0.0
    return 100.0 * (my_corners - opp_corners) / total


def corner_proximity(engine: "GameEngine", player: int) -> float:
    """Penalización por fichas en X/C-squares adyacentes a esquinas vacías."""
    opp = opponent(player)
    my_penalty = 0
    opp_penalty = 0
    for sq in X_SQUARES + C_SQUARES:
        corner = CORNER_NEIGHBORS.get(sq)
        if corner and engine.board[corner[0]][corner[1]] == EMPTY:
            r, c = sq
            if engine.board[r][c] == player:
                my_penalty += 1
            elif engine.board[r][c] == opp:
                opp_penalty += 1
    total = my_penalty + opp_penalty
    if total == 0:
        return 0.0
    return -100.0 * (my_penalty - opp_penalty) / total


def stability(engine: "GameEngine", player: int) -> float:
    """Aproximación de estabilidad: fichas en bordes ancladas a esquinas."""
    opp = opponent(player)
    my_stable = _count_stable(engine, player)
    opp_stable = _count_stable(engine, opp)
    total = my_stable + opp_stable
    if total == 0:
        return 0.0
    return 100.0 * (my_stable - opp_stable) / total


def _count_stable(engine: "GameEngine", player: int) -> int:
    """Cuenta fichas de player que no pueden voltearse (bordes + esquinas)."""
    stable = 0
    board = engine.board
    for r, c in CORNERS:
        if board[r][c] == player:
            stable += 1
    for c in range(BOARD_SIZE):
        if board[0][c] == player and all(board[0][cc] != EMPTY for cc in range(c + 1)):
            stable += 1
        if board[7][c] == player and all(board[7][cc] != EMPTY for cc in range(c + 1)):
            stable += 1
    for r in range(BOARD_SIZE):
        if board[r][0] == player and all(board[rr][0] != EMPTY for rr in range(r + 1)):
            stable += 1
        if board[r][7] == player and all(board[rr][7] != EMPTY for rr in range(r + 1)):
            stable += 1
    return stable


def positional_weight(engine: "GameEngine", player: int) -> float:
    """Suma de WEIGHTS para fichas propias menos rival, normalizada a [-100, 100]."""
    opp = opponent(player)
    my_score = sum(
        WEIGHTS[r][c]
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if engine.board[r][c] == player
    )
    opp_score = sum(
        WEIGHTS[r][c]
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if engine.board[r][c] == opp
    )
    max_possible = sum(abs(WEIGHTS[r][c]) for r in range(8) for c in range(8))
    if max_possible == 0:
        return 0.0
    return 100.0 * (my_score - opp_score) / max_possible


def detect_phase(engine: "GameEngine") -> str:
    """Detecta la fase del juego según el número de fichas en el tablero."""
    import numpy as np
    total = int((engine.board != EMPTY).sum())
    if total < 20:
        return "opening"
    if total < 54:
        return "midgame"
    return "endgame"


_PHASE_WEIGHTS: dict[str, dict[str, float]] = {
    "opening": {
        "parity": 0.00,
        "mobility": 0.40,
        "corners": 0.25,
        "proximity": 0.15,
        "stability": 0.10,
        "positional": 0.10,
    },
    "midgame": {
        "parity": 0.10,
        "mobility": 0.25,
        "corners": 0.30,
        "proximity": 0.10,
        "stability": 0.15,
        "positional": 0.10,
    },
    "endgame": {
        "parity": 0.50,
        "mobility": 0.05,
        "corners": 0.25,
        "proximity": 0.05,
        "stability": 0.10,
        "positional": 0.05,
    },
}


def combined_evaluate(engine: "GameEngine", player: int) -> float:
    """Combinación lineal ponderada de los 6 componentes según la fase."""
    phase = detect_phase(engine)
    w = _PHASE_WEIGHTS[phase]
    score = (
        w["parity"]     * coin_parity(engine, player)
        + w["mobility"]   * mobility(engine, player)
        + w["corners"]    * corner_control(engine, player)
        + w["proximity"]  * corner_proximity(engine, player)
        + w["stability"]  * stability(engine, player)
        + w["positional"] * positional_weight(engine, player)
    )
    return score
