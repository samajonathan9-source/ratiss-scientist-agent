# tests/test_ibm_connection.py
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from connectors.ibm_client import IBMClient
from connectors.universal_bridge import UniversalBridge
from connectors.schemas import Theory

try:
    from qiskit import QuantumCircuit
    QISKIT_AVAILABLE = True
except ImportError:
    QuantumCircuit = None
    QISKIT_AVAILABLE = False


def test_ibm_connection():
    print("🔬 [RATISS] Test de connexion IBM Client...")
    client = IBMClient()

    # Tester le simulateur
    print("🧪 Test du simulateur IBM...")
    client.connect("ibmq_qasm_simulator")

    if QISKIT_AVAILABLE and QuantumCircuit is not None:
        circuit = QuantumCircuit(2, 2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
    else:
        circuit = None

    results = client.run_circuit(circuit, shots=1024)
    print(f"Résultats simulateur: {results}")
    assert results is not None
    print("✅ Connexion simulateur réussie")


def test_ibm_universal_bridge():
    print("\n🔬 [RATISS] Test du Connecteur Universel avec IBM Quantum...")
    bridge = UniversalBridge()

    # Envoyer une requête sur simulateur IBM
    theory_sim = Theory(
        name="Tryperposition Bell State Simulator",
        equations={"Psi": "Q (x) I (x) M"},
        parameters={"shots": 10000, "platform": "ibmq_qasm_simulator"},
        target="ibm"
    )
    result_sim = bridge.send(theory_sim)
    print(f"Résultat Simulateur Bridge: {result_sim.data}")
    assert result_sim.data is not None

    # Envoyer sur QPU réelle (IBM Brisbane)
    theory_qpu = Theory(
        name="Tryperposition QPU Brisbane",
        equations={"Psi": "Q (x) I (x) M"},
        parameters={"shots": 10000, "platform": "ibm_brisbane"},
        target="ibm"
    )
    result_qpu = bridge.send(theory_qpu)
    print(f"Résultat QPU Brisbane Bridge: {result_qpu.data}")
    assert result_qpu.data is not None

    print("✅ Test Connecteur IBM Quantum réussi avec succès !")


if __name__ == "__main__":
    test_ibm_connection()
    test_ibm_universal_bridge()
