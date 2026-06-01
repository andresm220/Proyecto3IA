from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class BaseAgent:
    """Interfaz común para todos los agentes."""

    def __init__(self, player: int, time_limit: float = 2.0, seed: Optional[int] = None) -> None:
        self.player = player
        self.time_limit = time_limit
        self.seed = seed
        self.nodes_explored: int = 0
        self.last_move_time: float = 0.0
        self.last_value: float = 0.0

    def get_move(self, engine: "GameEngine") -> tuple[int, int]:
        """Devuelve la mejor jugada respetando time_limit."""
        raise NotImplementedError
