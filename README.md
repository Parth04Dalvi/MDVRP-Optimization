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
1. S. Russell and P. Norvig, Artificial Intelligence: A Modern Approach, 4th ed. 
Hoboken, NJ, USA: Pearson, 2020
2. G. Laporte, “The vehicle routing problem: An overview of exact and approximate 
algorithms,” European Journal of Operational Research, vol. 59, no. 3, pp. 345–358, 
1992 
3. J. F. Cordeau, M. Gendreau, and G. Laporte, “A tabu search heuristic for the static 
multi-depot vehicle routing problem,” Networks, vol. 30, no. 2, pp. 105–119, 1997  
4. F. Glover and M. Laguna, Tabu Search. Boston, MA, USA: Springer, 1997  
5. N. Christofides, “Worst-case analysis of a new heuristic for the travelling salesman 
problem,” Carnegie Mellon University, Pittsburgh, PA, USA, Tech. Rep., 1976  
6. E. W. Dijkstra, “A note on two problems in connexion with graphs,” Numerische 
Mathematik, vol. 1, pp. 269–271, 1959  
7. R. C. Prim, “Shortest connection networks and some generalizations,” Bell System 
Technical Journal, vol. 36, no. 6, pp. 1389–1401, 1957  
8. P. E. Hart, N. J. Nilsson, and B. Raphael, “A formal basis for the heuristic 
determination of minimum cost paths,” IEEE Transactions on Systems Science and 
Cybernetics, vol. 4, no. 2, pp. 100–107, 1968  
9. P. Toth and D. Vigo, Vehicle Routing: Problems, Methods, and Applications, 2nd ed. 
Philadelphia, PA, USA: SIAM, 2014  
10. Google Developers, “Vehicle Routing Problem,” Google OR-Tools Documentation. 
[Online]. Available: https://developers.google.com/optimization/routing 
11. O. Bräysy and M. Gendreau, “Vehicle routing problem with time windows, Part I: 
Route construction and local search algorithms,” Transportation Science, vol. 39, 
no. 1, pp. 104–118, 2005  
12. T. Vidal, T. G. Crainic, M. Gendreau, and C. Prins, “A hybrid genetic algorithm for 
multidepot and periodic vehicle routing problems,” Operations Research, vol. 60, 
no. 3, pp. 611–624, 2012  
13. S. Salhi and R. J. Sari, “A multi-level composite heuristic for the multi-depot vehicle 
routing problem,” Methodology and Computing in Applied Probability, vol. 9, no. 1, 
pp. 95–106, 2007  
14. D. Pisinger and S. Ropke, “A general heuristic for vehicle routing problems,” 
Computers & Operations Research, vol. 34, no. 8, pp. 2403–2435, 2007 
15. M. Dorigo and T. Stützle, Ant Colony Optimization. Cambridge, MA, USA: MIT Press, 
2004.
