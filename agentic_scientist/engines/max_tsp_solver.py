import numpy as np
from scipy.optimize import linear_sum_assignment
import gudhi as gd
import umap
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class MaxTSP_TopologySolver:
    def __init__(self, n_cities=500):
        self.n_cities = n_cities

    def generate_cities(self, d=7):
        return np.random.rand(self.n_cities, d)

    def compute_distance_matrix(self, points):
        return np.linalg.norm(points[:, np.newaxis, :] - points[np.newaxis, :, :], axis=-1)

    def compute_persistence(self, points):
        rips = gd.RipsComplex(points=points, max_edge_length=0.8)
        st = rips.create_simplex_tree(max_dimension=2)
        return st.persistence()

    def bottleneck_distance(self, diag1, diag2):
        return gd.bottleneck_distance(diag1, diag2)

    def two_opt(self, route, dist_matrix, max_iterations=50):
        improved = True
        iterations = 0
        while improved and iterations < max_iterations:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1: continue
                    new_route = route[:i] + route[i:j][::-1] + route[j:]
                    old_dist = dist_matrix[route[i-1], route[i]] + dist_matrix[route[j-1], route[j]]
                    new_dist = dist_matrix[route[i-1], route[j-1]] + dist_matrix[route[i], route[j]]
                    if new_dist < old_dist - 1e-6:
                        route = new_route
                        improved = True
            iterations += 1
        return route

    def solve(self):
        cities = self.generate_cities()

        start = time.time()
        reducer = umap.UMAP(
            n_components=3,
            n_neighbors=40,
            min_dist=0.05,
            random_state=42,
            low_memory=True
        )
        compressed = reducer.fit_transform(cities)
        time_compress = (time.time() - start) * 1000

        diag_before = self.compute_persistence(cities)
        diag_after = self.compute_persistence(compressed)
        bottleneck = self.bottleneck_distance(diag_before, diag_after)
        total_persistence = sum(d[1][1] for d in diag_before)
        conservation_rate = (total_persistence - bottleneck) / total_persistence * 100 if total_persistence > 0 else 0

        start = time.time()
        dist_3D = self.compute_distance_matrix(compressed)
        row_ind, col_ind = linear_sum_assignment(dist_3D)
        route = col_ind.tolist()
        route = self.two_opt(route, dist_3D, max_iterations=30)
        min_distance = sum(dist_3D[route[i], route[(i+1) % len(route)]] for i in range(len(route)))
        time_tsp = (time.time() - start) * 1000

        print(f"Distance totale minimale: {min_distance:.2f}")
        print(f"Taux de conservation: {conservation_rate:.2f}%")
        print(f"Temps compression: {time_compress:.2f} ms")
        print(f"Temps TSP + 2-opt: {time_tsp:.2f} ms")
        
        return min_distance, conservation_rate

if __name__ == "__main__":
    solver = MaxTSP_TopologySolver(n_cities=500)
    solver.solve()
