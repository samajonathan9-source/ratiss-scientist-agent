# tests/test_pennylane_connection.py
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from connectors.pennylane_bridge import PennyLaneBridge, PENNYLANE_AVAILABLE
from connectors.universal_bridge import UniversalBridge
from connectors.schemas import Theory


def test_pennylane_bridge():
    print("🔬 [RATISS] Test du Bridge PennyLane (pennylane_bridge.py)...")
    bridge = PennyLaneBridge()

    # Test Bell state execution
    bell_res = bridge.execute_bell_state(wires=2, shots=1000)
    print(f"Résultat Bell State: {bell_res}")
    assert bell_res["status"] == "success"
    assert "probabilities" in bell_res or "counts" in bell_res

    # Test Variational Quantum Circuit execution
    vqc_res = bridge.execute_variational_circuit(params=[0.54, 0.12, 0.88], wires=2, shots=1000)
    print(f"Résultat VQC: {vqc_res}")
    assert vqc_res["status"] == "success"
    print("✅ PennyLane Bridge fonctionnel")


def test_pennylane_universal_bridge():
    print("\n🔬 [RATISS] Test du Connecteur Universel avec PennyLane (TransformerP)...")
    ub = UniversalBridge()

    theory = Theory(
        name="Tryperposition Hybrid PennyLane",
        equations={"Psi": "Q (x) I (x) M"},
        parameters={"wires": 2, "shots": 10000, "platform": "default.qubit"},
        target="pennylane"
    )

    result = ub.send(theory)
    print(f"Résultat UniversalBridge (PennyLane): {result.data}")
    assert result.data["status"] == "success"
    assert result.data["shots"] == 10000
    print("✅ UniversalBridge PennyLane 100% Fonctionnel")


if __name__ == "__main__":
    test_pennylane_bridge()
    test_pennylane_universal_bridge()
