import sys
import os
import json
import numpy as np

# Ajout du chemin pour les imports relatifs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from attacks.circuit_lb_test import CircuitLowerBoundAttacker
from attacks.tsp_algo_test import TSPAlgoAttacker

def run_specific_redteam(request_data):
    # Cette fonction pourra évoluer pour traiter des requêtes précises
    # Pour l'instant, elle lance le benchmark complet
    from run_redteam import run_redteam_benchmark
    return run_redteam_benchmark()

if __name__ == "__main__":
    try:
        input_data = {}
        if len(sys.argv) > 1:
            input_data = json.loads(sys.argv[1])
        
        result = run_specific_redteam(input_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
