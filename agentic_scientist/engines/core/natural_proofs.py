from __future__ import annotations
import numpy as np
from typing import Callable
import itertools

class NaturalProofChecker:
    def __init__(self, n_inputs: int):
        self.n = n_inputs

    def check_constructivity(self, property_evaluator: Callable[[np.ndarray], bool]) -> bool:
        try:
            _ = property_evaluator(np.zeros(2**self.n, dtype=np.uint8))
            return True
        except Exception:
            return False

    def check_largeness(self, property_evaluator: Callable[[np.ndarray], bool], sample_size: int = 1000) -> float:
        true_count = 0
        if self.n <= 3:
            all_tables = list(itertools.product([0, 1], repeat=2**self.n))
            for table in all_tables:
                if property_evaluator(np.array(table, dtype=np.uint8)):
                    true_count += 1
            return true_count / len(all_tables)
        for _ in range(sample_size):
            random_truth_table = np.random.randint(0, 2, size=2**self.n, dtype=np.uint8)
            if property_evaluator(random_truth_table):
                true_count += 1
        return true_count / sample_size

    def check_usefulness(self, property_evaluator: Callable[[np.ndarray], bool], hard_function: np.ndarray) -> bool:
        return property_evaluator(hard_function)

    def run_redteam_analysis(self, property_candidate: Callable[[np.ndarray], bool], hard_func_test: np.ndarray) -> dict:
        constructive = self.check_constructivity(property_candidate)
        largeness_ratio = self.check_largeness(property_candidate)
        is_large = largeness_ratio >= (1.0 / (self.n ** 2))
        useful = self.check_usefulness(property_candidate, hard_func_test)
        is_natural = constructive and is_large and useful
        return {
            "constructivity": constructive,
            "largeness_ratio": largeness_ratio,
            "is_large": is_large,
            "usefulness": useful,
            "VERDICT_IS_NATURAL_PROOF": is_natural,
            "IMPLICATION": "Si VRAI, cette propriété NE PEUT PAS séparer P de NP sans casser la crypto." if is_natural else "Propriété non-naturelle."
        }
