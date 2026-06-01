# Othello IA — Proyecto 3 IA 2026

Implementación de Othello (Reversi) con agentes inteligentes: Alpha-Beta, Expectimax y MCTS.

## Requisitos

```bash
pip install pygame numpy matplotlib pytest
```

## Ejecutar el juego

```bash
python main.py
```

Selecciona el modo de juego en el menú:
- **Humano vs Humano** — dos jugadores en el mismo teclado/ratón
- **Humano vs IA** — tú juegas como Negras, la IA como Blancas
- **IA vs IA** — la partida avanza automáticamente

Elige el algoritmo IA: Alpha-Beta, MCTS o Expectimax.

## Tests de reglas

```bash
pytest tests/test_rules.py -v
```

## Análisis de rendimiento

### Explosión combinatoria (Minimax vs Alpha-Beta)

```bash
python analysis/combinatorial.py
```

Genera tabla de nodos explorados y factor de ramificación efectivo (b_eff) para profundidades 1–5.

### Torneo IA vs IA (20 partidas)

```bash
python analysis/tournament.py
```

Genera `analysis/tournament_results.json` con victorias, derrotas y empates.

### Generar todas las gráficas

```bash
python analysis/plots.py
```

Genera `analysis/combinatorial.png` y `analysis/tournament.png`.

## Estructura

```
othello-ai/
├── main.py                  # Punto de entrada + menú
├── src/
│   ├── constants.py         # Constantes y matriz de pesos
│   ├── game_engine.py       # Motor de juego puro
│   ├── heuristics.py        # 6 componentes heurísticos + fases
│   ├── agents/
│   │   ├── alphabeta_agent.py   # Alpha-Beta + iterative deepening
│   │   ├── mcts_agent.py        # MCTS / UCT
│   │   ├── expectimax_agent.py  # Expectimax (oponente aleatorio)
│   │   └── human_agent.py
│   └── visualizer.py        # GUI Pygame
├── analysis/
│   ├── combinatorial.py
│   ├── tournament.py
│   └── plots.py
└── tests/
    └── test_rules.py
```

## Algoritmos IA

- **Alpha-Beta**: Minimax con poda Alpha-Beta + iterative deepening. Explora hasta la máxima profundidad posible dentro de los 2 segundos por jugada.
- **MCTS**: Monte Carlo Tree Search con fórmula UCT. Realiza el mayor número de simulaciones posible en 2 segundos.
- **Expectimax**: Variante de Minimax que modela al oponente como jugador aleatorio uniforme (nodo de azar).

## Heurísticas

La función de evaluación combina 6 componentes con pesos que varían según la fase del juego (apertura, juego medio, cierre):
1. Paridad de fichas
2. Movilidad
3. Control de esquinas
4. Cercanía a esquinas (X/C-squares)
5. Estabilidad
6. Peso posicional (matriz estática)

## Controles

- **Clic izquierdo** — colocar ficha (modo humano)
- **ESC** — salir
