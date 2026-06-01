from __future__ import annotations
import time
from typing import TYPE_CHECKING, Optional
from src.agents.base_agent import BaseAgent
from src.constants import BLACK, WHITE, WEIGHTS, CORNERS, BOARD_SIZE

if TYPE_CHECKING:
    from src.game_engine import GameEngine

_INF = float("inf")
_TIME_MARGIN = 0.1  # segundos de margen de seguridad


def _move_order_key(engine: "GameEngine", move: tuple[int, int]) -> float:
    """Ordena: esquinas primero, luego por peso posicional decreciente."""
    r, c = move
    if (r, c) in CORNERS:
        return -10000.0
    return -float(WEIGHTS[r][c])


class AlphaBetaAgent(BaseAgent):

    def get_move(self, engine: "GameEngine") -> tuple[int, int]:
        import time as _time
        self.nodes_explored = 0
        start = _time.perf_counter()
        deadline = start + self.time_limit - _TIME_MARGIN

        moves = engine.get_legal_moves(self.player)
        if not moves:
            return (-1, -1)
        if len(moves) == 1:
            return moves[0]

        best_move = moves[0]
        best_value = -_INF

        # Iterative deepening
        depth = 1
        while True:
            if _time.perf_counter() >= deadline:
                break
            try:
                val, mv = self._search_root(engine, depth, deadline)
                best_value = val
                best_move = mv
            except _TimeOut:
                break
            depth += 1

        self.last_move_time = _time.perf_counter() - start
        self.last_value = best_value
        return best_move

    def _search_root(
        self, engine: "GameEngine", depth: int, deadline: float
    ) -> tuple[float, tuple[int, int]]:
        import time as _time
        moves = engine.get_legal_moves(self.player)
        moves.sort(key=lambda m: _move_order_key(engine, m))
        best_move = moves[0]
        best_val = -_INF
        alpha = -_INF
        for move in moves:
            if _time.perf_counter() >= deadline:
                raise _TimeOut()
            child = engine.clone()
            child.apply_move(move)
            val = self._alpha_beta(child, depth - 1, alpha, _INF, False, deadline)
            if val > best_val:
                best_val = val
                best_move = move
            alpha = max(alpha, best_val)
        return best_val, best_move

    def _alpha_beta(
        self,
        engine: "GameEngine",
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
        deadline: float,
    ) -> float:
        import time as _time
        if _time.perf_counter() >= deadline:
            raise _TimeOut()
        self.nodes_explored += 1

        if engine.is_terminal():
            winner = engine.get_winner()
            if winner == self.player:
                return 10000.0
            if winner == 0:
                return 0.0
            return -10000.0

        moves = engine.get_legal_moves()
        if depth == 0 or not moves:
            return engine.evaluate(self.player)

        moves.sort(key=lambda m: _move_order_key(engine, m))

        if maximizing:
            val = -_INF
            for move in moves:
                child = engine.clone()
                child.apply_move(move)
                val = max(val, self._alpha_beta(child, depth - 1, alpha, beta, False, deadline))
                alpha = max(alpha, val)
                if val >= beta:
                    break
            return val
        else:
            val = _INF
            for move in moves:
                child = engine.clone()
                child.apply_move(move)
                val = min(val, self._alpha_beta(child, depth - 1, alpha, beta, True, deadline))
                beta = min(beta, val)
                if val <= alpha:
                    break
            return val


class _TimeOut(Exception):
    pass
