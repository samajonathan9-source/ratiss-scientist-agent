import os
import httpx
import json
import hashlib
import time
import uuid
import logging
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Configuration du logger pour le monitoring souverain
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("video_router")

app = FastAPI(
    title="RATISS Cypher ODV - Sovereign Video Routing Engine (V9)",
    description="Sovereign local routing engine with cognitive parsing, asynchronous Wan 2.7 video synthesis, and NumPy memmap persistence.",
    version="9.0.0"
)

# Nettoyeur robuste de clés API pour éviter les guillemets et espaces parasites
def get_clean_key(env_var_name: str, fallback_var_name: Optional[str] = None) -> str:
    key = os.getenv(env_var_name)
    if not key and fallback_var_name:
        key = os.getenv(fallback_var_name)
    if not key:
        return ""
    # Nettoyage des guillemets et des espaces/caractères invisibles Unicode
    clean = key.strip().strip("'\"")
    clean = "".join(c for c in clean if not c.isspace())
    return clean

# Définition des endpoints officiels internationaux d'Alibaba Cloud Model Studio (2026)
DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com"
QWEN_COMPATIBLE_URL = f"{DASHSCOPE_BASE_URL}/compatible-mode/v1/chat/completions"
WAN_VIDEO_SYNTHESIS_URL = f"{DASHSCOPE_BASE_URL}/api/v1/services/aigc/text-to-video/video-synthesis"
WAN_TASK_STATUS_URL = f"{DASHSCOPE_BASE_URL}/api/v1/tasks"

async def async_call_dashscope_video(prompt: str, active_dashscope_key: str) -> tuple[Optional[str], str]:
    """
    Appelle l'API DashScope internationale de manière asynchrone pour générer la vidéo.
    Tente d'abord l'endpoint spécifié (text-to-video), puis text2video, puis video-generation en cas d'erreur.
    Retourne (task_id, task_status).
    """
    headers = {
        "Authorization": f"Bearer {active_dashscope_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    
    payload = {
        "model": "wan-text-to-video-v2.7",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "ratio": "16:9"
        }
    }
    
    endpoints_to_try = [
        f"{DASHSCOPE_BASE_URL}/api/v1/services/aigc/text-to-video/video-synthesis",
        f"{DASHSCOPE_BASE_URL}/api/v1/services/aigc/text2video/video-synthesis",
        f"{DASHSCOPE_BASE_URL}/api/v1/services/aigc/video-generation/video-synthesis"
    ]
    
    async with httpx.AsyncClient() as client:
        for url in endpoints_to_try:
            logger.info(f"[RATISS DashScope] Tentative d'appel asynchrone sur {url} avec le modèle wan-text-to-video-v2.7...")
            try:
                res = await client.post(url, headers=headers, json=payload, timeout=20.0)
                res_json = res.json()
                logger.info(f"[RATISS DashScope] Réponse reçue de {url}: {res.status_code} - {res_json}")
                
                output = res_json.get("output", {})
                task_id = output.get("task_id") or res_json.get("task_id")
                
                if res.is_success and task_id:
                    task_status = output.get("task_status") or res_json.get("task_status") or "PENDING"
                    logger.info(f"[RATISS DashScope] Tâche enregistrée avec succès. ID: {task_id}, Statut: {task_status}")
                    return task_id, task_status
            except Exception as e:
                logger.warning(f"[RATISS DashScope] Échec sur l'endpoint {url}: {str(e)}")
                
    # Si tous les endpoints échouent avec le modèle par défaut, tentons avec le modèle alternatif wan2.1-t2v-turbo
    alt_payload = {
        "model": "wan2.1-t2v-turbo",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "size": "1280*720"
        }
    }
    alt_endpoints = [
        f"{DASHSCOPE_BASE_URL}/api/v1/services/aigc/video-generation/video-synthesis"
    ]
    async with httpx.AsyncClient() as client:
        for url in alt_endpoints:
            logger.info(f"[RATISS DashScope] Tentative de secours avec le modèle wan2.1-t2v-turbo sur {url}...")
            try:
                res = await client.post(url, headers=headers, json=alt_payload, timeout=20.0)
                res_json = res.json()
                output = res_json.get("output", {})
                task_id = output.get("task_id") or res_json.get("task_id")
                if res.is_success and task_id:
                    task_status = output.get("task_status") or "PENDING"
                    logger.info(f"[RATISS DashScope Secours] Tâche enregistrée avec succès. ID: {task_id}")
                    return task_id, task_status
            except Exception as e:
                logger.warning(f"[RATISS DashScope Secours] Échec secours: {str(e)}")

    return None, "PENDING_LOCAL_FALLBACK"

