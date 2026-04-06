
from utils import euclidean_distance

def mst_cost(nodes, dist_matrix):
    if len(nodes) <= 1:
        return 0

    visited = set([nodes[0]])
    cost = 0

    while len(visited) < len(nodes):
        min_edge = float('inf')
        next_node = None

        for u in visited:
            for v in nodes:
                if v not in visited:
                    if dist_matrix[u][v] < min_edge:
                        min_edge = dist_matrix[u][v]
                        next_node = v

        cost += min_edge
        visited.add(next_node)

    return cost
