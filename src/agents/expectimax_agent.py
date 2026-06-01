from __future__ import annotations
import time
from typing import TYPE_CHECKING
from src.agents.base_agent import BaseAgent
from src.constants import CORNERS, WEIGHTS

if TYPE_CHECKING:
    from src.game_engine import GameEngine

_INF = float("inf")
_TIME_MARGIN = 0.1


def _move_order_key(move: tuple[int, int]) -> float:
    r, c = move
    if (r, c) in CORNERS:
        return -10000.0
    return -float(WEIGHTS[r][c])


class ExpectimaxAgent(BaseAgent):
    """Oponente modelado como jugador aleatorio uniforme (nodo de azar)."""

    def get_move(self, engine: "GameEngine") -> tuple[int, int]:
        self.nodes_explored = 0
        start = time.perf_counter()
        deadline = start + self.time_limit - _TIME_MARGIN

        moves = engine.get_legal_moves(self.player)
        if not moves:
            return (-1, -1)
        if len(moves) == 1:
            return moves[0]

        best_move = moves[0]
        best_val = -_INF
        depth = 1

        while True:
            if time.perf_counter() >= deadline:
                break
            try:
                val, mv = self._search_root(engine, depth, deadline)
                best_val = val
                best_move = mv
            except _TimeOut:
                break
            depth += 1

        self.last_move_time = time.perf_counter() - start
        self.last_value = best_val
        return best_move

    def _search_root(self, engine: "GameEngine", depth: int, deadline: float) -> tuple[float, tuple[int, int]]:
        moves = engine.get_legal_moves(self.player)
        moves.sort(key=_move_order_key)
        best_move = moves[0]
        best_val = -_INF
        for move in moves:
            if time.perf_counter() >= deadline:
                raise _TimeOut()
            child = engine.clone()
            child.apply_move(move)
            val = self.expectimax(child, depth - 1, deadline)
            if val > best_val:
                best_val = val
                best_move = move
        return best_val, best_move

    def expectimax(self, engine: "GameEngine", depth: int, deadline: float) -> float:
        """Nodo max para self.player, nodo de azar (promedio uniforme) para el oponente."""
        if time.perf_counter() >= deadline:
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

        if engine.current_player == self.player:
            best = -_INF
            for move in moves:
                child = engine.clone()
                child.apply_move(move)
                best = max(best, self.expectimax(child, depth - 1, deadline))
            return best
        else:
            total = 0.0
            for move in moves:
                child = engine.clone()
                child.apply_move(move)
                total += self.expectimax(child, depth - 1, deadline)
            return total / len(moves)


class _TimeOut(Exception):
    pass
