# scripts/run_physical_quantum_test.py
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from connectors.universal_bridge import UniversalBridge
from connectors.schemas import Theory

def run_physical_tests():
    print("=========================================================")
    print("⚛️  RATISS CYPHER ODV - BENCHMARK ET MESURES PHYSIQUES  ⚛️")
    print("=========================================================\n")

    bridge = UniversalBridge()

    # 1. QUANDELA PHOTONIC (Ascella & Exqalibur)
    print("--- [1] QUANDELA PHOTONIQUE (Interféromètre à Séparateur de Faisceau BS) ---")
    theory_quandela_g = Theory(
        name="Intrication Photonique Tryperposition (GPU)",
        equations={"Psi": "|0,1> + |1,0>"},
        parameters={"shots": 10000},
        target="gpu"
    )
    res_q_g = bridge.send(theory_quandela_g)
    print("• Plateforme Target:", res_q_g.metadata["target"].upper(), "(sim:exqalibur)")
    print("• Nombre de Tirs (Shots):", res_q_g.data["shots"])
    print("• Distribution des Détections Photons:")
    for mode, count in res_q_g.data["results"].items():
        prob = (count / res_q_g.data["shots"]) * 100
        print(f"   - État {mode}: {count} tirs ({prob:.2f}%)")
    print("• Preuve Cryptographique ZK:", res_q_g.proof)
    print()

    theory_quandela_q = Theory(
        name="Intrication Photonique Tryperposition (QPU Ascella)",
        equations={"Psi": "|0,1> + |1,0>"},
        parameters={"shots": 10000},
        target="qpu"
    )
    res_q_q = bridge.send(theory_quandela_q)
    print("• Plateforme Target:", res_q_q.metadata["target"].upper(), "(qpu:ascella - Photonic QPU)")
    print("• Nombre de Tirs (Shots):", res_q_q.data["shots"])
    print("• Distribution des Détections Photons:")
    for mode, count in res_q_q.data["results"].items():
        prob = (count / res_q_q.data["shots"]) * 100
        print(f"   - État {mode}: {count} tirs ({prob:.2f}%)")
    print("• Preuve Cryptographique ZK:", res_q_q.proof)
    print("\n---------------------------------------------------------\n")

    # 2. IBM QUANTUM (Superconducteur / Bell State)
    print("--- [2] IBM QUANTUM SUPERCONDUCTEUR (État Maximalement Intriqué Bell |Φ+>) ---")
    theory_ibm = Theory(
        name="Circuit de Bell IBM Brisbane",
        equations={"Psi": "1/√2 (|00> + |11>)"},
        parameters={"shots": 10000, "platform": "ibm_brisbane"},
        target="ibm"
    )
    res_ibm = bridge.send(theory_ibm)
    print("• Backend Cible:", res_ibm.data["platform"])
    print("• Nombre de Tirs (Shots):", res_ibm.data["shots"])
    print("• Histogramme des Qubits Mesurés:")
    counts = res_ibm.data["data"]["counts"]
    for qubit_state, count in counts.items():
        prob = (count / res_ibm.data["shots"]) * 100
        print(f"   - Qubits |{qubit_state}>: {count} tirs ({prob:.2f}%)")
    print("• Ratio de Parité Intriquée:", f"{counts['00']/res_ibm.data['shots']:.4f} / {counts['11']/res_ibm.data['shots']:.4f}")
    print("• Preuve Cryptographique ZK:", res_ibm.proof)
    print("\n---------------------------------------------------------\n")

    # 3. PENNYLANE (Circuit Variational Hybride VQC)
    print("--- [3] PENNYLANE (Circuit Variatif Hybride & Observable Z) ---")
    theory_pl = Theory(
        name="VQC Optimization QNode",
        equations={"U(theta)": "RX(0.54) (x) RY(0.12) -> CNOT -> RZ(0.88)"},
        parameters={"wires": 2, "shots": 10000, "params": [0.54, 0.12, 0.88]},
        target="pennylane"
    )
    res_pl = bridge.send(theory_pl)
    vqc_data = res_pl.data["data"]
    print("• Framework Engine:", res_pl.data["platform"])
    print("• Qubits / Wires:", vqc_data["wires"])
    print("• Paramètres d'Angle (θ):", vqc_data["params"])
    print("• Probabilités Quantiques d'États:")
    states = ["|00>", "|01>", "|10>", "|11>"]
    for st, p in zip(states, vqc_data["probabilities"]):
        print(f"   - État {st}: {p*100:.2f}%")
    print("• Valeur Moyenne d'Observable <⟨σ_z⟩>:", vqc_data["expectation_value_z"])
    print("• Preuve Cryptographique ZK:", res_pl.proof)
    print("\n=========================================================")
    print("✅  MESURES PHYSIQUES QUANTIKES RATISS EXÉCUTÉES AVEC SUCCÈS")
    print("=========================================================")

if __name__ == "__main__":
    run_physical_tests()
