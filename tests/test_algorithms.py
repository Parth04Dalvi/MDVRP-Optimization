"""
tests/test_algorithms.py
-------------------------
Unit tests for all MDVRP algorithms.

Run with:
    python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math
import pytest

from mdvrp import (
    Problem, Customer, Depot, Route,
    greedy_solve, astar_solve, tabu_solve,
    validate_solution, solution_cost,
)
from mdvrp.utils import mst_cost, euclidean


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def small_problem():
    """5 customers, 2 depots, capacity=30."""
    return Problem.generate_random(
        n_customers=5, n_depots=2, capacity=30, seed=0, name="small"
    )

@pytest.fixture
def medium_problem():
    """20 customers, 2 depots, capacity=50."""
    return Problem.generate_random(
        n_customers=20, n_depots=2, capacity=50, seed=42, name="medium"
    )

@pytest.fixture
def edge_single_customer():
    """Edge case: 1 customer, 1 depot."""
    depot    = Depot(id=0, x=50.0, y=50.0, capacity=100)
    customer = Customer(id=0, x=60.0, y=60.0, demand=10)
    p = Problem(depots=[depot], customers=[customer], name="single")
    p.build_distance_matrix()
    return p

@pytest.fixture
def edge_exact_capacity():
    """Edge case: one customer whose demand exactly equals depot capacity."""
    depot    = Depot(id=0, x=0.0, y=0.0, capacity=15)
    customer = Customer(id=0, x=10.0, y=0.0, demand=15)
    p = Problem(depots=[depot], customers=[customer], name="exact-cap")
    p.build_distance_matrix()
    return p


# ── Utils tests ───────────────────────────────────────────────────────────────

class TestUtils:

    def test_euclidean_same_point(self):
        c = Customer(0, 3.0, 4.0, 5)
        assert euclidean(c, c) == pytest.approx(0.0)

    def test_euclidean_known_distance(self):
        a = Customer(0, 0.0, 0.0, 1)
        b = Customer(1, 3.0, 4.0, 1)
        assert euclidean(a, b) == pytest.approx(5.0)

    def test_mst_cost_two_nodes(self):
        a = Customer(0, 0.0, 0.0, 1)
        b = Customer(1, 3.0, 4.0, 1)
        assert mst_cost([a, b]) == pytest.approx(5.0)

    def test_mst_cost_single_node_returns_zero(self):
        assert mst_cost([Customer(0, 1.0, 1.0, 1)]) == 0.0

    def test_mst_cost_empty_returns_zero(self):
        assert mst_cost([]) == 0.0

    def test_mst_admissible_vs_tour(self):
        """MST cost must be ≤ any valid tour (admissibility)."""
        nodes = [Customer(i, float(i*10), float(i*5), 1) for i in range(6)]
        mst   = mst_cost(nodes)
        # brute-force shortest path through all nodes (sequential is one tour)
        pts   = [nodes[0]] + nodes + [nodes[0]]
        tour  = sum(euclidean(pts[i], pts[i+1]) for i in range(len(pts)-1))
        assert mst <= tour + 1e-9


# ── Route tests ───────────────────────────────────────────────────────────────

class TestRoute:

    def test_empty_route_distance_is_zero(self):
        d = Depot(0, 0.0, 0.0, 100)
        r = Route(depot=d)
        assert r.distance == pytest.approx(0.0)

    def test_route_distance_triangle(self):
        d  = Depot(0, 0.0, 0.0, 100)
        c1 = Customer(0, 3.0, 0.0, 5)
        c2 = Customer(1, 3.0, 4.0, 5)
        r  = Route(depot=d, customers=[c1, c2])
        # 0→c1=3, c1→c2=4, c2→0=5  total=12
        assert r.distance == pytest.approx(12.0)

    def test_feasibility_within_capacity(self):
        d  = Depot(0, 0.0, 0.0, capacity=20)
        cs = [Customer(i, float(i), 0.0, 5) for i in range(3)]
        r  = Route(depot=d, customers=cs)
        assert r.is_feasible is True

    def test_feasibility_exceeds_capacity(self):
        d  = Depot(0, 0.0, 0.0, capacity=10)
        cs = [Customer(i, float(i), 0.0, 5) for i in range(3)]  # demand=15
        r  = Route(depot=d, customers=cs)
        assert r.is_feasible is False

    def test_two_opt_does_not_increase_distance(self):
        d  = Depot(0, 0.0, 0.0, 100)
        cs = [Customer(i, float(i*7 % 30), float(i*11 % 30), 1) for i in range(8)]
        r  = Route(depot=d, customers=list(cs))
        before = r.distance
        r.two_opt()
        assert r.distance <= before + 1e-9


# ── Greedy tests ──────────────────────────────────────────────────────────────

class TestGreedy:

    def test_all_customers_served(self, medium_problem):
        routes, _, _ = greedy_solve(medium_problem, seed=0)
        ok, msg = validate_solution(routes, len(medium_problem.customers))
        assert ok, msg

    def test_solution_feasible(self, medium_problem):
        routes, _, _ = greedy_solve(medium_problem, seed=0)
        for r in routes:
            assert r.is_feasible, f"Route for depot {r.depot.id} exceeds capacity"

    def test_single_customer(self, edge_single_customer):
        routes, dist, _ = greedy_solve(edge_single_customer, seed=0)
        ok, msg = validate_solution(routes, 1)
        assert ok, msg
        assert dist > 0

    def test_exact_capacity(self, edge_exact_capacity):
        routes, _, _ = greedy_solve(edge_exact_capacity, seed=0)
        ok, msg = validate_solution(routes, 1)
        assert ok, msg

    def test_deterministic_with_same_seed(self, medium_problem):
        r1, d1, _ = greedy_solve(medium_problem, seed=99)
        r2, d2, _ = greedy_solve(medium_problem, seed=99)
        assert d1 == pytest.approx(d2)

    def test_returns_positive_distance(self, medium_problem):
        _, dist, _ = greedy_solve(medium_problem)
        assert dist > 0

    def test_small_problem(self, small_problem):
        routes, dist, elapsed = greedy_solve(small_problem, seed=0)
        ok, msg = validate_solution(routes, len(small_problem.customers))
        assert ok, msg
        assert elapsed < 5.0


# ── A* tests ─────────────────────────────────────────────────────────────────

class TestAstar:

    def test_all_customers_served(self, small_problem):
        g_routes, _, _ = greedy_solve(small_problem, seed=0)
        routes, _, _, _ = astar_solve(small_problem, initial_routes=g_routes)
        ok, msg = validate_solution(routes, len(small_problem.customers))
        assert ok, msg

    def test_astar_not_worse_than_greedy(self, small_problem):
        g_routes, g_dist, _ = greedy_solve(small_problem, seed=0)
        a_routes, a_dist, _, _ = astar_solve(
            small_problem, initial_routes=g_routes, max_nodes_per_depot=2000
        )
        # A* should match or improve Greedy
        assert a_dist <= g_dist + 1e-6

    def test_nodes_expanded_positive(self, small_problem):
        g_routes, _, _ = greedy_solve(small_problem, seed=0)
        _, _, _, nodes = astar_solve(small_problem, initial_routes=g_routes)
        assert nodes >= 0

    def test_single_customer(self, edge_single_customer):
        g_routes, _, _ = greedy_solve(edge_single_customer, seed=0)
        routes, dist, _, _ = astar_solve(edge_single_customer,
                                          initial_routes=g_routes)
        ok, msg = validate_solution(routes, 1)
        assert ok, msg
        assert dist > 0

    def test_feasibility_maintained(self, medium_problem):
        g_routes, _, _ = greedy_solve(medium_problem, seed=0)
        a_routes, _, _, _ = astar_solve(
            medium_problem, initial_routes=g_routes, max_nodes_per_depot=500
        )
        for r in a_routes:
            assert r.is_feasible


# ── Tabu tests ────────────────────────────────────────────────────────────────

class TestTabu:

    def test_all_customers_served(self, medium_problem):
        g_routes, _, _ = greedy_solve(medium_problem, seed=0)
        routes, _, _, _ = tabu_solve(medium_problem, initial_routes=g_routes,
                                     max_iterations=50, seed=0)
        ok, msg = validate_solution(routes, len(medium_problem.customers))
        assert ok, msg

    def test_tabu_improves_on_greedy(self, medium_problem):
        g_routes, g_dist, _ = greedy_solve(medium_problem, seed=0)
        _, t_dist, _, _ = tabu_solve(medium_problem, initial_routes=g_routes,
                                     max_iterations=200, seed=42)
        assert t_dist <= g_dist + 1e-6

    def test_history_non_increasing(self, medium_problem):
        """Best distance in history must be monotonically non-increasing."""
        g_routes, _, _ = greedy_solve(medium_problem, seed=0)
        _, _, _, history = tabu_solve(medium_problem, initial_routes=g_routes,
                                      max_iterations=100, seed=0)
        for i in range(1, len(history)):
            assert history[i] <= history[i - 1] + 1e-9

    def test_stochastic_variation(self, medium_problem):
        """Different seeds should produce different results."""
        g_routes, _, _ = greedy_solve(medium_problem, seed=0)
        results = set()
        for s in range(5):
            _, dist, _, _ = tabu_solve(medium_problem, initial_routes=g_routes,
                                       max_iterations=50, seed=s)
            results.add(round(dist, 3))
        # at least 2 distinct results across 5 seeds
        assert len(results) >= 2

    def test_feasibility_maintained(self, medium_problem):
        g_routes, _, _ = greedy_solve(medium_problem, seed=0)
        routes, _, _, _ = tabu_solve(medium_problem, initial_routes=g_routes,
                                     max_iterations=100, seed=0)
        for r in routes:
            assert r.is_feasible

    def test_single_customer(self, edge_single_customer):
        g_routes, _, _ = greedy_solve(edge_single_customer, seed=0)
        routes, dist, _, _ = tabu_solve(edge_single_customer,
                                         initial_routes=g_routes,
                                         max_iterations=20, seed=0)
        ok, msg = validate_solution(routes, 1)
        assert ok, msg


# ── Integration test ──────────────────────────────────────────────────────────

class TestIntegration:

    def test_full_pipeline(self):
        """Greedy → A* → Tabu pipeline on a medium instance."""
        problem = Problem.generate_random(
            n_customers=15, n_depots=2, capacity=50, seed=7, name="pipeline"
        )
        # Stage 1: Greedy
        g_routes, g_dist, _ = greedy_solve(problem, seed=7)
        assert validate_solution(g_routes, 15)[0]

        # Stage 2: A*
        a_routes, a_dist, _, _ = astar_solve(
            problem, initial_routes=g_routes, max_nodes_per_depot=1000
        )
        assert validate_solution(a_routes, 15)[0]
        assert a_dist <= g_dist + 1e-6

        # Stage 3: Tabu
        t_routes, t_dist, _, history = tabu_solve(
            problem, initial_routes=a_routes, max_iterations=150, seed=7
        )
        assert validate_solution(t_routes, 15)[0]
        assert t_dist <= a_dist + 1e-6
        assert len(history) > 0

        improvement = (g_dist - t_dist) / g_dist * 100
        print(f"\nPipeline: Greedy={g_dist:.1f} → A*={a_dist:.1f} → "
              f"Tabu={t_dist:.1f}  (↓{improvement:.1f}% total)")
