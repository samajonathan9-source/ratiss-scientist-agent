# Injection et routage de la mise à jour V8.5 OMEGA
from engines.ricci_manifold_smoother import RicciManifoldSmoother
from engines.feynman_path_interferometer import FeynmanPathInterferometer
import numpy as np

def run_swan_black_pipeline(raw_high_dim_data: np.ndarray):
    print("[RATISS_SYSTEM] : Initialisation de la deuxième structure d'activation...")
    
    # 1. Instanciation des couches géométriques et physiques
    smoother = RicciManifoldSmoother(iterations=5, alpha=0.1)
    interferometer = FeynmanPathInterferometer()
    
    # 2. Phase 1 : Lissage et effondrement de la variété
    print("[RATISS_SYSTEM] : Activation du engine_ricci_manifold_smoother...")
    compressed_space, t_ricci = smoother.smooth(raw_high_dim_data)
    
    # 3. Phase 2 : Résolution instantanée par phase
    print("[RATISS_SYSTEM] : Activation du engine_feynman_path_interferometer...")
    optimal_route, t_feynman = interferometer.resolve(compressed_space)
    
    # 4. Calcul de la métrique finale sur l'espace d'origine
    total_distance = 0.0
    for i in range(len(optimal_route)):
        p1 = raw_high_dim_data[optimal_route[i]]
        p2 = raw_high_dim_data[optimal_route[(i + 1) % len(optimal_route)]]
        total_distance += np.linalg.norm(p1 - p2)
        
    print(f"[RATISS_SYSTEM] : Séquence terminée avec succès.")
    return {
        "status": "COMPUTED_STABLE",
        "ricci_time_ms": t_ricci,
        "feynman_time_ms": t_feynman,
        "total_distance_r7": total_distance,
        "route": optimal_route.tolist()
    }
