import sys
import pygame
from src.game_engine import GameEngine
from src.constants import BLACK, WHITE
from src.agents.human_agent import HumanAgent
from src.agents.alphabeta_agent import AlphaBetaAgent
from src.agents.mcts_agent import MCTSAgent
from src.agents.expectimax_agent import ExpectimaxAgent
from src.agents.base_agent import BaseAgent

BG    = (245, 245, 240)
BOARD = (212, 237, 218)
LINE  = (150, 180, 160)
ACCENT= (60, 140, 80)
TEXT  = (50, 50, 50)


def _make_ai(player: int, algo: str) -> BaseAgent:
    if algo == "alphabeta":
        return AlphaBetaAgent(player, time_limit=2.0)
    if algo == "mcts":
        return MCTSAgent(player, time_limit=2.0)
    return ExpectimaxAgent(player, time_limit=2.0)


def choose_mode() -> tuple[BaseAgent, BaseAgent]:
    pygame.init()
    screen = pygame.display.set_mode((520, 480))
    pygame.display.set_caption("Othello IA — Menú")
    font_title = pygame.font.SysFont("Arial", 32, bold=True)
    font_opt   = pygame.font.SysFont("Arial", 19)
    font_sm    = pygame.font.SysFont("Arial", 14)
    clock = pygame.time.Clock()

    mode_options = [
        ("Humano vs Humano",  "hvh"),
        ("Humano vs IA",      "hvai"),
        ("IA vs IA",          "aivai"),
    ]
    algo_options = [
        ("Alpha-Beta", "alphabeta"),
        ("MCTS",       "mcts"),
        ("Expectimax", "expectimax"),
    ]

    selected_mode = None
    selected_algo = "alphabeta"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, (_, key) in enumerate(mode_options):
                    rect = pygame.Rect(60, 110 + i * 56, 400, 44)
                    if rect.collidepoint(mx, my):
                        selected_mode = key
                for i, (_, key) in enumerate(algo_options):
                    rect = pygame.Rect(60 + i * 155, 300, 145, 36)
                    if rect.collidepoint(mx, my):
                        selected_algo = key
                start_rect = pygame.Rect(160, 390, 200, 44)
                if start_rect.collidepoint(mx, my) and selected_mode:
                    return _build_agents(selected_mode, selected_algo)

        screen.fill(BG)
        title = font_title.render("Othello IA", True, TEXT)
        screen.blit(title, (520 // 2 - title.get_width() // 2, 30))

        screen.blit(font_sm.render("MODO DE JUEGO", True, ACCENT), (60, 88))
        for i, (label, key) in enumerate(mode_options):
            rect = pygame.Rect(60, 110 + i * 56, 400, 44)
            color = (180, 220, 190) if selected_mode == key else BOARD
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, LINE, rect, 2, border_radius=6)
            screen.blit(font_opt.render(label, True, TEXT), (rect.x + 12, rect.y + 11))

        screen.blit(font_sm.render("ALGORITMO IA", True, ACCENT), (60, 278))
        for i, (label, key) in enumerate(algo_options):
            rect = pygame.Rect(60 + i * 155, 300, 145, 36)
            color = (180, 220, 190) if selected_algo == key else BOARD
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, LINE, rect, 2, border_radius=6)
            screen.blit(font_sm.render(label, True, TEXT), (rect.x + 8, rect.y + 9))

        if selected_mode:
            start_rect = pygame.Rect(160, 390, 200, 44)
            pygame.draw.rect(screen, ACCENT, start_rect, border_radius=8)
            lbl = font_opt.render("Iniciar", True, (255, 255, 255))
            screen.blit(lbl, (start_rect.x + start_rect.width // 2 - lbl.get_width() // 2,
                               start_rect.y + 12))

        pygame.display.flip()
        clock.tick(30)


def _build_agents(mode: str, algo: str) -> tuple[BaseAgent, BaseAgent]:
    if mode == "hvh":
        return HumanAgent(BLACK), HumanAgent(WHITE)
    if mode == "hvai":
        return HumanAgent(BLACK), _make_ai(WHITE, algo)
    return _make_ai(BLACK, algo), _make_ai(WHITE, algo)


def main() -> None:
    black_agent, white_agent = choose_mode()
    engine = GameEngine()
    from src.visualizer import GameVisualizer
    viz = GameVisualizer(engine, black_agent, white_agent)
    viz.run()


if __name__ == "__main__":
    main()
