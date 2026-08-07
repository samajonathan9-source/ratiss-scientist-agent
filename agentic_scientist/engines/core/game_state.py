from __future__ import annotations
from typing import Set, List, Tuple, Any
import math
import copy
from .kds_tournament import KineticConvexHull, KineticPoint

class KineticEvasionState:
    """
    État du jeu DYNAMIC KINETIC CONVEX HULL EVASION.
    Défenseur (MCTS) = Max player, Adversaire (Heuristique) = Min player.
    """
    def __init__(self, t: int, frozen: Set[int], kds: KineticConvexHull, T_max: int = 100):
        self.t = t
        self.frozen = frozen # IDs des points gelés
        self.kds = kds
        self.T_max = T_max
        self._hull_ids = self.kds.get_hull_ids()
        self._hull_area = self.kds.get_hull_area()

    def is_terminal(self) -> bool:
        return self.t >= self.T_max or len(self._hull_ids) <= 2

    def get_legal_actions(self) -> List[int]:
        """Actions du défenseur : geler un point sur l'enveloppe non encore gelé."""
        return [pid for pid in self._hull_ids if pid not in self.frozen]

    def apply(self, action: int) -> 'KineticEvasionState':
        """Gèle le point, avance le temps et laisse l'adversaire supprimer un point."""
        new_frozen = set(self.frozen)
        if action != -1:
            new_frozen.add(action)
        
        # Copie profonde du moteur KDS pour la simulation
        new_kds = self.kds.copy()
        
        # Tour de l'adversaire : supprime un sommet de l'enveloppe qui maximise la perte d'aire
        adv_choice = self._adversary_choice()
        if adv_choice != -1:
            new_kds.remove_point(adv_choice)
            
        new_kds.advance_to(self.t + 1)
        return KineticEvasionState(self.t + 1, new_frozen, new_kds, self.T_max)

    def _adversary_choice(self) -> int:
        """Politique Min : l'adversaire supprime le point qui réduit le plus l'aire, s'il n'est pas gelé."""
        best_v, max_loss = -1, -1.0
        for vid in self._hull_ids:
            if vid in self.frozen: continue
            loss = self.kds.area_loss_if_removed(vid)
            if loss > max_loss:
                max_loss, best_v = loss, vid
        return best_v

    def value(self) -> float:
        """Score : on cherche à maximiser l'aire négative (minimiser l'aire réelle)."""
        return -self._hull_area

    def get_rollout_state(self) -> 'KineticEvasionState':
        """Heuristique gloutonne pour le rollout MCTS."""
        actions = self.get_legal_actions()
        if not actions:
            return self.apply(-1)
        # Gèle le point avec le meilleur Shapley Score approximé
        best_action = max(actions, key=lambda pid: self._shapley_score(pid))
        return self.apply(best_action)

    def _shapley_score(self, pid: int) -> float:
        """Contribution marginale future. Plus le point est central au futur, plus il est critique."""
        p = self.kds.get_point(pid)
        future_pos = p.pos(self.t + 5)
        cx, cy = self.kds.get_centroid()
        # On préfère geler les points qui resteront proches du centre de masse
        return -math.dist(future_pos, (cx, cy))
