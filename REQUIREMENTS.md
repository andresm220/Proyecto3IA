n# REQUIREMENTS.md — Othello (Reversi) con IA Adversaria

> Documento de especificación para implementación asistida por Claude Code.
> Proyecto 3 — Inteligencia Artificial 2026. Juegos adversarios (suma cero, información perfecta).
> **Idioma de código y comentarios:** español (variables/funciones en inglés, docstrings en español está bien).

---

## 1. Objetivo del proyecto

Implementar un **agente inteligente** capaz de competir en **Othello (Reversi)** sobre un tablero de 8×8, usando algoritmos deterministas y probabilísticos, con una **interfaz gráfica en Pygame**.

El proyecto se evalúa por:
1. Correctitud de las reglas de Othello.
2. Calidad y diversidad de los algoritmos de búsqueda (Alpha-Beta, Expectimax, MCTS).
3. Calidad de las **heurísticas** (obligatorias: no se llega al final del árbol).
4. Una GUI funcional con indicadores de rendimiento.
5. Un análisis de rendimiento (explosión combinatoria + torneo IA-IA).

---

## 2. Stack tecnológico y restricciones globales

- **Lenguaje:** Python 3.11+
- **GUI:** Pygame
- **Gráficas del reporte:** matplotlib
- **Dependencias mínimas** (`requirements.txt`): `pygame`, `numpy`, `matplotlib`.
- **Restricción dura de tiempo:** **máximo 2.0 segundos por jugada** para cualquier agente IA. Esto NO es opcional: el código debe respetarlo (ver §8 Gestión de tiempo).
- **Separación total lógica/visual:** el motor de juego (`GameEngine`) y los agentes NO deben importar Pygame ni depender de nada gráfico. La GUI consume el motor, nunca al revés. Esto es un requisito explícito del enunciado.
- **Reproducibilidad:** los componentes con aleatoriedad (MCTS, Expectimax) deben aceptar una `seed` opcional.

---

## 3. Reglas de Othello (implementar exactamente así)

### 3.1 Tablero y posición inicial
- Tablero 8×8, indexado `[fila][columna]` con `fila` y `columna` en `0..7` (fila 0 = arriba).
- Tres estados de casilla: `EMPTY = 0`, `BLACK = 1`, `WHITE = 2` (definir como constantes).
- **Posición inicial exacta** (estándar del enunciado: negras en d5/e4, blancas en d4/e5):
  - `(3,3) = WHITE`
  - `(3,4) = BLACK`
  - `(4,3) = BLACK`
  - `(4,4) = WHITE`
- **Comienza NEGRO.**

### 3.2 Movimientos válidos
- Un movimiento coloca una ficha del jugador en una casilla vacía de modo que **encierre** una o más fichas del oponente en línea recta (8 direcciones: horizontal, vertical, diagonal), terminando en otra ficha propia.
- Un movimiento es válido **si y solo si voltea al menos una ficha** del oponente.
- Al colocar, **todas** las fichas encerradas en **todas** las direcciones válidas se voltean.

### 3.3 Turnos, pases y fin de juego
- Si un jugador **no tiene movimientos válidos**, **pasa** el turno (no juega). NO se puede pasar voluntariamente si hay jugadas disponibles.
- Si **ambos** jugadores no tienen movimientos válidos → **fin del juego**.
- También termina si el tablero está lleno.
- **Ganador:** el jugador con más fichas. Empate posible (32–32).

### 3.4 Tests obligatorios de reglas
Crear `tests/test_rules.py` que verifique al menos:
- Posición inicial correcta.
- Negro tiene exactamente 4 movimientos legales en la apertura.
- Un movimiento voltea correctamente en múltiples direcciones.
- Detección de pase y de fin de juego.
- Conteo final y determinación del ganador.

---

## 4. Arquitectura y estructura de archivos

