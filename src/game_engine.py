from __future__ import annotations
from typing import Optional
import numpy as np
from src.constants import EMPTY, BLACK, WHITE, BOARD_SIZE, DIRECTIONS


def opponent(player: int) -> int:
    return WHITE if player == BLACK else BLACK


class GameEngine:
    def __init__(self) -> None:
        self.board: np.ndarray = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        self.board[3][3] = WHITE
        self.board[3][4] = BLACK
        self.board[4][3] = BLACK
        self.board[4][4] = WHITE
        self.current_player: int = BLACK

    def _flips(self, row: int, col: int, player: int, opp: int) -> list[tuple[int, int]]:
        """Fichas que se voltearían al jugar (row, col) como player."""
        flipped: list[tuple[int, int]] = []
        for dr, dc in DIRECTIONS:
            candidates: list[tuple[int, int]] = []
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == opp:
                candidates.append((r, c))
                r += dr
                c += dc
            if candidates and 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == player:
                flipped.extend(candidates)
        return flipped

    def get_legal_moves(self, player: Optional[int] = None) -> list[tuple[int, int]]:
        """Movimientos válidos del jugador dado (por defecto current_player)."""
        if player is None:
            player = self.current_player
        opp = opponent(player)
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == EMPTY and self._flips(r, c, player, opp):
                    moves.append((r, c))
        return moves

    def is_legal_move(self, move: tuple[int, int], player: Optional[int] = None) -> bool:
        if player is None:
            player = self.current_player
        r, c = move
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return False
        if self.board[r][c] != EMPTY:
            return False
        return bool(self._flips(r, c, player, opponent(player)))

    def apply_move(self, move: tuple[int, int]) -> GameEngine:
        """Aplica el movimiento, voltea fichas y cambia de turno.
        Gestiona el pase automático si el rival no tiene jugadas."""
        player = self.current_player
        opp = opponent(player)
        r, c = move
        self.board[r][c] = player
        for fr, fc in self._flips(r, c, player, opp):
            self.board[fr][fc] = player
        self.current_player = opp
        if not self.get_legal_moves(opp):
            self.current_player = player
        return self

    def clone(self) -> GameEngine:
        """Copia profunda barata del estado."""
        new: GameEngine = GameEngine.__new__(GameEngine)
        new.board = self.board.copy()
        new.current_player = self.current_player
        return new

    def is_terminal(self) -> bool:
        if not self.get_legal_moves(BLACK) and not self.get_legal_moves(WHITE):
            return True
        return int(np.sum(self.board != EMPTY)) == BOARD_SIZE * BOARD_SIZE

    def get_winner(self) -> int:
        """BLACK, WHITE o 0 (empate). Solo válido en estado terminal."""
        b, w = self.count_pieces()
        if b > w:
            return BLACK
        if w > b:
            return WHITE
        return 0

    def count_pieces(self) -> tuple[int, int]:
        """(negras, blancas)."""
        b = int(np.sum(self.board == BLACK))
        w = int(np.sum(self.board == WHITE))
        return b, w

    def evaluate(self, player: int) -> float:
        """Heurística delegada a heuristics.py."""
        from src.heuristics import combined_evaluate
        return combined_evaluate(self, player)
