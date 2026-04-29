"""
main.py
-------
Command-line interface for the MDVRP Hybrid Solver.

Usage examples
--------------
# Run full pipeline on a random instance (default settings)
    python main.py

# Custom problem size
    python main.py --customers 30 --depots 3 --capacity 60

# Fixed seed for reproducibility
    python main.py --seed 42

# Skip A* (Greedy + Tabu only) for large instances
    python main.py --customers 100 --skip-astar

# Specify output directory
    python main.py --output-dir results/run1
"""

from __future__ import annotations
import argparse
import logging
import os
import sys
import time

from mdvrp import (
    Problem, greedy_solve, astar_solve, tabu_solve,
    validate_solution, print_solution, solution_cost,
)
from mdvrp.visualizer import plot_routes, plot_distance_comparison, plot_convergence

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── CLI argument parser ───────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="MDVRP Hybrid Solver: Greedy → A* + MST → Tabu Search"
    )
    p.add_argument("--customers",   type=int,   default=20,
                   help="Number of customer nodes (default: 20)")
    p.add_argument("--depots",      type=int,   default=2,
                   help="Number of depot nodes (default: 2)")
    p.add_argument("--capacity",    type=int,   default=50,
                   help="Vehicle capacity per depot (default: 50)")
    p.add_argument("--seed",        type=int,   default=42,
                   help="Random seed (default: 42)")
    p.add_argument("--tabu-iters",  type=int,   default=500,
                   help="Tabu Search max iterations (default: 500)")
    p.add_argument("--tabu-tenure", type=int,   default=10,
                   help="Tabu tenure (default: 10)")
    p.add_argument("--max-nodes",   type=int,   default=10_000,
                   help="A* max nodes per depot (default: 10000)")
    p.add_argument("--skip-astar",  action="store_true",
                   help="Skip A* step (Greedy → Tabu only)")
    p.add_argument("--output-dir",  default="outputs",
                   help="Directory for saving figures (default: outputs/)")
    p.add_argument("--no-plots",    action="store_true",
                   help="Disable figure generation")
    return p


# ── Main pipeline ─────────────────────────────────────────────────────────────

def main() -> None:
    args   = build_parser().parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    log.info("=" * 55)
    log.info("  MDVRP Hybrid Solver — CS 57200 Final Project")
    log.info("=" * 55)
    log.info(f"  customers={args.customers}  depots={args.depots}  "
             f"capacity={args.capacity}  seed={args.seed}")
    log.info("")

    # ── generate problem ──────────────────────────────────────────────────────
    problem = Problem.generate_random(
        n_customers=args.customers,
        n_depots=args.depots,
        capacity=args.capacity,
        seed=args.seed,
        name=f"MDVRP-n{args.customers}-d{args.depots}",
    )
    log.info(f"Problem: {problem}")

    # ── Stage 1: Greedy ───────────────────────────────────────────────────────
    log.info("\n── Stage 1: Greedy Nearest-Neighbour ──")
    g_routes, g_dist, g_time = greedy_solve(problem, seed=args.seed)

    ok, msg = validate_solution(g_routes, len(problem.customers))
    if not ok:
        log.error(f"Greedy solution invalid: {msg}")
        sys.exit(1)

    log.info(f"  Distance : {g_dist:.2f}")
    log.info(f"  Time     : {g_time*1000:.2f} ms")
    print_solution(g_routes, "Greedy")

    # ── Stage 2: A* + MST ────────────────────────────────────────────────────
    if not args.skip_astar:
        log.info("── Stage 2: A* Search with MST Heuristic ──")
        a_routes, a_dist, a_time, a_nodes = astar_solve(
            problem,
            initial_routes=g_routes,
            max_nodes_per_depot=args.max_nodes,
        )
        ok, msg = validate_solution(a_routes, len(problem.customers))
        if not ok:
            log.warning(f"A* solution invalid: {msg} — falling back to Greedy")
            a_routes, a_dist = g_routes, g_dist
            a_nodes = 0

        log.info(f"  Distance       : {a_dist:.2f}  "
                 f"(Δ {100*(g_dist-a_dist)/g_dist:+.1f}% vs Greedy)")
        log.info(f"  Time           : {a_time*1000:.2f} ms")
        log.info(f"  Nodes expanded : {a_nodes}")
        print_solution(a_routes, "A* + MST")
        tabu_seed_routes = a_routes
    else:
        log.info("── Stage 2: A* skipped ──")
        a_dist = g_dist
        tabu_seed_routes = g_routes

    # ── Stage 3: Tabu Search ─────────────────────────────────────────────────
    log.info("── Stage 3: Tabu Search ──")
    t_routes, t_dist, t_time, history = tabu_solve(
        problem,
        initial_routes=tabu_seed_routes,
        max_iterations=args.tabu_iters,
        tabu_tenure=args.tabu_tenure,
        seed=args.seed,
    )
    ok, msg = validate_solution(t_routes, len(problem.customers))
    if not ok:
        log.error(f"Tabu solution invalid: {msg}")
        sys.exit(1)

    log.info(f"  Distance       : {t_dist:.2f}  "
             f"(Δ {100*(g_dist-t_dist)/g_dist:+.1f}% vs Greedy)")
    log.info(f"  Time           : {t_time*1000:.2f} ms")
    log.info(f"  Iterations run : {len(history)}")
    print_solution(t_routes, "Tabu Search")

    # ── Summary ───────────────────────────────────────────────────────────────
    log.info("=" * 55)
    log.info("  SUMMARY")
    log.info("=" * 55)
    log.info(f"  {'Algorithm':<20} {'Distance':>10}  {'Time (ms)':>10}")
    log.info(f"  {'Greedy':<20} {g_dist:>10.2f}  {g_time*1000:>10.2f}")
    if not args.skip_astar:
        log.info(f"  {'A* + MST':<20} {a_dist:>10.2f}  {a_time*1000:>10.2f}")
    log.info(f"  {'Tabu Search':<20} {t_dist:>10.2f}  {t_time*1000:>10.2f}")
    log.info(f"\n  Total improvement: {100*(g_dist-t_dist)/g_dist:.1f}% over Greedy")

    # ── Figures ───────────────────────────────────────────────────────────────
    if not args.no_plots:
        log.info("\nGenerating figures...")
        plot_routes(
            problem, g_routes,
            title=f"Greedy Solution — dist={g_dist:.1f}",
            output_path=os.path.join(args.output_dir, "greedy_routes.png"),
        )
        plot_routes(
            problem, t_routes,
            title=f"Tabu Search Solution — dist={t_dist:.1f}",
            output_path=os.path.join(args.output_dir, "tabu_routes.png"),
        )
        labels = ["Greedy", "Tabu Search"]
        means  = [g_dist, t_dist]
        if not args.skip_astar:
            labels.insert(1, "A* + MST")
            means.insert(1, a_dist)
        plot_distance_comparison(
            labels, means,
            title="Algorithm Distance Comparison",
            output_path=os.path.join(args.output_dir, "distance_comparison.png"),
        )
        plot_convergence(
            [history],
            title="Tabu Search Convergence",
            output_path=os.path.join(args.output_dir, "tabu_convergence.png"),
        )
        log.info(f"Figures saved to {args.output_dir}/")


if __name__ == "__main__":
    main()
