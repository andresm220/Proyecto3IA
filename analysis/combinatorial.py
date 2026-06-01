"""Compara nodos visitados entre Minimax puro y Alpha-Beta a profundidades 1-5."""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.game_engine import GameEngine
from src.constants import BLACK, WHITE, CORNERS, WEIGHTS

_INF = float("inf")


def _move_order_key(move: tuple[int, int]) -> float:
    r, c = move
    if (r, c) in CORNERS:
        return -10000.0
    return -float(WEIGHTS[r][c])


def minimax(engine: GameEngine, depth: int, player: int, counter: list[int]) -> float:
    counter[0] += 1
    if engine.is_terminal() or depth == 0:
        return engine.evaluate(player)
    moves = engine.get_legal_moves()
    if not moves:
        return engine.evaluate(player)
    if engine.current_player == player:
        return max(minimax(engine.clone().apply_move(m), depth - 1, player, counter) for m in moves)
    else:
        return min(minimax(engine.clone().apply_move(m), depth - 1, player, counter) for m in moves)


def alpha_beta_count(engine: GameEngine, depth: int, alpha: float, beta: float,
                     maximizing: bool, player: int, counter: list[int]) -> float:
    counter[0] += 1
    if engine.is_terminal() or depth == 0:
        return engine.evaluate(player)
    moves = engine.get_legal_moves()
    if not moves:
        return engine.evaluate(player)
    moves.sort(key=_move_order_key)
    if maximizing:
        val = -_INF
        for m in moves:
            val = max(val, alpha_beta_count(engine.clone().apply_move(m), depth - 1, alpha, beta, False, player, counter))
            alpha = max(alpha, val)
            if val >= beta:
                break
        return val
    else:
        val = _INF
        for m in moves:
            val = min(val, alpha_beta_count(engine.clone().apply_move(m), depth - 1, alpha, beta, True, player, counter))
            beta = min(beta, val)
            if val <= alpha:
                break
        return val


def run_analysis(max_depth: int = 5) -> dict:
    engine = GameEngine()
    results = {"depth": [], "minimax_nodes": [], "alphabeta_nodes": [], "b_eff_mm": [], "b_eff_ab": []}

    for depth in range(1, max_depth + 1):
        print(f"  Profundidad {depth}...")
        mm_counter = [0]
        minimax(engine.clone(), depth, BLACK, mm_counter)
        mm_nodes = mm_counter[0]

        ab_counter = [0]
        alpha_beta_count(engine.clone(), depth, -_INF, _INF, True, BLACK, ab_counter)
        ab_nodes = ab_counter[0]

        b_eff_mm = mm_nodes ** (1 / depth) if depth > 0 else 0
        b_eff_ab = ab_nodes ** (1 / depth) if depth > 0 else 0

        results["depth"].append(depth)
        results["minimax_nodes"].append(mm_nodes)
        results["alphabeta_nodes"].append(ab_nodes)
        results["b_eff_mm"].append(round(b_eff_mm, 2))
        results["b_eff_ab"].append(round(b_eff_ab, 2))

        print(f"    Minimax:   {mm_nodes:>8,} nodos | b_eff={b_eff_mm:.2f}")
        print(f"    AlphaBeta: {ab_nodes:>8,} nodos | b_eff={b_eff_ab:.2f}")

    return results


if __name__ == "__main__":
    print("=== Análisis combinatorio ===")
    data = run_analysis(max_depth=5)
    print("\n=== Tabla resumen ===")
    print(f"{'Prof':>5} | {'Minimax':>12} | {'AlphaBeta':>12} | {'b_eff MM':>8} | {'b_eff AB':>8}")
    print("-" * 60)
    for i, d in enumerate(data["depth"]):
        print(f"{d:>5} | {data['minimax_nodes'][i]:>12,} | {data['alphabeta_nodes'][i]:>12,} | "
              f"{data['b_eff_mm'][i]:>8.2f} | {data['b_eff_ab'][i]:>8.2f}")
