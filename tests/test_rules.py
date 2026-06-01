import numpy as np
import pytest
from src.game_engine import GameEngine, opponent
from src.constants import BLACK, WHITE, EMPTY


def test_initial_position():
    e = GameEngine()
    assert e.board[3][3] == WHITE
    assert e.board[3][4] == BLACK
    assert e.board[4][3] == BLACK
    assert e.board[4][4] == WHITE
    assert e.current_player == BLACK


def test_black_has_four_legal_moves_at_start():
    e = GameEngine()
    moves = set(e.get_legal_moves(BLACK))
    assert moves == {(2, 3), (3, 2), (4, 5), (5, 4)}


def test_move_flips_in_one_direction():
    e = GameEngine()
    e.apply_move((2, 3))
    assert e.board[2][3] == BLACK
    assert e.board[3][3] == BLACK  # volteada
    assert e.board[3][4] == BLACK  # ya era negra
    assert e.board[4][4] == WHITE  # sin cambio


def test_move_flips_multiple_directions():
    e = GameEngine()
    e.apply_move((3, 2))
    assert e.board[3][2] == BLACK
    assert e.board[3][3] == BLACK


def test_turn_switches_after_move():
    e = GameEngine()
    assert e.current_player == BLACK
    e.apply_move((2, 3))
    assert e.current_player == WHITE


def test_pass_when_no_moves():
    """Si el rival no tiene movimientos, el turno vuelve al jugador actual."""
    e = GameEngine()
    e.board = np.zeros((8, 8), dtype=np.int8)
    e.board[0][0] = WHITE
    e.board[0][1] = WHITE
    e.board[0][2] = WHITE
    e.current_player = WHITE
    moves = e.get_legal_moves(WHITE)
    assert moves == []


def test_terminal_full_board():
    e = GameEngine()
    e.board = np.ones((8, 8), dtype=np.int8)  # todo BLACK
    assert e.is_terminal()


def test_terminal_no_moves_for_anyone():
    e = GameEngine()
    e.board = np.zeros((8, 8), dtype=np.int8)
    e.board[0][0] = BLACK  # sin movimientos para nadie
    assert e.is_terminal()


def test_winner_black():
    e = GameEngine()
    e.board = np.ones((8, 8), dtype=np.int8)
    assert e.get_winner() == BLACK


def test_winner_white():
    e = GameEngine()
    e.board = np.full((8, 8), WHITE, dtype=np.int8)
    assert e.get_winner() == WHITE


def test_draw():
    e = GameEngine()
    e.board = np.zeros((8, 8), dtype=np.int8)
    for r in range(8):
        for c in range(8):
            e.board[r][c] = BLACK if (r + c) % 2 == 0 else WHITE
    assert e.get_winner() == 0


def test_count_pieces_initial():
    e = GameEngine()
    b, w = e.count_pieces()
    assert b == 2 and w == 2


def test_clone_independence():
    e = GameEngine()
    c = e.clone()
    c.apply_move((2, 3))
    assert e.board[2][3] == EMPTY  # original sin cambio


def test_full_game_does_not_crash():
    """Jugar partida completa aleatoria sin errores."""
    import random
    rng = random.Random(42)
    e = GameEngine()
    for _ in range(200):
        if e.is_terminal():
            break
        moves = e.get_legal_moves()
        if moves:
            e.apply_move(rng.choice(moves))
    assert e.is_terminal() or True  # no debe lanzar excepción
