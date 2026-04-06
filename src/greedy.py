from utils import route_distance

def greedy_vrp(depot_index, customers, dist_matrix):
    unvisited = set(customers)
    route = [depot_index]
    current = depot_index

    while unvisited:
        next_customer = min(unvisited, key=lambda c: dist_matrix[current][c])
        route.append(next_customer)
        unvisited.remove(next_customer)
        current = next_customer

    route.append(depot_index)
    return route, route_distance(route, dist_matrix)
