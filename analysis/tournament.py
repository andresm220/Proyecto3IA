"""Torneo 20 partidas AlphaBeta vs MCTS con límite de 2s/jugada."""
from __future__ import annotations
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.game_engine import GameEngine
from src.constants import BLACK, WHITE
from src.agents.alphabeta_agent import AlphaBetaAgent
from src.agents.mcts_agent import MCTSAgent


def play_game(black_agent, white_agent, game_num: int) -> dict:
    engine = GameEngine()
    move_times = {BLACK: [], WHITE: []}
    move_count = 0

    while not engine.is_terminal():
        agent = black_agent if engine.current_player == BLACK else white_agent
        moves = engine.get_legal_moves()
        if not moves:
            break
        t0 = time.perf_counter()
        move = agent.get_move(engine.clone())
        elapsed = time.perf_counter() - t0
        move_times[engine.current_player].append(elapsed)

        if move and move != (-1, -1):
            engine.apply_move(move)
        move_count += 1

        if move_count > 200:  # safety
            break

    winner = engine.get_winner()
    b, w = engine.count_pieces()
    print(f"  Partida {game_num:>2}: {'Negras' if winner==BLACK else 'Blancas' if winner==WHITE else 'Empate':>7} | "
          f"N{b} B{w} | "
          f"t_negro={sum(move_times[BLACK])/max(len(move_times[BLACK]),1):.2f}s "
          f"t_blanco={sum(move_times[WHITE])/max(len(move_times[WHITE]),1):.2f}s")
    return {
        "winner": winner,
        "black_pieces": b,
        "white_pieces": w,
        "black_avg_time": sum(move_times[BLACK]) / max(len(move_times[BLACK]), 1),
        "white_avg_time": sum(move_times[WHITE]) / max(len(move_times[WHITE]), 1),
    }


def run_tournament(n_games: int = 20) -> dict:
    results = []
    ab_wins = mcts_wins = draws = 0

    for i in range(n_games):
        if i % 2 == 0:
            ab_agent = AlphaBetaAgent(BLACK, time_limit=2.0)
            mcts_agent = MCTSAgent(WHITE, time_limit=2.0, seed=i)
            r = play_game(ab_agent, mcts_agent, i + 1)
            if r["winner"] == BLACK:
                ab_wins += 1
            elif r["winner"] == WHITE:
                mcts_wins += 1
            else:
                draws += 1
            r["ab_color"] = "black"
        else:
            mcts_agent = MCTSAgent(BLACK, time_limit=2.0, seed=i)
            ab_agent = AlphaBetaAgent(WHITE, time_limit=2.0)
            r = play_game(mcts_agent, ab_agent, i + 1)
            if r["winner"] == WHITE:
                ab_wins += 1
            elif r["winner"] == BLACK:
                mcts_wins += 1
            else:
                draws += 1
            r["ab_color"] = "white"
        results.append(r)

    return {
        "results": results,
        "ab_wins": ab_wins,
        "mcts_wins": mcts_wins,
        "draws": draws,
        "n_games": n_games,
    }


if __name__ == "__main__":
    print("=== Torneo AlphaBeta vs MCTS (20 partidas) ===\n")
    data = run_tournament(20)
    print(f"\n=== Resultado final ===")
    print(f"AlphaBeta: {data['ab_wins']} victorias")
    print(f"MCTS:      {data['mcts_wins']} victorias")
    print(f"Empates:   {data['draws']}")

    import json
    with open("analysis/tournament_results.json", "w") as f:
        summary = {k: v for k, v in data.items() if k != "results"}
        json.dump(summary, f, indent=2)
    print("Resultados guardados en analysis/tournament_results.json")
