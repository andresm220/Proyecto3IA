from __future__ import annotations
import threading
import time
from typing import Optional, TYPE_CHECKING
import pygame
from src.constants import BLACK, WHITE, EMPTY, BOARD_SIZE

if TYPE_CHECKING:
    from src.game_engine import GameEngine
    from src.agents.base_agent import BaseAgent
    from src.agents.human_agent import HumanAgent

# ── Colores (tema minimalista claro) ─────────────────────────────────
BG_COLOR       = (245, 245, 240)
BOARD_COLOR    = (212, 237, 218)
LINE_COLOR     = (150, 180, 160)
BLACK_PIECE    = (30,  30,  30)
WHITE_PIECE    = (248, 248, 248)
WHITE_BORDER   = (180, 180, 180)
HINT_COLOR     = (100, 160, 120, 120)
LAST_MOVE_COLOR= (255, 200, 0)
PANEL_BG       = (230, 230, 225)
TEXT_COLOR     = (50,  50,  50)
ACCENT_COLOR   = (60,  140,  80)

CELL  = 70
BOARD_PX = CELL * BOARD_SIZE
MARGIN = 30
PANEL_W = 220
WIN_W = MARGIN + BOARD_PX + MARGIN + PANEL_W + MARGIN
WIN_H = MARGIN + BOARD_PX + MARGIN


