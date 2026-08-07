import heapq
import math
import numpy as np
import copy
from typing import List, Tuple, Set, Dict, Optional

class KineticPoint:
    __slots__ = ('id', 'x', 'y', 'vx', 'vy')
    def __init__(self, id: int, x0: float, y0: float, vx: float, vy: float):
        self.id = id
        self.x = x0
        self.y = y0
        self.vx = vx
        self.vy = vy

    def pos(self, t: float) -> Tuple[float, float]:
        return self.x + self.vx * t, self.y + self.vy * t

def orient(p: KineticPoint, q: KineticPoint, r: KineticPoint, t: float) -> float:
    px, py = p.pos(t); qx, qy = q.pos(t); rx, ry = r.pos(t)
    return (qx - px) * (ry - py) - (qy - py) * (rx - px)

class KineticConvexHull:
    """Moteur cinétique itératif (Andrew's Monotone Chain) avec support de suppression."""
    def __init__(self, points: List[KineticPoint]):
        self.t = 0.0
        self.points_dict = {p.id: p for p in points}
        self.active_ids = set(self.points_dict.keys())
        self.hull_ids = []
        self._recompute_hull()

    def _recompute_hull(self):
        pts = [self.points_dict[pid] for pid in self.active_ids]
        n = len(pts)
        if n <= 2:
            self.hull_ids = [p.id for p in pts]
            return

        # Tri temporel à t
        sorted_pts = sorted(pts, key=lambda p: (p.pos(self.t)[0], p.pos(self.t)[1]))
        
        lower = []
        for p in sorted_pts:
            while len(lower) >= 2 and orient(lower[-2], lower[-1], p, self.t) <= 0:
                lower.pop()
            lower.append(p)
        
        upper = []
        for p in reversed(sorted_pts):
            while len(upper) >= 2 and orient(upper[-2], upper[-1], p, self.t) <= 0:
                upper.pop()
            upper.append(p)
            
        full_hull = lower[:-1] + upper[:-1]
        self.hull_ids = [p.id for p in full_hull]

    def advance_to(self, t_new: float):
        self.t = t_new
        self._recompute_hull()

    def remove_point(self, pid: int):
        if pid in self.active_ids:
            self.active_ids.remove(pid)
            self._recompute_hull()

    def get_hull_ids(self) -> List[int]:
        return self.hull_ids

    def get_hull_area(self) -> float:
        h_pts = [self.points_dict[pid] for pid in self.hull_ids]
        if len(h_pts) < 3: return 0.0
        s = 0.0
        for i in range(len(h_pts)):
            p1 = h_pts[i]
            p2 = h_pts[(i + 1) % len(h_pts)]
            x1, y1 = p1.pos(self.t)
            x2, y2 = p2.pos(self.t)
            s += (x1 * y2 - x2 * y1)
        return abs(s) / 2.0

    def area_loss_if_removed(self, pid: int) -> float:
        """Heuristique ΔArea."""
        if pid not in self.hull_ids or len(self.hull_ids) < 3: return 0.0
        idx = self.hull_ids.index(pid)
        prev_id = self.hull_ids[idx - 1]
        next_id = self.hull_ids[(idx + 1) % len(self.hull_ids)]
        
        p = self.points_dict[pid]
        prev_p = self.points_dict[prev_id]
        next_p = self.points_dict[next_id]
        
        # Aire du triangle formé par pid et ses voisins sur l'enveloppe
        return abs(orient(prev_p, p, next_p, self.t)) / 2.0

    def get_point(self, pid: int) -> KineticPoint:
        return self.points_dict[pid]

    def get_centroid(self) -> Tuple[float, float]:
        pts = [self.points_dict[pid].pos(self.t) for pid in self.active_ids]
        if not pts: return (0.0, 0.0)
        return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))

    def copy(self) -> 'KineticConvexHull':
        new_kds = KineticConvexHull([])
        new_kds.t = self.t
        new_kds.points_dict = self.points_dict # Immutable points
        new_kds.active_ids = set(self.active_ids)
        new_kds.hull_ids = list(self.hull_ids)
        return new_kds