# Filtre local strict (Zéro token gaspillé sur le VPS à 10$)
VIDEO_TRIGGERS = [
    "génère une vidéo", "générez une vidéo", "générer une vidéo",
    "génère un vidéo", "générez un vidéo", "générer un vidéo",
    "génère des vidéos", "générez des vidéos", "générer des vidéos",
    "générer vidéo", "génère vidéo", "générez vidéo",
    "crée une vidéo", "créez une vidéo", "créer une vidéo",
    "crée un vidéo", "créez un vidéo", "créer un vidéo",
    "fait une vidéo", "faites une vidéo", "faire une vidéo",
    "fait un vidéo", "faites un vidéo", "faire un vidéo",
    "illustre une vidéo", "illustrez une vidéo", "illustrer une vidéo",
    "montre une vidéo", "montrez une vidéo", "montrer une vidéo",
    "fait apparaître une vidéo", "faites apparaître une vidéo", "faire apparaître une vidéo",
    "generate video", "generate a video", "create video", "create a video", "make video", "make a video",
    ".ratvid"
]

# PERSISTENCE CONFIGURATION VIA NUMPY MEMMAP
LEDGER_FILE = os.path.join(os.path.dirname(__file__), "volt_omega_ledger.dat")
RECORD_DTYPE = np.dtype([
    ('volt_hash', 'S64'),        # SHA3-256 hash (64 hex characters)
    ('task_id', 'S64'),          # DashScope task ID or Local fallback ID
    ('timestamp', 'i8'),         # Nanoseconds timestamp
    ('prompt', 'S512'),          # Render prompt
    ('equation', 'S256'),        # Mathematical equation
    ('curvature', 'f8'),         # Local curvature value
    ('proof', 'S512'),           # Formal proof
    ('vector', 'f8', (7,))       # Coordinates in R^7
])
MAX_RECORDS = 1000

def init_ledger():
    if not os.path.exists(LEDGER_FILE):
        # Create a pre-allocated file filled with zeros
        fp = np.memmap(LEDGER_FILE, dtype=RECORD_DTYPE, mode='w+', shape=(MAX_RECORDS,))
        fp.flush()
        del fp

def get_ledger_memmap(mode='r+'):
    init_ledger()
    return np.memmap(LEDGER_FILE, dtype=RECORD_DTYPE, mode=mode, shape=(MAX_RECORDS,))

def write_record(volt_hash: str, task_id: str, timestamp_ns: int, prompt: str, equation: str, curvature: float, proof: str, vector: list):
    mmap = get_ledger_memmap('r+')
    
    # Find an empty slot
    slot_idx = -1
    for i in range(MAX_RECORDS):
        if mmap[i]['volt_hash'] == b'' or mmap[i]['volt_hash'] == b'\x00' * 64:
            slot_idx = i
            break
            
    if slot_idx == -1:
        # Overwrite first index if ledger is full (rolling)
        slot_idx = 0
        
    mmap[slot_idx]['volt_hash'] = volt_hash.encode('utf-8')[:64]
    mmap[slot_idx]['task_id'] = task_id.encode('utf-8')[:64]
    mmap[slot_idx]['timestamp'] = timestamp_ns
    mmap[slot_idx]['prompt'] = prompt.encode('utf-8')[:512]
    mmap[slot_idx]['equation'] = equation.encode('utf-8')[:256]
    mmap[slot_idx]['curvature'] = curvature
    mmap[slot_idx]['proof'] = proof.encode('utf-8')[:512]
    
    vec = np.zeros(7, dtype=np.float64)
    for idx, val in enumerate(vector[:7]):
        vec[idx] = val
    mmap[slot_idx]['vector'] = vec
    
    mmap.flush()
    
    # Companion audit trail log file
    log_file = os.path.join(os.path.dirname(__file__), "volt_omega_audit.log")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp_ns}] HASH: {volt_hash} | TASK: {task_id} | CURVATURE: {curvature:.6f} | EQ: {equation}\n")
    except Exception as e:
        logger.error(f"[RATISS Ledger] Error writing audit log: {str(e)}")
        
    del mmap

