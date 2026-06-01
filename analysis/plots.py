"""Genera gráficas de rendimiento para el reporte."""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import matplotlib
matplotlib.use("Agg")  # sin ventana de display
import matplotlib.pyplot as plt


def plot_combinatorial(data: dict, output_path: str = "analysis/combinatorial.png") -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(data["depth"], data["minimax_nodes"], "o-", label="Minimax puro", color="#e74c3c")
    ax1.plot(data["depth"], data["alphabeta_nodes"], "s-", label="Alpha-Beta", color="#2ecc71")
    ax1.set_yscale("log")
    ax1.set_xlabel("Profundidad")
    ax1.set_ylabel("Nodos explorados (log)")
    ax1.set_title("Explosión combinatoria: Minimax vs Alpha-Beta")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(data["depth"])

    ax2.plot(data["depth"], data["b_eff_mm"], "o-", label="b_eff Minimax", color="#e74c3c")
    ax2.plot(data["depth"], data["b_eff_ab"], "s-", label="b_eff Alpha-Beta", color="#2ecc71")
    ax2.set_xlabel("Profundidad")
    ax2.set_ylabel("Factor de ramificación efectivo")
    ax2.set_title("Factor de ramificación efectivo (b_eff)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(data["depth"])

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Guardado: {output_path}")
    plt.close()


def plot_tournament(data: dict, output_path: str = "analysis/tournament.png") -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Alpha-Beta", "MCTS", "Empates"]
    values = [data["ab_wins"], data["mcts_wins"], data["draws"]]
    colors = ["#3498db", "#e67e22", "#95a5a6"]
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=1.5)
    ax.set_title(f"Torneo IA vs IA ({data['n_games']} partidas)")
    ax.set_ylabel("Número de partidas")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                str(val), ha="center", va="bottom", fontweight="bold")
    ax.set_ylim(0, data["n_games"] + 2)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Guardado: {output_path}")
    plt.close()


if __name__ == "__main__":
    from analysis.combinatorial import run_analysis
    from analysis.tournament import run_tournament

    print("Generando gráfica combinatoria...")
    comb_data = run_analysis(max_depth=5)
    plot_combinatorial(comb_data)

    print("\nGenerando gráfica de torneo (esto puede tardar varios minutos)...")
    tourn_data = run_tournament(n_games=20)
    plot_tournament(tourn_data)

    print("\nGráficas guardadas en analysis/")
