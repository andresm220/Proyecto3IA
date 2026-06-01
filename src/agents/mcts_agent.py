from __future__ import annotations
import math
import random
import time
from typing import Optional, TYPE_CHECKING
from src.agents.base_agent import BaseAgent
from src.constants import BLACK, WHITE

if TYPE_CHECKING:
    from src.game_engine import GameEngine

_TIME_MARGIN = 0.1


class _Node:
    __slots__ = ("engine", "move", "parent", "children", "wins", "visits", "untried_moves")

    def __init__(self, engine: "GameEngine", move: Optional[tuple[int, int]], parent: Optional["_Node"]) -> None:
        self.engine = engine
        self.move = move
        self.parent = parent
        self.children: list[_Node] = []
        self.wins: float = 0.0
        self.visits: int = 0
        self.untried_moves: list[tuple[int, int]] = engine.get_legal_moves()

    def uct_score(self, C: float, parent_visits: int) -> float:
        if self.visits == 0:
            return float("inf")
        return self.wins / self.visits + C * math.sqrt(math.log(parent_visits) / self.visits)

    def best_child(self, C: float) -> "_Node":
        return max(self.children, key=lambda ch: ch.uct_score(C, self.visits))

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def is_terminal(self) -> bool:
        return self.engine.is_terminal()


class MCTSAgent(BaseAgent):

    def __init__(self, player: int, time_limit: float = 2.0, seed: Optional[int] = None,
                 C: float = 1.41, iterations: Optional[int] = None) -> None:
        super().__init__(player, time_limit, seed)
        self.C = C
        self.iterations = iterations
        self._rng = random.Random(seed)

    def get_move(self, engine: "GameEngine") -> tuple[int, int]:
        self.nodes_explored = 0
        start = time.perf_counter()
        deadline = start + self.time_limit - _TIME_MARGIN

        moves = engine.get_legal_moves(self.player)
        if not moves:
            return (-1, -1)
        if len(moves) == 1:
            return moves[0]

        root = _Node(engine.clone(), None, None)
        iters = 0

        while True:
            if self.iterations is not None:
                if iters >= self.iterations:
                    break
            else:
                if time.perf_counter() >= deadline:
                    break

            node = self._select(root)
            if not node.is_terminal() and not node.is_fully_expanded():
                node = self._expand(node)
            result = self._simulate(node.engine)
            self._backpropagate(node, result)
            iters += 1
            self.nodes_explored += 1

        if not root.children:
            best_move = self._rng.choice(moves)
        else:
            best_child = max(root.children, key=lambda ch: ch.visits)
            best_move = best_child.move  # type: ignore[assignment]

        self.last_move_time = time.perf_counter() - start
        self.last_value = 0.0
        if root.children:
            best = max(root.children, key=lambda ch: ch.visits)
            self.last_value = best.wins / best.visits if best.visits > 0 else 0.0

        return best_move

    def _select(self, node: _Node) -> _Node:
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            node = node.best_child(self.C)
        return node

    def _expand(self, node: _Node) -> _Node:
        move = self._rng.choice(node.untried_moves)
        node.untried_moves.remove(move)
        child_engine = node.engine.clone()
        child_engine.apply_move(move)
        child = _Node(child_engine, move, node)
        node.children.append(child)
        return child

    def _simulate(self, engine: "GameEngine") -> float:
        """Rollout aleatorio hasta el final. Devuelve 1.0 si gana self.player, 0.5 empate, 0.0 derrota."""
        sim = engine.clone()
        for _ in range(200):
            if sim.is_terminal():
                break
            moves = sim.get_legal_moves()
            if moves:
                sim.apply_move(self._rng.choice(moves))
        winner = sim.get_winner()
        if winner == self.player:
            return 1.0
        if winner == 0:
            return 0.5
        return 0.0

    def _backpropagate(self, node: Optional[_Node], result: float) -> None:
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
