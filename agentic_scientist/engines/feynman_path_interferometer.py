import numpy as np
import time
from numba import njit, prange

@njit(parallel=True, fastmath=True)
def execute_feynman_interference(dist_matrix_3d: np.ndarray, n_cities: int) -> np.ndarray:
    """
    Phase 2 de l'Assemblage Cygne Noir compilée nativement (JIT).
    Traite les distances comme des phases complexes et élimine les interférences destructives.
    """
    # Matrice des amplitudes complexes : exp(i * D)
    # Pour des raisons de performance JIT, on sépare le calcul réel et imaginaire
    phase_real = np.cos(dist_matrix_3d)
    phase_imag = np.sin(dist_matrix_3d)
    
    # Initialisation du vecteur d'état fondamental
    optimal_route = np.zeros(n_cities, dtype=np.int64)
    visited = np.zeros(n_cities, dtype=np.int64)
    
    current_node = 0
    optimal_route[0] = current_node
    visited[current_node] = 1
    
    for step in range(1, n_cities):
        best_amplitude = -1e9
        next_node = -1
        
        for j in prange(n_cities):
            if visited[j] == 0:
                # Interférence constructive : maximiser l'amplitude de phase
                amplitude = phase_real[current_node, j] # Priorité à la cohérence de phase
                if amplitude > best_amplitude:
                    best_amplitude = amplitude
                    next_node = j
                    
        if next_node == -1: # Sécurité de rupture
            for j in range(n_cities):
                if visited[j] == 0:
                    next_node = j
                    break
                    
        optimal_route[step] = next_node
        visited[next_node] = 1
        current_node = next_node
        
    return optimal_route

class FeynmanPathInterferometer:
    def __init__(self):
        pass

    def resolve(self, compressed_coords: np.ndarray) -> tuple[np.ndarray, float]:
        start_time = time.time()
        n_cities = len(compressed_coords)
        
        # Calcul de la matrice de distance lissée en 3D
        dist_3d = np.linalg.norm(compressed_coords[:, np.newaxis, :] - compressed_coords[np.newaxis, :, :], axis=-1)
        
        # Exécution du noyau d'interférence accéléré
        route = execute_feynman_interference(dist_3d, n_cities)
        
        execution_time_ms = (time.time() - start_time) * 1000
        return route, execution_time_ms
