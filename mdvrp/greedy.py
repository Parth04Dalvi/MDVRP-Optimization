"""
mdvrp/greedy.py
---------------
Greedy Nearest-Neighbour baseline for the MDVRP.

Algorithm
---------
For each unassigned customer (shuffled to break ties randomly):
  1. Find the nearest depot that still has capacity.
  2. Append the customer to that depot's current route.

After all customers are assigned, apply 2-opt intra-route improvement
to each route (Enhancement 1 — intra-route 2-opt).

Time complexity : O(n * d)  where n = customers, d = depots
Space complexity: O(n)
"""

from __future__ import annotations
import random
import time
from typing import Dict, List, Optional, Tuple

from mdvrp.problem import Customer, Depot, Problem, Route
from mdvrp.utils   import solution_cost, validate_solution


def greedy_solve(
    problem: Problem,
    seed: Optional[int] = None,
    apply_two_opt: bool = True,
) -> Tuple[List[Route], float, float]:
    """Solve MDVRP with the Greedy Nearest-Neighbour heuristic.

    Each depot may spawn multiple vehicle routes if a single vehicle's
    capacity is insufficient for all assigned customers.

    Parameters
    ----------
    problem : Problem
        The MDVRP instance to solve.
    seed : int or None
        Shuffle seed for customer ordering (for reproducibility).
    apply_two_opt : bool
        If True, apply 2-opt intra-route improvement after assignment.

    Returns
    -------
    routes : list of Route
        All constructed routes (≥1 per depot that has customers).
    total_dist : float
        Sum of all route distances.
    elapsed : float
        Wall-clock time in seconds.
    """
    t_start = time.perf_counter()

    # ── active routes: list of open routes per depot ──────────────────────────
    # Each depot starts with one empty route; a new one is opened on overflow.
    active: Dict[int, Route] = {d.id: Route(depot=d) for d in problem.depots}
    all_routes: List[Route]  = list(active.values())

    # ── shuffle customers to avoid order bias ─────────────────────────────────
    rng = random.Random(seed)
    unassigned = list(problem.customers)
    rng.shuffle(unassigned)

    # ── assign each customer to the nearest feasible depot/vehicle ────────────
    for customer in unassigned:
        best_depot_id = _nearest_feasible_depot(
            customer, problem.depots, active
        )
        if best_depot_id is None:
            # All current vehicles full → open a new vehicle at the nearest depot
            nearest_depot = min(
                problem.depots,
                key=lambda d: customer.distance_to(d)
            )
            new_route = Route(depot=nearest_depot)
            all_routes.append(new_route)
            active[nearest_depot.id] = new_route
            best_depot_id = nearest_depot.id

        active[best_depot_id].customers.append(customer)

    # ── Enhancement 1: intra-route 2-opt ──────────────────────────────────────
    if apply_two_opt:
        for r in all_routes:
            r.two_opt()

    elapsed = time.perf_counter() - t_start
    total   = solution_cost(all_routes)
    return all_routes, total, elapsed


def _nearest_feasible_depot(
    customer: Customer,
    depots: List[Depot],
    active: Dict[int, "Route"],
) -> Optional[int]:
    """Return the depot id whose active route can still accept the customer.

    Picks the nearest depot (by depot coordinates) with sufficient
    remaining capacity.  Returns None if all active routes are full.
    """
    best_id   = None
    best_dist = float("inf")

    for depot in depots:
        route         = active[depot.id]
        remaining_cap = depot.capacity - route.total_demand
        if customer.demand <= remaining_cap:
            d = customer.distance_to(depot)
            if d < best_dist:
                best_dist = d
                best_id   = depot.id

    return best_id
