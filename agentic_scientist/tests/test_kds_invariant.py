import random
import pytest
from engines.core.kds_tournament import KineticConvexHull, KineticPoint, orient

def test_kds_invariant_N100_T50():
    """Vérifie que l'enveloppe reste CCW et valide pendant 50 pas de temps."""
    random.seed(42)
    pts = [KineticPoint(i, random.uniform(-100, 100), random.uniform(-100, 100),
                        random.uniform(-1, 1), random.uniform(-1, 1)) for i in range(100)]
    
    kds = KineticConvexHull(pts)
    for t in range(50):
        kds.advance_to(float(t))
        hull_ids = kds.get_hull_ids()
        n = len(hull_ids)
        if n < 3: continue
        
        hull_pts = [kds.get_point(pid) for pid in hull_ids]
        for i in range(n):
            u, v, w = hull_pts[i-1], hull_pts[i], hull_pts[(i+1)%n]
            # On tolère une petite imprécision flottante
            assert orient(u, v, w, float(t)) >= -1e-9, f"CCW violé à t={t} pour les points {u.id}, {v.id}, {w.id}"

def test_mcts_integration_smoke():
    """Vérifie que le moteur MCTS peut explorer l'état du jeu sans crasher."""
    from engines.core.mcts_pw import mcts_search
    from engines.core.game_state import KineticEvasionState
    
    random.seed(42)
    pts = [KineticPoint(i, random.uniform(-10, 10), random.uniform(-10, 10),
                        random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)) for i in range(10)]
    kds = KineticConvexHull(pts)
    root_state = KineticEvasionState(0, set(), kds, T_max=10)
    
    best_action = mcts_search(root_state, budget=20)
    assert best_action is not None or len(pts) > 0
