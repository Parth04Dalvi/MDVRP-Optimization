# MDVRP Hybrid Optimization Framework

**CS 57200 – Heuristic Problem Solving | Track B: Optimization**
**Student:** Parth Samir Dalvi

---

## Overview

A hybrid heuristic framework for the **Multi-Depot Vehicle Routing Problem (MDVRP)** combining three algorithms in a pipeline:

```
Data Input → Greedy Nearest-Neighbour → A* + MST Heuristic → Tabu Search → Output
```

| Algorithm | Role | Key Property |
|-----------|------|-------------|
| Greedy NN | Baseline / warm start | O(n·d), fast, feasible |
| A* + MST  | Route optimiser | Admissible h(n) → optimal per-depot |
| Tabu Search | Global refiner | Escapes local optima via memory |

---

## Repository Structure

```
MDVRP-Optimization/
├── main.py                      # CLI entry point — run the full pipeline
├── requirements.txt             # Python dependencies
│
├── mdvrp/                       # Core package
│   ├── __init__.py
│   ├── problem.py               # Problem, Customer, Depot, Route classes
│   ├── greedy.py                # Greedy nearest-neighbour + 2-opt
│   ├── astar.py                 # A* search with admissible MST heuristic
│   ├── tabu.py                  # Tabu Search with aspiration criteria
│   ├── utils.py                 # MST (Prim's), metrics, validation
│   └── visualizer.py            # All plotting functions
│
├── experiments/
│   └── run_experiments.py       # All 4 report experiments + CSV export
│
├── tests/
│   └── test_algorithms.py       # 25 unit + integration tests
│
└── outputs/                     # Generated figures and CSVs (git-ignored)
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/Parth04Dalvi/MDVRP-Optimization
cd MDVRP-Optimization

# Install dependencies
pip install -r requirements.txt
```

**Requirements:** Python 3.9+, numpy, matplotlib, pytest

---

## Quick Start

### Run the full pipeline (default: 20 customers, 2 depots)
```bash
python main.py
```

### Custom problem size
```bash
python main.py --customers 30 --depots 3 --capacity 60 --seed 7
```

### Large instance (skip A* to avoid memory explosion)
```bash
python main.py --customers 100 --skip-astar --tabu-iters 1000
```

### Run all report experiments (generates all figures + CSV)
```bash
python experiments/run_experiments.py --output-dir outputs/
```

### Skip the slow scaling experiment
```bash
python experiments/run_experiments.py --skip-scaling
```

---

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `--customers` | 20 | Number of customer nodes |
| `--depots` | 2 | Number of depot nodes |
| `--capacity` | 50 | Vehicle capacity per depot |
| `--seed` | 42 | Random seed for reproducibility |
| `--tabu-iters` | 500 | Tabu Search max iterations |
| `--tabu-tenure` | 10 | How long a move stays forbidden |
| `--max-nodes` | 10000 | A* node expansion limit per depot |
| `--skip-astar` | False | Skip A* step (Greedy → Tabu only) |
| `--output-dir` | outputs/ | Directory for saving figures |
| `--no-plots` | False | Disable figure generation |

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Expected output: **25 tests passing** covering:
- Utility functions (MST admissibility, Euclidean distance)
- Route class (distance, feasibility, 2-opt)
- Greedy (correctness, edge cases, determinism)
- A* (improvement over greedy, feasibility)
- Tabu Search (feasibility, monotonic history, stochastic variation)
- Full pipeline integration test

---

## Algorithm Details

### Greedy Nearest-Neighbour
- Assigns each customer to the nearest depot with remaining capacity
- Applies **2-opt intra-route improvement** after assignment (Enhancement 1)
- Time: O(n·d), Space: O(n)

### A* Search with MST Heuristic
- Runs independently per depot on the assigned customers
- **State:** (current node, frozenset of unvisited customer IDs)
- **g(n):** actual travel distance so far
- **h(n):** MST cost of remaining unvisited customers (Prim's algorithm)
- h(n) is **admissible** — never overestimates — guaranteeing optimality
- Node expansion limit prevents memory explosion on large instances

### Tabu Search
- **Neighbourhood moves:** relocate (move one customer) + swap (exchange two customers between depots)
- **Tabu list:** forbids recently made moves for `tenure` iterations
- **Aspiration criterion:** overrides tabu if move achieves a new global best
- **Early stopping:** halts after 100 consecutive non-improving iterations
- Runs 30 times for stochastic statistical reporting

---

## Results Summary

| Algorithm | Avg Distance | Std Dev | 95% CI | Runs |
|-----------|-------------|---------|--------|------|
| Greedy | 1034.54 | 84.55 | [1004.29, 1064.80] | 30 |
| A* + MST | 811.08 | 66.29 | [787.36, 834.80] | 30 |
| **Tabu Search** | **429.93** | **32.88** | **[418.17, 441.70]** | **30** |

**Tabu Search achieves 58.4% improvement over Greedy on average.**

---

## Reproducibility

All experiments use fixed seeds (42–71) for the 30-run statistical analysis.
To exactly reproduce Table 4.3:

```bash
python experiments/run_experiments.py --output-dir outputs/
```

Results are saved to `outputs/results_summary.csv`.

---

## References

- Hart, Nilsson & Raphael (1968) — A* Search
- Cordeau, Gendreau & Laporte (1997) — Tabu Search for MDVRP
- Prim (1957) — MST Algorithm
- Russell & Norvig (2020) — AI: A Modern Approach
