import math

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def compute_distance_matrix(nodes):
    n = len(nodes)
    dist = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dist[i][j] = euclidean_distance(nodes[i], nodes[j])
    return dist

def route_distance(route, dist_matrix):
    total = 0
    for i in range(len(route)-1):
        total += dist_matrix[route[i]][route[i+1]]
    return total