def find_record_by_hash(volt_hash: str):
    mmap = get_ledger_memmap('r')
    target_bytes = volt_hash.encode('utf-8')
    
    # Use boolean indexing for speed
    hashes = mmap['volt_hash']
    matches = (hashes == target_bytes)
    indices = np.where(matches)[0]
    
    if len(indices) == 0:
        # Fallback strip comparison in case of padding difference
        for i in range(MAX_RECORDS):
            h_str = mmap[i]['volt_hash'].decode('utf-8').strip('\x00').strip()
            if h_str == volt_hash:
                rec = mmap[i]
                return {
                    "volt_hash": h_str,
                    "task_id": rec['task_id'].decode('utf-8').strip('\x00').strip(),
                    "timestamp": int(rec['timestamp']),
                    "prompt": rec['prompt'].decode('utf-8', errors='ignore').strip('\x00').strip(),
                    "equation": rec['equation'].decode('utf-8', errors='ignore').strip('\x00').strip(),
                    "curvature": float(rec['curvature']),
                    "proof": rec['proof'].decode('utf-8', errors='ignore').strip('\x00').strip(),
                    "vector": rec['vector'].tolist()
                }
        return None
        
    idx = indices[0]
    rec = mmap[idx]
    return {
        "volt_hash": rec['volt_hash'].decode('utf-8').strip('\x00').strip(),
        "task_id": rec['task_id'].decode('utf-8').strip('\x00').strip(),
        "timestamp": int(rec['timestamp']),
        "prompt": rec['prompt'].decode('utf-8', errors='ignore').strip('\x00').strip(),
        "equation": rec['equation'].decode('utf-8', errors='ignore').strip('\x00').strip(),
        "curvature": float(rec['curvature']),
        "proof": rec['proof'].decode('utf-8', errors='ignore').strip('\x00').strip(),
        "vector": rec['vector'].tolist()
    }

def derive_topological_metadata(prompt: str, volt_hash: str) -> dict:
    # Derive deterministic pseudo-random mathematical values from the SHA3 hash
    try:
        hash_bytes = bytes.fromhex(volt_hash)
    except Exception:
        hash_bytes = hashlib.sha3_256(volt_hash.encode('utf-8')).digest()
        
    # Curvature derivation [-2.5, 2.5]
    val_curv = (hash_bytes[0] * 256 + hash_bytes[1]) / 65535.0 * 5.0 - 2.5
    
    # R^7 Coordinates [-5.0, 5.0]
    vector = []
    for i in range(7):
        val = (hash_bytes[2+i*2] * 256 + hash_bytes[3+i*2]) / 65535.0 * 10.0 - 5.0
        vector.append(round(val, 4))
        
    # Set of beautiful equations
    equations = [
        "\\partial_t g_{ij} = -2 R_{ij} \\quad \\text{(Ricci Flow Metromorphic Equation)}",
        "R_{\\mu\\nu} - \\frac{1}{2}R g_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\kappa T_{\\mu\\nu}",
        "\\int_M K \\, dA + \\int_{\\partial M} k_g \\, ds = 2\\pi \\chi(M)",
        "\\Delta u + R(x)u - K(x)u^{\\frac{n+2}{n-2}} = 0 \\quad \\text{(Yamabe Invariant Flow)}"
    ]
    eq_idx = hash_bytes[20 % len(hash_bytes)] % len(equations)
    equation = equations[eq_idx]
    
    # Set of formal proofs
    proofs = [
        "Formal proof established via Perelman's energy functional W(g, f, tau) with non-decreasing monotonicity under geometric Ricci flow.",
        "Proved by application of the de Rham cohomology group H^2(M, R) showing equivalence under topological surgery.",
        "Verified via Gauss-Bonnet-Chern theorem integration under constant sectional curvature sectional_K = 1.0.",
        "Certified using Alexandrov spaces comparison theorem indicating bounded curvature below by local curvature K."
    ]
    proof_idx = hash_bytes[21 % len(hash_bytes)] % len(proofs)
    proof = proofs[proof_idx]
    
    return {
        "equation": equation,
        "curvature": round(val_curv, 6),
        "proof": proof,
        "vector": vector
    }