```
othello-ai/
├── README.md
├── requirements.txt
├── main.py                     # punto de entrada: lanza la GUI / selección de modo
├── src/
│   ├── __init__.py
│   ├── constants.py            # EMPTY/BLACK/WHITE, BOARD_SIZE, DIRECTIONS, matriz de pesos
│   ├── game_engine.py          # GameEngine: estado + reglas + evaluate()
│   ├── heuristics.py           # funciones heurísticas + detección de fase
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py       # interfaz común: get_move(engine) -> move
│   │   ├── human_agent.py      # devuelve la jugada recibida de la GUI
│   │   ├── alphabeta_agent.py  # Alpha-Beta + iterative deepening + (opcional) TT
│   │   ├── expectimax_agent.py # Expectimax (nodos de azar)
│   │   └── mcts_agent.py       # MCTS / UCT con presupuesto de tiempo
│   └── visualizer.py           # GameVisualizer (Pygame)
├── analysis/
│   ├── combinatorial.py        # conteo de nodos Minimax puro vs Alpha-Beta + b_eff
│   ├── tournament.py           # torneo 20 partidas Alpha-Beta vs MCTS
│   └── plots.py                # genera las gráficas del reporte (matplotlib)
└── tests/
    └── test_rules.py
```

**Principio de diseño:** `GameEngine` y `agents/` son *puros* (sin Pygame). `visualizer.py` y `main.py` son la única capa que conoce Pygame.

---

## 5. Clase `GameEngine` (núcleo, en `game_engine.py`)

Representa el estado y las reglas. Debe ser **clonable y barato de copiar** (los algoritmos exploran muchos estados).

### Atributos
- `board`: matriz 8×8 (`numpy.int8` o lista de listas).
- `current_player`: `BLACK` o `WHITE`.

### Métodos requeridos (incluye los que pide el enunciado)
```python
def get_legal_moves(self, player=None) -> list[tuple[int,int]]:
    """Movimientos válidos del jugador dado (por defecto current_player)."""

def is_legal_move(self, move, player=None) -> bool: ...

def apply_move(self, move) -> "GameEngine":
    """Aplica el movimiento, voltea fichas y cambia de turno.
    Debe manejar el PASE automático si el rival no tiene jugadas."""

def clone(self) -> "GameEngine":
    """Copia profunda barata del estado."""

def is_terminal(self) -> bool: ...

def get_winner(self) -> int:
    """BLACK, WHITE o 0 (empate). Solo válido en estado terminal."""

def count_pieces(self) -> tuple[int,int]:
    """(negras, blancas)."""

def evaluate(self, player) -> float:
    """Heurística: valor numérico de un estado NO terminal desde la
    perspectiva de `player`. Delega en heuristics.py (ver §7)."""
```

> **Nota sobre el rubro:** el enunciado lista `alpha_beta`, `expectimax` y `mcts` como métodos del motor, pero permite construir la arquitectura que se considere conveniente. Aquí esos algoritmos viven en `agents/` por limpieza. En el **reporte** se debe documentar este mapeo y dejar constancia de que cada algoritmo está implementado.

---

## 6. Agentes / Algoritmos de búsqueda (`src/agents/`)

Interfaz común en `base_agent.py`:
```python
class BaseAgent:
    def __init__(self, player, time_limit=2.0, seed=None): ...
    def get_move(self, engine: "GameEngine") -> tuple[int,int]:
        """Devuelve la mejor jugada respetando time_limit."""
    # métricas expuestas para la GUI y el análisis:
    self.nodes_explored: int
    self.last_move_time: float
    self.last_value: float   # valoración del tablero de la jugada elegida
```

### 6.1 `AlphaBetaAgent` (determinista)
- **Minimax con poda Alpha-Beta.**
- **Iterative deepening** (profundizar mientras quede tiempo dentro de los 2s) para respetar el límite y poder reportar la mejor jugada parcial.
- **Ordenamiento de movimientos** para maximizar las podas (p.ej. probar primero esquinas y casillas de mayor peso posicional).
- (Opcional, recomendado) **Tabla de transposición** con hash del tablero.
- Debe contabilizar `nodes_explored`.

```python
def alpha_beta(self, engine, depth, alpha, beta, maximizing) -> float: ...
```

### 6.2 `ExpectimaxAgent` (probabilístico)
- Variante para modelar un oponente **subóptimo / incierto**: en los nodos del oponente se usa un **nodo de azar** (promedio ponderado) en lugar de minimizar.
- Modelo sugerido: el oponente elige movimientos con probabilidad proporcional a su heurística (softmax) o uniforme sobre las jugadas legales. Documentar el modelo elegido.

```python
def expectimax(self, engine, depth) -> float: ...
```

### 6.3 `MCTSAgent` (Montecarlo / UCT)
- Cuatro fases: **selección → expansión → simulación (rollout) → retropropagación**.
- **Fórmula UCT** para la selección:

  `Score = mean_win_rate + C * sqrt( ln(parent_visits) / node_visits )`

  - `C` configurable (por defecto `C = 1.41` ≈ √2). Exponer como parámetro.
