import heapq
from mst import mst_cost
from utils import route_distance

class State:
    def __init__(self, current, visited, path, cost):
        self.current = current
        self.visited = visited
        self.path = path
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost


def astar_vrp(depot, customers, dist_matrix):
    initial = State(depot, set([depot]), [depot], 0)
    pq = []
    heapq.heappush(pq, (0, initial))

    best_cost = float('inf')
    best_path = None

    while pq:
        f, state = heapq.heappop(pq)

        if len(state.visited) == len(customers) + 1:
            final_path = state.path + [depot]
            total_cost = route_distance(final_path, dist_matrix)
            if total_cost < best_cost:
                best_cost = total_cost
                best_path = final_path
            continue

        for c in customers:
            if c not in state.visited:
                new_visited = state.visited.copy()
                new_visited.add(c)

                new_path = state.path + [c]
                g = state.cost + dist_matrix[state.current][c]

                remaining = [x for x in customers if x not in new_visited]
                h = mst_cost(remaining + [c], dist_matrix) if remaining else 0

                new_state = State(c, new_visited, new_path, g)
                heapq.heappush(pq, (g + h, new_state))

    return best_path, best_cost