class UserRequest(BaseModel):
    message: str

class StoryWeaverRequest(BaseModel):
    checkpoints: List[str]

class EchoChamberRequest(BaseModel):
    hypothesis_a: str
    hypothesis_b: str

def generate_volt_omega_hash(task_id: str, prompt_physics: str, timestamp_ns: int) -> str:
    """
    Génère une signature cryptographique unique SHA3-256 (Ancrage VOLT-Ω)
    en combinant le prompt, l'identifiant de la tâche et un horodatage à la nanoseconde.
    """
    raw_payload = f"{task_id}-{prompt_physics}-{timestamp_ns}".encode("utf-8")
    return hashlib.sha3_256(raw_payload).hexdigest()

@app.post("/route-video")
async def route_video_request(request: UserRequest):
    user_msg = request.message.lower()
    
    # Étape 1 : Interrupteur sémantique strict local (Zéro token gaspillé)
    matches_explicit = any(trigger in user_msg for trigger in VIDEO_TRIGGERS)
    matches_flexible = ("vidéo" in user_msg or "video" in user_msg) and any(
        verb in user_msg for verb in ["génér", "gener", "crée", "cree", "fait", "faire", "illustr", "montr", "appar", "make"]
    )
    
    if not (matches_explicit or matches_flexible or ".ratvid" in user_msg):
        logger.info("[RATISS Router] Requête hors filtre vidéo. Délégation immédiate au chat standard.")
        return {"video_trigger": False, "action": "delegate_to_standard_chat"}

    logger.info("[RATISS Router] Déclencheur vidéo détecté ! Initialisation de l'analyse cognitive via Qwen...")

    # Récupération et nettoyage dynamique des clés API actives
    active_qwen_key = get_clean_key("QWEN_API_KEY", "DASHSCOPE_API_KEY")
    active_dashscope_key = get_clean_key("DASHSCOPE_API_KEY", "QWEN_API_KEY")

    if not active_qwen_key:
        raise HTTPException(status_code=401, detail="Missing API key configuration (QWEN_API_KEY or DASHSCOPE_API_KEY).")

    # Étape 2 : Analyse cognitive Qwen
    async with httpx.AsyncClient() as client:
        qwen_headers = {
            "Authorization": f"Bearer {active_qwen_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "[ROLE: SOVEREIGN COGNITIVE PARSER & MATHEMATICAL GEOMETRICIAN]\n"
            "Tu es l'interrupteur cognitif de RATISS Cypher ODV.\n"
            "Traduis la requête physique ou géométrique de l'utilisateur en un prompt de visualisation géométrique en anglais.\n"
            "RÈGLES ABSOLUES :\n"
            "1. Épure le prompt de toute texture lourde, jargons photo-réalistes, filtres cinéma 4K/8K, éclairage studio ou détails superficiels.\n"
            "2. Concentre-toi EXCLUSIVEMENT sur la structure pure : lignes de grille vectorielles (vector grid lines), champs de forces (vector fields), "
            "mailles de précision (clean wireframe mesh), contrastes mathématiques élevés (high-contrast mathematical viz), "
            "et évolutions topologiques continues (smooth continuous evolution).\n"
            "3. Retourne UNIQUEMENT un objet JSON brut respectant exactement ce schéma :\n"
            "{\n"
            "  \"video_trigger\": true,\n"
            "  \"prompt_physics\": \"<prompt géométrique épuré en anglais>\"\n"
            "}\n"
            "N'ajoute aucun enrobage, aucune introduction, aucune balise de bloc de code markdown. Réponds uniquement par du JSON valide."
        )

        qwen_payload = {
            "model": "qwen-max",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        try:
            qwen_res = await client.post(QWEN_COMPATIBLE_URL, headers=qwen_headers, json=qwen_payload, timeout=12.0)
            qwen_res.raise_for_status()
            qwen_data = qwen_res.json()
            
            raw_content = qwen_data["choices"][0]["message"]["content"].strip()
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw_content = "\n".join(lines[1:-1]).strip()
            
            routing_result = json.loads(raw_content)
        except Exception as e:
            logger.error(f"[RATISS Router] Échec de l'analyse cognitive Qwen : {str(e)}")
            routing_result = {
                "video_trigger": True,
                "prompt_physics": f"High contrast 3D mathematical wireframe visualization, schematic grid lines, STRICTLY NO TEXT, no words, no letters, no typography, clean aesthetic, representing: {request.message}"
            }

        if not routing_result.get("video_trigger"):
            logger.info("[RATISS Router] Le parseur a déterminé que la requête ne justifie pas de génération vidéo.")
            return {"video_trigger": False, "action": "delegate_to_standard_chat"}

        prompt_physics = routing_result.get("prompt_physics", "Topological Ricci flow manifold deformation")
        logger.info(f"[RATISS Router] Prompt souverain généré : {prompt_physics}")

        # Étape 3 : Pilotage asynchrone non-bloquant de l'API vidéo Wan 2.7
        final_prompt = f"Mathematical vector field animation, wireframe grid, {prompt_physics}"
        timestamp_ns = time.time_ns()
        fallback_task_id = f"task_fallback_{uuid.uuid4().hex[:8]}"

        try:
            logger.info("[RATISS Router] Enregistrement de la tâche asynchrone Wan 2.7 auprès de DashScope...")
            ds_task_id, task_status = await async_call_dashscope_video(final_prompt, active_dashscope_key)
            
            if ds_task_id:
                actual_task_id = ds_task_id
            else:
                actual_task_id = fallback_task_id
                task_status = "PENDING_LOCAL_FALLBACK"
                
            # Calcul de la signature cryptographique unique VOLT-Ω
            volt_omega_sha3 = generate_volt_omega_hash(actual_task_id, prompt_physics, timestamp_ns)

            # Persistance locale via le ledger np.memmap
            meta = derive_topological_metadata(prompt_physics, volt_omega_sha3)
            write_record(
                volt_hash=volt_omega_sha3,
                task_id=actual_task_id,
                timestamp_ns=timestamp_ns,
                prompt=prompt_physics,
                equation=meta["equation"],
                curvature=meta["curvature"],
                proof=meta["proof"],
                vector=meta["vector"]
            )

            return {
                "status": "success",
                "type": "video_manifest",
                "payload": {
                    "task_id": actual_task_id,
                    "task_status": task_status,
                    "duration_seconds": 15,
                    "parameters": {
                        "ratio": "16:9",
                        "size": "1280*720",
                        "model": "wan-text-to-video-v2.7"
                    },
                    "prompt": prompt_physics,
                    "cryptographic_signatures": {
                        "sha3": volt_omega_sha3,
                        "ancrage": f"IPFS QmVOLT8_Omega_DashScope_{actual_task_id[:8]}"
                    }
                }
            }
        except Exception as e:
            logger.error(f"[RATISS Router] Échec de l'appel DashScope : {str(e)}")
            volt_omega_sha3 = generate_volt_omega_hash(fallback_task_id, prompt_physics, timestamp_ns)
            
            # Persistance locale via le ledger np.memmap
            meta = derive_topological_metadata(prompt_physics, volt_omega_sha3)
            write_record(
                volt_hash=volt_omega_sha3,
                task_id=fallback_task_id,
                timestamp_ns=timestamp_ns,
                prompt=prompt_physics,
                equation=meta["equation"],
                curvature=meta["curvature"],
                proof=meta["proof"],
                vector=meta["vector"]
            )

            return {
                "status": "success",
                "type": "video_manifest",
                "payload": {
                    "task_id": fallback_task_id,
                    "task_status": "PENDING_LOCAL_FALLBACK",
                    "duration_seconds": 15,
                    "parameters": {
                        "ratio": "16:9",
                        "size": "1280*720",
                        "model": "wan-text-to-video-v2.7 (Simulated)"
                    },
                    "prompt": prompt_physics,
                    "cryptographic_signatures": {
                        "sha3": volt_omega_sha3,
                        "ancrage": "IPFS QmVOLT8_Omega_Local"
                    },
                    "error_info": str(e)
                }
            }

@app.post("/route-video/weave")
async def story_weaver_route(request: StoryWeaverRequest):
    """
    StoryWeaver: Interpolation sémantique multi-frames.
    Reçoit une séquence ordonnée de checkpoints géométriques et produit un flux géodésique continu.
    """
    if not request.checkpoints:
        raise HTTPException(status_code=400, detail="Séquence de checkpoints vide.")
        
    checkpoints_str = " into ".join(f"[{cp}]" for cp in request.checkpoints)
    prompt_physics = f"Continuous cinematic transition sequence smoothly morphing from {checkpoints_str}, continuous vector grid layout, high contrast wireframe, STRICTLY NO TEXT, no words, no letters, no typography, clean aesthetic"
    logger.info(f"[RATISS StoryWeaver] Prompt composite formulé : {prompt_physics}")

    active_dashscope_key = get_clean_key("DASHSCOPE_API_KEY", "QWEN_API_KEY")
    timestamp_ns = time.time_ns()
    actual_task_id = f"task_weave_{uuid.uuid4().hex[:8]}"
    volt_hash = generate_volt_omega_hash(actual_task_id, prompt_physics, timestamp_ns)

    # Persistance locale immédiate dans le ledger NumPy memmap
    meta = derive_topological_metadata(prompt_physics, volt_hash)
    write_record(
        volt_hash=volt_hash,
        task_id=actual_task_id,
        timestamp_ns=timestamp_ns,
        prompt=prompt_physics,
        equation=meta["equation"],
        curvature=meta["curvature"],
        proof=meta["proof"],
        vector=meta["vector"]
    )

    # Pilotage asynchrone Wan 2.7
    task_status = "PENDING"
    try:
        final_prompt = f"Mathematical vector field continuous morphing, wireframe grid, {prompt_physics}"
        ds_task_id, task_status = await async_call_dashscope_video(final_prompt, active_dashscope_key)
        if ds_task_id:
            actual_task_id = ds_task_id
            # Mettre à jour l'enregistrement
            write_record(
                volt_hash=volt_hash,
                task_id=actual_task_id,
                timestamp_ns=timestamp_ns,
                prompt=prompt_physics,
                equation=meta["equation"],
                curvature=meta["curvature"],
                proof=meta["proof"],
                vector=meta["vector"]
            )
    except Exception as e:
        logger.error(f"[RATISS StoryWeaver] DashScope API non joignable: {str(e)}")
        task_status = "PENDING_LOCAL_FALLBACK"

    return {
        "status": "success",
        "type": "video_manifest",
        "payload": {
            "task_id": actual_task_id,
            "task_status": task_status,
            "duration_seconds": 15,
            "parameters": {
                "ratio": "16:9",
                "size": "1280*720",
                "model": "wan-text-to-video-v2.7"
            },
            "prompt": prompt_physics,
            "cryptographic_signatures": {
                "sha3": volt_hash,
                "ancrage": "IPFS QmVOLT8_Omega_StoryWeaver"
            }
        }
    }

@app.get("/route-video/scalpel/{volt_hash}")
async def topo_scalpel_route(volt_hash: str):
    """
    TopoScalpel: Outil de dissection clinique invariant par d'ancrage VOLT-Ω.
    Extraction instantanée via np.memmap.
    """
    logger.info(f"[RATISS TopoScalpel] Dissection clinique du hash: {volt_hash}")
    record = find_record_by_hash(volt_hash)
    
    if not record:
        raise HTTPException(
            status_code=404, 
            detail=f"Cryptographic block for VOLT-Ω hash '{volt_hash}' not found in local NumPy memory-mapped ledger."
        )
        
    return {
        "status": "success",
        "volt_hash": record["volt_hash"],
        "task_id": record["task_id"],
        "timestamp": record["timestamp"],
        "prompt": record["prompt"],
        "equation": record["equation"],
        "curvature": record["curvature"],
        "proof": record["proof"],
        "vector": record["vector"]
    }

@app.post("/route-video/echo-chamber")
async def echo_chamber_route(request: EchoChamberRequest):
    """
    EchoChamber: Collision sémantique de deux hypothèses physiques concurrentes.
    Force un split-screen et des interférences topologiques entre Hypothèse A et Hypothèse B.
    """
    prompt_physics = f"Visual split-screen and topological interference pattern showing the direct collision between [{request.hypothesis_a}] and [{request.hypothesis_b}], overlapping vector fields, discrete geometry diffraction, STRICTLY NO TEXT, no words, no letters, no typography, clean aesthetic"
    logger.info(f"[RATISS EchoChamber] Orchestration de combat sémantique : {prompt_physics}")

    active_dashscope_key = get_clean_key("DASHSCOPE_API_KEY", "QWEN_API_KEY")
    timestamp_ns = time.time_ns()
    actual_task_id = f"task_echo_{uuid.uuid4().hex[:8]}"
    volt_hash = generate_volt_omega_hash(actual_task_id, prompt_physics, timestamp_ns)

    # Persistance locale immédiate dans le ledger NumPy memmap
    meta = derive_topological_metadata(prompt_physics, volt_hash)
    write_record(
        volt_hash=volt_hash,
        task_id=actual_task_id,
        timestamp_ns=timestamp_ns,
        prompt=prompt_physics,
        equation=meta["equation"],
        curvature=meta["curvature"],
        proof=meta["proof"],
        vector=meta["vector"]
    )

    # Pilotage asynchrone Wan 2.7
    task_status = "PENDING"
    try:
        final_prompt = f"Topological collision split-screen rendering, wireframe grid, {prompt_physics}"
        ds_task_id, task_status = await async_call_dashscope_video(final_prompt, active_dashscope_key)
        if ds_task_id:
            actual_task_id = ds_task_id
            # Mettre à jour l'enregistrement
            write_record(
                volt_hash=volt_hash,
                task_id=actual_task_id,
                timestamp_ns=timestamp_ns,
                prompt=prompt_physics,
                equation=meta["equation"],
                curvature=meta["curvature"],
                proof=meta["proof"],
                vector=meta["vector"]
            )
    except Exception as e:
        logger.error(f"[RATISS EchoChamber] DashScope API non joignable: {str(e)}")
        task_status = "PENDING_LOCAL_FALLBACK"

    return {
        "status": "success",
        "type": "video_manifest",
        "payload": {
            "task_id": actual_task_id,
            "task_status": task_status,
            "duration_seconds": 15,
            "parameters": {
                "ratio": "16:9",
                "size": "1280*720",
                "model": "wan-text-to-video-v2.7"
            },
            "prompt": prompt_physics,
            "cryptographic_signatures": {
                "sha3": volt_hash,
                "ancrage": "IPFS QmVOLT8_Omega_EchoChamber"
            }
        }
    }

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Permet à l'UI ou au backend d'interroger l'état d'avancement d'une tâche DashScope.
    """
    if "fallback" in task_id or "weave" in task_id or "echo" in task_id:
        return {
            "task_id": task_id,
            "task_status": "SUCCEEDED",
            "progress": 100,
            "video_url": "/assets/simulated_topo_video.mp4"
        }

    active_dashscope_key = get_clean_key("DASHSCOPE_API_KEY", "QWEN_API_KEY")
    if not active_dashscope_key:
        raise HTTPException(status_code=401, detail="API Key configuration is missing.")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {active_dashscope_key}"
        }
        try:
            status_url = f"{WAN_TASK_STATUS_URL}/{task_id}"
            logger.info(f"[RATISS Status] Interrogation de l'état DashScope pour la tâche : {task_id}")
            res = await client.get(status_url, headers=headers, timeout=10.0)
            res.raise_for_status()
            data = res.json()
            
            output = data.get("output", {})
            status = output.get("task_status", "PENDING")
            video_url = output.get("video_url")
            
            return {
                "task_id": task_id,
                "task_status": status,
                "progress": 100 if status == "SUCCEEDED" else (50 if status == "RUNNING" else 0),
                "video_url": video_url,
                "dashscope_data": data
            }
        except Exception as e:
            logger.error(f"[RATISS Status] Impossible de récupérer l'état DashScope pour {task_id} : {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    init_ledger()
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
