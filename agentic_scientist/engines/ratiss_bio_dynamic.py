import os
import numpy as np
import hashlib
import time
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import uvicorn

# Configuration du fichier memmap local (Souverain et dynamique)
MEMMAP_FILE_PATH = "ratiss_bio_dynamic.dat"
SHAPE = (30, 7)  # 30 penseurs, 7 dimensions (R7)
DTYPE = np.float64

# Initialisation du fichier à blanc (vide) s'il n'existe pas
if not os.path.exists(MEMMAP_FILE_PATH):
    with open(MEMMAP_FILE_PATH, "wb") as f:
        f.write(b"\x00" * (30 * 7 * 8))  # Allocation d'un espace totalement vide (zéroté)

# Ouverture du ledger local NumPy memmap
data_ledger = np.memmap(MEMMAP_FILE_PATH, dtype=DTYPE, mode='r+', shape=SHAPE)

# Schéma Pydantic pour recevoir n'importe quelle coordonnée et cible
class BioAnalysisRequest(BaseModel):
    coordinates: List[List[float]]
    target_dimension: Optional[float] = 2.61  # Optionnel, modifiable à la volée

def calculate_sha3_256(source_code: str) -> str:
    return hashlib.sha3_256(source_code.encode('utf-8')).hexdigest()

def sync_volt_omega_signature(signature: str):
    try:
        with open("volt_omega_audit.log", "a") as log_file:
            # Nanosecond precision timestamp for VOLT-Ω
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            log_file.write(f"[{timestamp}] [CHILD-SPAWN] [RATISS-BIO-DYNAMIC] HASH: {signature}\n")
        # Double ledger: binary NumPy
        np.save("volt_omega_ledger.npy", np.array([signature], dtype=object))
    except Exception as e:
        print(f"[RATISS-BIO-ERROR] Failed to sync VOLT-Ω signature: {e}")

# Calcul mathématique purement dynamique basé sur les données réelles injectées
def analyze_topology(matrix: np.ndarray) -> float:
    if np.all(matrix == 0):
        return 0.0  # Espace vide, aucune structure détectée
    
    # Calcul dynamique de la variance sur l'espace R7 pour extraire une signature unique
    variance_r7 = np.var(matrix, axis=1)
    mean_variance = np.mean(variance_r7)
    
    # Génération d'une dimension dynamique simulée à partir de tes données réelles
    # pour voir comment le système réagit à l'aléa
    dynamic_dim = 1.0 + (mean_variance % 2.0)
    return round(dynamic_dim, 2)

app = FastAPI(title="RATISS-BIO - Open Dynamic Engine")

@app.get("/p53/status")
async def get_status():
    # Permet de voir l'état actuel de la matrice en mémoire
    current_dim = analyze_topology(data_ledger)
    return {
        "status": "ready",
        "source_type": "synthetic_bio",
        "matrix_is_empty": bool(np.all(data_ledger == 0)),
        "current_computed_dimension": current_dim,
        "timestamp_ns": time.time_ns()
    }

@app.post("/p53/inject-and-analyze")
async def inject_and_analyze(payload: BioAnalysisRequest):
    input_array = np.array(payload.coordinates, dtype=DTYPE)
    
    if input_array.shape != SHAPE:
        raise HTTPException(
            status_code=400, 
            detail=f"Erreur structurelle : la matrice reçue a la forme {input_array.shape}, elle doit être de forme (30, 7)."
        )
    
    # Écriture instantanée des données aléatoires/neuves dans le memmap brut
    data_ledger[:] = input_array
    data_ledger.flush()
    
    # Calcul immédiat de la topologie sur ces nouvelles données
    computed_dim = analyze_topology(data_ledger)
    
    # Signature VOLT-Ω par exécution
    exec_signature = calculate_sha3_256(f"{time.time_ns()}-{computed_dim}")
    sync_volt_omega_signature(exec_signature)
    
    return {
        "status": "success",
        "message": "Données injectées et analysées à la volée",
        "computed_dimension": computed_dim,
        "target_dimension_requested": payload.target_dimension,
        "stable_match": bool(computed_dim == payload.target_dimension),
        "volt_omega_signature": exec_signature
    }

if __name__ == "__main__":
    # Verrouillage VOLT-Ω Initial
    try:
        current_file_path = Path(__file__).resolve()
        with open(current_file_path, "r", encoding="utf-8") as current_file:
            module_code = current_file.read()
        sha3_256_hash = calculate_sha3_256(module_code)
        sync_volt_omega_signature(sha3_256_hash)
    except Exception:
        sha3_256_hash = calculate_sha3_256("RATISS_BIO_DYNAMIC_FALLBACK")
        sync_volt_omega_signature(sha3_256_hash)
    
    port = int(os.environ.get("PORT", 8014))
    uvicorn.run(app, host="0.0.0.0", port=port)