class GameVisualizer:
    def __init__(
        self,
        engine: "GameEngine",
        black_agent: "BaseAgent",
        white_agent: "BaseAgent",
    ) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Othello IA")
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 16)
        self.font_sm = pygame.font.SysFont("Arial", 13)

        self.engine = engine
        self.black_agent = black_agent
        self.white_agent = white_agent

        self._ai_thread: Optional[threading.Thread] = None
        self._ai_move: Optional[tuple[int, int]] = None
        self._ai_thinking = False
        self._last_move: Optional[tuple[int, int]] = None
        self._message = ""
        self._game_over = False

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if not self._game_over:
                    self._handle_event(event)

            self._apply_ai_move_if_ready()
            self._tick()
            self._draw()
            self.clock.tick(30)

    def _handle_event(self, event: pygame.event.Event) -> None:
        from src.agents.human_agent import HumanAgent
        current_agent = self.black_agent if self.engine.current_player == BLACK else self.white_agent
        if isinstance(current_agent, HumanAgent) and not self._ai_thinking:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                col = (mx - MARGIN) // CELL
                row = (my - MARGIN) // CELL
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    move = (row, col)
                    if self.engine.is_legal_move(move):
                        current_agent.set_move(move)
                        self._apply_human_move(current_agent)

    def _apply_human_move(self, agent: "HumanAgent") -> None:
        move = agent.get_move(self.engine)
        if move:
            self.engine.apply_move(move)
            self._last_move = move
            self._check_game_over()

    def _tick(self) -> None:
        from src.agents.human_agent import HumanAgent
        if self._game_over or self._ai_thinking or self._ai_move is not None:
            return
        current_agent = self.black_agent if self.engine.current_player == BLACK else self.white_agent
        if isinstance(current_agent, HumanAgent):
            return
        self._ai_thinking = True
        self._ai_thread = threading.Thread(target=self._run_ai, args=(current_agent,), daemon=True)
        self._ai_thread.start()

    def _run_ai(self, agent: "BaseAgent") -> None:
        engine_copy = self.engine.clone()
        move = agent.get_move(engine_copy)
        self._ai_move = move
        self._ai_thinking = False

    def _draw(self) -> None:
        self.screen.fill(BG_COLOR)
        legal_moves = set(self.engine.get_legal_moves()) if not self._game_over else set()
        self._draw_board(legal_moves)
        self._draw_panel()
        pygame.display.flip()

    def _apply_ai_move_if_ready(self) -> None:
        if self._ai_move is not None and not self._ai_thinking:
            move = self._ai_move
            self._ai_move = None
            if move and move != (-1, -1):
                self.engine.apply_move(move)
                self._last_move = move
                self._check_game_over()

    def _check_game_over(self) -> None:
        if self.engine.is_terminal():
            self._game_over = True
            winner = self.engine.get_winner()
            if winner == BLACK:
                self._message = "¡Ganan las NEGRAS!"
            elif winner == WHITE:
                self._message = "¡Ganan las BLANCAS!"
            else:
                self._message = "¡Empate!"
        else:
            moves = self.engine.get_legal_moves()
            if not moves:
                self._message = "Pase de turno"
            else:
                self._message = ""

    def _draw_board(self, legal_moves: set) -> None:
        ox, oy = MARGIN, MARGIN
        pygame.draw.rect(self.screen, BOARD_COLOR, (ox, oy, BOARD_PX, BOARD_PX))
        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(self.screen, LINE_COLOR, (ox + i * CELL, oy), (ox + i * CELL, oy + BOARD_PX), 1)
            pygame.draw.line(self.screen, LINE_COLOR, (ox, oy + i * CELL), (ox + BOARD_PX, oy + i * CELL), 1)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cx = ox + c * CELL + CELL // 2
                cy = oy + r * CELL + CELL // 2
                if self._last_move == (r, c):
                    pygame.draw.rect(self.screen, LAST_MOVE_COLOR,
                                     (ox + c * CELL + 1, oy + r * CELL + 1, CELL - 2, CELL - 2))
                piece = self.engine.board[r][c]
                if piece == BLACK:
                    pygame.draw.circle(self.screen, BLACK_PIECE, (cx, cy), CELL // 2 - 5)
                elif piece == WHITE:
                    pygame.draw.circle(self.screen, WHITE_PIECE, (cx, cy), CELL // 2 - 5)
                    pygame.draw.circle(self.screen, WHITE_BORDER, (cx, cy), CELL // 2 - 5, 2)
                elif (r, c) in legal_moves:
                    surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                    pygame.draw.circle(surf, HINT_COLOR, (CELL // 2, CELL // 2), CELL // 6)
                    self.screen.blit(surf, (ox + c * CELL, oy + r * CELL))

        if self._message:
            txt = self.font_lg.render(self._message, True, ACCENT_COLOR)
            self.screen.blit(txt, (ox + BOARD_PX // 2 - txt.get_width() // 2, oy + BOARD_PX + 5))

    def _draw_panel(self) -> None:
        px = MARGIN + BOARD_PX + MARGIN
        py = MARGIN
        pw = PANEL_W
        ph = BOARD_PX
        pygame.draw.rect(self.screen, PANEL_BG, (px, py, pw, ph), border_radius=8)

        b, w = self.engine.count_pieces()
        player_name = "NEGRAS" if self.engine.current_player == BLACK else "BLANCAS"
        current_agent = self.black_agent if self.engine.current_player == BLACK else self.white_agent

        rows = [
            ("Turno", player_name),
            ("", ""),
            ("Negras", str(b)),
            ("Blancas", str(w)),
            ("", ""),
        ]

        from src.agents.human_agent import HumanAgent
        if not isinstance(current_agent, HumanAgent):
            rows += [
                ("Nodos", f"{current_agent.nodes_explored:,}"),
                ("Tiempo", f"{current_agent.last_move_time:.2f}s"),
                ("Valor", f"{current_agent.last_value:.1f}"),
            ]
        else:
            rows += [("Modo", "Humano"), ("", ""), ("", "")]

        y = py + 15
        for label, value in rows:
            if label:
                lbl = self.font_sm.render(label, True, TEXT_COLOR)
                val = self.font_md.render(value, True, ACCENT_COLOR if label == "Turno" else TEXT_COLOR)
                self.screen.blit(lbl, (px + 10, y))
                self.screen.blit(val, (px + pw - val.get_width() - 10, y))
            y += 22

        if self._ai_thinking:
            thinking = self.font_sm.render("IA pensando...", True, ACCENT_COLOR)
            self.screen.blit(thinking, (px + 10, py + ph - 30))