- **Presupuesto por tiempo** (no por iteraciones fijas): correr el mayor número de iteraciones posible dentro de los 2s. Igualmente aceptar un parámetro `iterations` para experimentos.
- Rollout: aleatorio uniforme por defecto; se puede mejorar con rollout sesgado por heurística (documentar si se hace).
- Reportar número de simulaciones e iteraciones por jugada.

```python
def mcts(self, engine, iterations=None, C=1.41) -> tuple[int,int]: ...
```

> Se pueden implementar variantes/mejoras adicionales (p.ej. Alpha-Beta con ventanas de aspiración, MCTS con RAVE). Si se hace, **debe documentarse el funcionamiento lógico en el reporte**.

---

## 7. Heurísticas (OBLIGATORIAS) — `heuristics.py`

En Othello **no basta llegar al final del árbol**; la heurística decide la fuerza del agente. Implementar una **combinación lineal ponderada** de los siguientes componentes, todos normalizados a un rango comparable (p.ej. `-100..100`):

1. **Paridad de fichas (coin parity):** `100 * (mías - rival) / (mías + rival)`. Útil sobre todo al final; **poco peso al inicio**.
2. **Movilidad (mobility):** diferencia normalizada del número de jugadas legales `100 * (mov_mías - mov_rival)/(mov_mías + mov_rival)`. Alta importancia en apertura/medio juego.
3. **Control de esquinas (corner control):** las esquinas no se pueden voltear → altísimo valor. Contar esquinas capturadas por cada lado.
4. **Cercanía a esquinas (X-squares / C-squares):** penalizar fichas en casillas diagonales (X) y adyacentes (C) a esquinas **vacías**, porque regalan la esquina.
5. **Estabilidad (stability):** fichas que ya no pueden voltearse nunca (bordes anclados a esquinas, etc.). Penalizar fichas inestables/“frontera”.
6. **Peso posicional (matriz estática):** suma de los pesos de la siguiente matriz para las fichas propias menos las del rival.

### Matriz de pesos posicionales (8×8) — definir en `constants.py`
```python
WEIGHTS = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120],
]
```

### Estrategia por FASES (requisito del enunciado)
`evaluate()` debe ajustar los pesos según la fase, detectada por número de fichas en tablero o de jugadas:
- **Apertura (≈ primeras 10–15 jugadas):** priorizar **movilidad** y **posición**; **minimizar** la cantidad de fichas propias; evitar X/C-squares. Peso de paridad ≈ 0.
- **Juego medio:** balancear movilidad + estabilidad + posición + esquinas.
- **Cierre (≈ últimas 10–15 jugadas):** subir el peso de **paridad** (maximizar fichas); si el árbol ya es pequeño, el Alpha-Beta puede **resolver exacto hasta el final** (búsqueda completa de fichas).

Implementar `detect_phase(engine) -> {"opening","midgame","endgame"}` y un diccionario de pesos por fase, configurable.

---

## 8. Gestión del límite de tiempo (2 s/jugada)

- Cada `get_move` recibe `time_limit=2.0` y debe terminar **antes** de agotarlo, devolviendo la mejor jugada encontrada hasta ese momento.
- **Alpha-Beta:** iterative deepening; al detectar que se acaba el tiempo, abortar la iteración en curso y devolver el mejor resultado de la última profundidad completa.
- **MCTS:** bucle `while time.perf_counter() - start < time_limit`.
- Dejar un margen de seguridad (p.ej. cortar a 1.9 s) para no excederse por el overhead de devolver el resultado.

---

## 9. Clase `GameVisualizer` (Pygame, en `visualizer.py`)

GUI que consume el motor y los agentes. Debe permitir:

- **Renderizado del tablero 8×8** con fichas blancas/negras y la posición inicial correcta.
- **Movimiento de piezas en tiempo real** (animación o redibujado por turno). Resaltar jugadas legales del humano y, opcionalmente, la última jugada hecha.
- **Panel de indicadores de rendimiento de la IA** (actualizado por jugada):
  - Nodos explorados (o iteraciones/simulaciones en MCTS).
  - Tiempo por jugada (segundos).
  - Valoración del tablero (`last_value`).
  - Marcador de fichas (negras vs blancas) y turno actual.
