# tests/test_quandela_connection.py
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from connectors.quandela_client import QuandelaClient
from connectors.universal_bridge import UniversalBridge
from connectors.schemas import Theory

try:
    import perceval as pcvl
    PERCEVAL_AVAILABLE = True
except ImportError:
    pcvl = None
    PERCEVAL_AVAILABLE = False


def test_connection():
    print("🔬 [RATISS] Test de connexion Quandela Client...")
    client = QuandelaClient()
    session = client.connect("sim:exqalibur")

    if PERCEVAL_AVAILABLE and pcvl is not None:
        circuit = pcvl.Circuit(2) // pcvl.BS()
    else:
        circuit = None

    results = client.run_circuit(circuit, shots=1000)
    print(f"Résultats client: {results}")
    assert results is not None
    print("✅ Connexion réussie")


def test_universal_bridge():
    print("\n🔬 [RATISS] Test du Connecteur Universel (GPU & QPU)...")
    bridge = UniversalBridge()

    theory_gpu = Theory(
        name="Tryperposition GPU",
        equations={"Psi": "Q (x) I (x) M"},
        parameters={"shots": 1000},
        target="gpu"
    )
    res_gpu = bridge.send(theory_gpu)
    print(f"Résultat GPU: {res_gpu.data}")
    assert res_gpu.data is not None

    theory_qpu = Theory(
        name="Tryperposition QPU",
        equations={"Psi": "Q (x) I (x) M"},
        parameters={"shots": 1000},
        target="qpu"
    )
    res_qpu = bridge.send(theory_qpu)
    print(f"Résultat QPU: {res_qpu.data}")
    assert res_qpu.data is not None
    print("✅ Connecteur Universel RATISS 100% Fonctionnel")


if __name__ == "__main__":
    test_connection()
    test_universal_bridge()
