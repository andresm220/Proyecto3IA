from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from src.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class HumanAgent(BaseAgent):
    """Agente humano: devuelve la jugada recibida desde la GUI."""

    def __init__(self, player: int) -> None:
        super().__init__(player)
        self._pending_move: Optional[tuple[int, int]] = None

    def set_move(self, move: tuple[int, int]) -> None:
        """La GUI llama a este método cuando el humano hace clic."""
        self._pending_move = move

    def get_move(self, engine: "GameEngine") -> tuple[int, int]:
        """Devuelve la jugada pendiente (debe haber sido seteada por set_move)."""
        move = self._pending_move
        self._pending_move = None
        return move  # type: ignore[return-value]
