from __future__ import annotations
from typing import Callable, List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np
from core.natural_proofs import NaturalProofChecker

class AttackVector(Enum):
    NATURAL_PROOF = "Natural Proof Barrier (Razborov-Rudich)"
    HASTAD_VIOLATION = "Violation Quantitative Håstad (AC0)"
    COUNTER_EXAMPLE_FOUND = "Contre-exemple explicite dans la classe cible"

@dataclass
class RedTeamResult:
    hypothesis_id: str
    target_class: str
    target_function: str
    property_description: str
    verdict: str
    killed_by: List[AttackVector]
    evidence: Dict[str, Any]
    natural_proof_report: Optional[Dict] = None

class CircuitLowerBoundAttacker:
    def __init__(self, n_vars: int = 6):
        self.n = n_vars
        self.np_checker = NaturalProofChecker(n_vars)

    def _is_parity(self, truth_table: np.ndarray) -> bool:
        expected = np.array([bin(i).count('1') % 2 for i in range(2**self.n)], dtype=np.uint8)
        return np.array_equal(truth_table, expected) or np.array_equal(truth_table, 1 - expected)

    def _find_counter_example_in_class(self, target_class: str, property_evaluator: Callable[[np.ndarray], bool]) -> Optional[Tuple[str, np.ndarray]]:
        target_class = target_class.upper()
        if target_class in ["AC0", "NC0"]:
            f_const0 = np.zeros(2**self.n, dtype=np.uint8)
            if property_evaluator(f_const0):
                return ("Constant_0_Function", f_const0)
            f_dict = np.array([1 if (i & 1) else 0 for i in range(2**self.n)], dtype=np.uint8)
            if property_evaluator(f_dict):
                return ("Dictator_Function_x0", f_dict)
            for k in range(1, min(self.n, 4)):
                mask = (1 << k) - 1
                f_and = np.array([1 if (i & mask) == mask else 0 for i in range(2**self.n)], dtype=np.uint8)
                if property_evaluator(f_and):
                    return (f"AND_Gate_k{k}", f_and)
        if target_class in ["TC0", "P/POLY"]:
            threshold = self.n // 2
            f_maj = np.array([1 if bin(i).count('1') >= threshold else 0 for i in range(2**self.n)], dtype=np.uint8)
            if property_evaluator(f_maj):
                return ("MAJORITY_Function", f_maj)
        return None

    def register_hypothesis(self, hypothesis_id: str, target_class: str, target_function_truth_table: np.ndarray, property_evaluator: Callable[[np.ndarray], bool], property_description: str, syntactic_hints: List[str] = None) -> RedTeamResult:
        killed_by = []
        evidence = {}
        np_report = self.np_checker.run_redteam_analysis(property_evaluator, target_function_truth_table)
        evidence["natural_proof_analysis"] = np_report
        if np_report["VERDICT_IS_NATURAL_PROOF"]:
            killed_by.append(AttackVector.NATURAL_PROOF)
        if target_class.upper() in ["AC0", "NC0"] and target_function_truth_table is not None:
            if self._is_parity(target_function_truth_table):
                killed_by.append(AttackVector.HASTAD_VIOLATION)
                evidence["hastad"] = "PARITY ∉ AC0 (Håstad 86). Ta preuve n'est pas valide dans cette classe."
        counter_example = self._find_counter_example_in_class(target_class, property_evaluator)
        if counter_example is not None:
            killed_by.append(AttackVector.COUNTER_EXAMPLE_FOUND)
            evidence["counter_example"] = {"message": f"Fonction {counter_example[0]} ∈ {target_class} mais C(f)=True. La propriété ne sépare pas."}
        if syntactic_hints:
            for hint in syntactic_hints:
                if hint in ["polynomial_method", "rank", "fourier_sparsity", "sensitivity"]:
                    if AttackVector.NATURAL_PROOF not in killed_by:
                        killed_by.append(AttackVector.NATURAL_PROOF)
                        evidence["syntactic_warning"] = f"Méthode '{hint}' historiquement bloquée par les Natural Proofs."
        verdict = "KILLED" if killed_by else "SURVIVED_BARRIERS"
        return RedTeamResult(
            hypothesis_id=hypothesis_id,
            target_class=target_class,
            target_function="PARITY" if self._is_parity(target_function_truth_table) else "CUSTOM",
            property_description=property_description,
            verdict=verdict,
            killed_by=killed_by,
            evidence=evidence,
            natural_proof_report=np_report
        )
