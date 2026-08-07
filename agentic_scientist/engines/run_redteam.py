import sys
import os
import json
import numpy as np

# Ajout du chemin pour les imports relatifs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from attacks.circuit_lb_test import CircuitLowerBoundAttacker
from attacks.tsp_algo_test import TSPAlgoAttacker

def naive_density_property(truth_table: np.ndarray) -> bool:
    return bool(np.sum(truth_table) > (len(truth_table) // 2))

def naive_heuristic_tsp_candidate(D: np.ndarray) -> tuple[float, list[int]]:
    n = D.shape[0]
    tour = list(range(n))
    cost = sum(D[tour[i], tour[(i+1)%n]] for i in range(n))
    return float(cost), tour

def run_redteam_benchmark():
    report = {
        "circuit_verdict": None,
        "tsp_verdict": None,
        "circuit_details": {},
        "tsp_details": {}
    }
    
    # --- CIRCUIT TEST ---
    n_vars = 4
    circuit_attacker = CircuitLowerBoundAttacker(n_vars=n_vars)
    parity_tt = np.array([bin(i).count('1') % 2 for i in range(2**n_vars)], dtype=np.uint8)
    circuit_result = circuit_attacker.register_hypothesis(
        hypothesis_id="HYP-DEMO-001",
        target_class="AC0",
        target_function_truth_table=parity_tt,
        property_evaluator=naive_density_property,
        property_description="Majorité stricte",
        syntactic_hints=["sensitivity"]
    )
    
    report["circuit_verdict"] = circuit_result.verdict
    report["circuit_details"] = {
        "killed_by": [v.value for v in circuit_result.killed_by],
        "evidence": circuit_result.evidence,
        "is_natural": circuit_result.natural_proof_report["VERDICT_IS_NATURAL_PROOF"]
    }
    
    # --- TSP TEST ---
    tsp_attacker = TSPAlgoAttacker()
    tsp_report = tsp_attacker.benchmark_algorithm(naive_heuristic_tsp_candidate)
    
    report["tsp_verdict"] = tsp_report["verdict"]
    report["tsp_details"] = {
        "failures": tsp_report["failures"],
        "results": tsp_report["results"]
    }
    
    return report

if __name__ == "__main__":
    # Mode exécution directe pour test ou via subprocess
    try:
        final_report = run_redteam_benchmark()
        print(json.dumps(final_report, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
