import numpy as np
import gudhi as gd
from sklearn.manifold import SpectralEmbedding
import time

class RicciManifoldSmoother:
    """
    Phase 1 de l'Assemblage Cygne Noir.
    Calcule la courbure locale (approximation discrète de Bakry-Émery) 
    et applique un lissage géodésique par déformation de la matrice de distance.
    """
    def __init__(self, iterations=5, alpha=0.1):
        self.iterations = iterations
        self.alpha = alpha # Pas du flot de Ricci

    def compute_bakry_emery_curvature(self, dist_matrix: np.ndarray) -> np.ndarray:
        """Estime la courbure discrète basée sur le Laplacien du graphe."""
        # Calcul de la matrice de contiguïté floue (noyau gaussien adaptatif)
        sigma = np.median(dist_matrix) if np.median(dist_matrix) > 0 else 1.0
        W = np.exp(- (dist_matrix ** 2) / (2 * (sigma ** 2)))
        np.fill_diagonal(W, 0)
        
        # Degrés et Laplacien
        D = np.sum(W, axis=1)
        D_inv = np.zeros_like(D)
        D_inv[D > 0] = 1.0 / D[D > 0]
        P = W * D_inv[:, np.newaxis] # Matrice de transition
        
        # Approximation de la courbure de Bakry-Émery locale (I - P^2)
        curvature = np.ones_like(dist_matrix) - np.dot(P, P)
        return curvature

    def smooth(self, points: np.ndarray) -> tuple[np.ndarray, float]:
        start_time = time.time()
        dist_matrix = np.linalg.norm(points[:, np.newaxis, :] - points[np.newaxis, :, :], axis=-1)
        
        # Application itérative du flot de Ricci discret
        current_dist = dist_matrix.copy()
        for _ in range(self.iterations):
            K = self.compute_bakry_emery_curvature(current_dist)
            # Déformation de la métrique : d_new = d_old * exp(-alpha * K)
            current_dist = current_dist * np.exp(-self.alpha * K)
            np.fill_diagonal(current_dist, 0)

        # Réduction dimensionnelle topologique via Spectral Embedding (Diffusion Maps proxy)
        embedder = SpectralEmbedding(n_components=3, affinity='precomputed', random_state=42)
        # Transformation de la distance lissée en affinité
        affinity_matrix = np.exp(-current_dist / np.max(current_dist))
        compressed_coords = embedder.fit_transform(affinity_matrix)
        
        execution_time_ms = (time.time() - start_time) * 1000
        return compressed_coords, execution_time_ms
