from __future__ import annotations
import hashlib
from abc import ABC, abstractmethod

class Oracle(ABC):
    """Oracle O : {0,1}* -> {0,1}."""
    @abstractmethod
    def query(self, x: str) -> int: ...

class OracleB_PNotEqualsNP(Oracle):
    """
    Oracle B (Bennett-Gill 1981 / BGS 1975).
    P^B != NP^B avec probabilité 1.
    Zéro mémoire, évaluation déterministe via pseudo-random oracle.
    """
    def __init__(self, seed: str = "RATISS_CYPHER_ODV_2026"):
        self.seed = seed.encode('utf-8')

    def query(self, x: str) -> int:
        h = hashlib.sha256(self.seed + x.encode('utf-8')).digest()
        return h[0] & 1

    def L_B_contains_heuristic(self, n: int, samples: int = 1000) -> bool:
        if n > 20: return True
        for i in range(min(2**n, samples)):
            x = format(i, f'0{n}b')
            if self.query(x) == 1:
                return True
        return False