- **Selección de modo de juego:**
  - Humano vs. Humano
  - Humano vs. IA
  - IA vs. IA
- **(Opcional) Selección de dificultad** para la IA (p.ej. profundidad del Alpha-Beta o `iterations`/tiempo del MCTS, y elección del algoritmo).
- Manejo correcto del **pase** (mostrar aviso si un jugador no tiene jugadas) y de la **pantalla de fin de juego** con el ganador.

---

## 10. Análisis de rendimiento (`analysis/`) — para el reporte

### 10.1 Explosión combinatoria (`combinatorial.py`)
- Comparar **nodos visitados** entre **Minimax puro** (a baja profundidad, p.ej. 1–5, si es viable) y **Alpha-Beta** a las mismas profundidades, sobre las mismas posiciones.
- Calcular el **factor de ramificación efectivo**:

  `b_eff = nodos_totales ** (1 / depth)`   (la raíz `depth`-ésima de los nodos totales).

- Generar una **gráfica** nodos-vs-profundidad (escala log recomendada) y una tabla de `b_eff`.

### 10.2 Torneo IA-IA (`tournament.py`)
- **20 partidas** entre:
  - **Agente A:** Alpha-Beta con profundidad fija optimizada.
  - **Agente B:** MCTS con presupuesto de simulaciones **equivalente en tiempo**.
- **Límite estricto de 2 s por jugada** en ambos.
- Alternar quién juega negras/blancas para evitar sesgo del primer movimiento.
- Reportar: **victorias, derrotas, empates**, tiempo promedio por jugada y eficiencia temporal de cada agente.
- `plots.py` genera las gráficas de resultados.

---

## 11. Entregables (recordatorio del curso)

- Código fuente **documentado** en repositorio Git.
- **Video de demostración de 3 min** mostrando los modos de juego (lo graba el estudiante; el código debe facilitar enseñar los 3 modos).
- **Reporte técnico en PDF** con gráficas de rendimiento (apoyarse en `analysis/`).

> Claude Code debe generar el código, los scripts de análisis y un `README.md` con instrucciones de ejecución. El video y el PDF final los produce el estudiante a partir de esos resultados.

---

## 12. Convenciones de código

- Type hints en firmas públicas.
- Docstrings breves en español explicando el "por qué", no solo el "qué".
- Sin lógica de juego dentro de la capa Pygame.
- Constantes mágicas en `constants.py`.
- Aleatoriedad siempre vía un `random.Random(seed)` inyectable.
- Commits pequeños y descriptivos.

---

## 13. Criterios de aceptación (Definition of Done)

- [ ] Reglas de Othello correctas; `tests/test_rules.py` pasa.
- [ ] `GameEngine` puro (sin Pygame), clonable, con `get_legal_moves`, `apply_move`, `is_terminal`, `get_winner`, `evaluate`.
- [ ] Tres agentes funcionando: `AlphaBetaAgent`, `ExpectimaxAgent`, `MCTSAgent`.
- [ ] Todos respetan el límite de **2.0 s/jugada**.
- [ ] Heurística con los 6 componentes y **estrategia por fases**.
- [ ] GUI Pygame con los 3 modos y el panel de métricas (nodos, tiempo, valoración).
- [ ] `analysis/combinatorial.py` calcula nodos Minimax vs Alpha-Beta y `b_eff`.
- [ ] `analysis/tournament.py` corre 20 partidas Alpha-Beta vs MCTS y reporta métricas.
- [ ] `analysis/plots.py` genera las gráficas.
- [ ] `README.md` con instrucciones para ejecutar el juego y los análisis.

---

## 14. Orden de implementación sugerido (roadmap para Claude Code)

1. `constants.py` + `game_engine.py` con reglas + `tests/test_rules.py` (verde antes de seguir).
2. `heuristics.py` + `evaluate()` con fases.
3. `agents/base_agent.py` + `human_agent.py`.
4. `alphabeta_agent.py` (con iterative deepening y conteo de nodos).
5. `visualizer.py` + `main.py`: jugar Humano vs IA con el Alpha-Beta.
6. `mcts_agent.py` y `expectimax_agent.py`.
7. Modos Humano vs Humano e IA vs IA en la GUI.
8. `analysis/` (combinatoria, torneo, gráficas).
9. `README.md` y limpieza final.

> Implementar y validar fase por fase; no avanzar al siguiente bloque si el actual no corre.
