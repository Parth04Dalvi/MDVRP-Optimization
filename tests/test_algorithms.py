from src.greedy import greedy_vrp
from src.astar import astar_vrp
from src.utils import compute_distance_matrix

def run_test():
    # Sample nodes: depot + customers
    nodes = [
        (0, 0),   # depot (index 0)
        (2, 3),
        (5, 4),
        (1, 6),
        (7, 2)
    ]

    depot = 0
    customers = [1, 2, 3, 4]

    dist_matrix = compute_distance_matrix(nodes)

    print("Running Greedy...")
    g_route, g_cost = greedy_vrp(depot, customers, dist_matrix)
    print("Greedy Route:", g_route)
    print("Greedy Cost:", g_cost)

    print("\nRunning A*...")
    a_route, a_cost = astar_vrp(depot, customers, dist_matrix)
    print("A* Route:", a_route)
    print("A* Cost:", a_cost)


if __name__ == "__main__":
    run_test()
