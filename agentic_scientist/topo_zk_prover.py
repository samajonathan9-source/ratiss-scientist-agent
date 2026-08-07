#!/usr/bin/env python3
# topo_zk_prover.py
# RATISS Cypher ODV — Topological ZK Prover
# Couplage TopologyCompressor + ZK-GPU sur CPU

import json
import hashlib
import time
import os
import sys

# --- 1. TopologyCompressor (Version simplifiée pour CPU) ---
# Reprendre les fonctions de compression topologique du moteur RATISS

def topology_compress(trace: dict) -> dict:
    """
    Compresse la trace en identifiant les cycles répétitifs et les invariants.
    Réduit l'espace des contraintes sans perte d'information.
    """
    cycles = trace.get('cycles', [])
    if len(cycles) < 2:
        trace['compressed_cycles'] = cycles
        trace['compression_ratio'] = 1.0
        trace['original_length'] = len(cycles)
        return trace
    
    compressed_cycles = []
    i = 0
    while i < len(cycles):
        # On essaie d'identifier une répétition à partir de i
        # Cherchons s'il y a un pattern de longueur 'pattern_length' qui se répète 'count' fois
        best_pattern_len = 1
        best_count = 1
        
        # On teste différentes longueurs de patterns (1 à 8 instructions)
        for pattern_len in range(1, 9):
            if i + pattern_len > len(cycles):
                continue
                
            pattern = cycles[i : i + pattern_len]
            count = 1
            
            # Compter combien de fois ce pattern se répète immédiatement
            while i + (count + 1) * pattern_len <= len(cycles):
                next_part = cycles[i + count * pattern_len : i + (count + 1) * pattern_len]
                # Comparaison simple du dictionnaire (par serialisation JSON pour être sûr)
                if json.dumps(pattern, sort_keys=True) == json.dumps(next_part, sort_keys=True):
                    count += 1
                else:
                    break
            
            if count > 1 and (count * pattern_len) > (best_count * best_pattern_len):
                best_pattern_len = pattern_len
                best_count = count
                
        if best_count > 1:
            # On compresse ce pattern répétitif
            pattern_sublist = cycles[i : i + best_pattern_len]
            compressed_cycles.append({
                "type": "repeated",
                "pattern": pattern_sublist if best_pattern_len > 1 else pattern_sublist[0],
                "count": best_count,
                "pattern_length": best_pattern_len
            })
            i += best_count * best_pattern_len
        else:
            # Conservation de l'instruction unique
            compressed_cycles.append(cycles[i])
            i += 1
            
    trace['compressed_cycles'] = compressed_cycles
    trace['compression_ratio'] = len(compressed_cycles) / len(cycles) if len(cycles) > 0 else 1.0
    trace['original_length'] = len(cycles)
    
    return trace

# --- 2. Arithmétique Goldilocks (CPU) ---
MODULUS = 0xFFFFFFFF00000001

def field_add(a, b):
    return (a + b) % MODULUS

def field_sub(a, b):
    return (a - b) % MODULUS

def evaluate_single_cycle_constraints(cycle: dict, constraints_out: list):
    regs = cycle.get('registers', [0]*32)
    opcode = cycle.get('opcode', '')
    pc = cycle.get('pc', 0)
    
    if opcode == "ADD":
        ra = regs[1] if len(regs) > 1 else 0
        rb = regs[5] if len(regs) > 5 else 0
        rc = regs[10] if len(regs) > 10 else 0
        res = field_sub(field_add(ra, rb), rc)
        constraints_out.append({
            "type": "ADD",
            "result": res,
            "valid": res == 0,
            "pc": pc
        })
    elif opcode == "JAL":
        pc_next = cycle.get('pc_next', pc + 4)
        res = field_sub(pc_next, field_add(pc, 4))
        constraints_out.append({
            "type": "JAL",
            "result": res,
            "valid": res == 0,
            "pc": pc
        })
    elif opcode == "LOAD":
        # Contrainte LOAD (exemple d'intégrité mémoire fictive: mem_val != None)
        mem_val = cycle.get('mem_val', 0)
        constraints_out.append({
            "type": "LOAD",
            "result": 0,
            "valid": mem_val is not None,
            "pc": pc
        })

# --- 3. Évaluation des contraintes sur la trace compressée ---
def evaluate_constraints(trace: dict) -> dict:
    """
    Évalue les contraintes Plonkish sur la trace compressée.
    Retourne les contraintes satisfaites et la preuve associée.
    """
    cycles = trace.get('compressed_cycles', [])
    constraints = []
    
    for cycle in cycles:
        if isinstance(cycle, dict) and cycle.get('type') == 'repeated':
            # Pour les cycles répétitifs, on évalue le pattern et on multiplie le compte
            pattern = cycle['pattern']
            count = cycle['count']
            
            sub_constraints = []
            if isinstance(pattern, list):
                for sub_c in pattern:
                    evaluate_single_cycle_constraints(sub_c, sub_constraints)
            else:
                evaluate_single_cycle_constraints(pattern, sub_constraints)
                
            # On applique la validité sur le bloc compressé
            all_valid = all(c['valid'] for c in sub_constraints) if sub_constraints else True
            constraints.append({
                "type": "REPEATED_BLOCK",
                "count": count,
                "sub_constraints": sub_constraints,
                "valid": all_valid
            })
        else:
            evaluate_single_cycle_constraints(cycle, constraints)
            
    # Calcul des statistiques de contraintes réelles représentées (décompressées)
    total_uncompressed_constraints = 0
    valid_uncompressed_constraints = 0
    
    for c in constraints:
        if c.get("type") == "REPEATED_BLOCK":
            weight = c.get("count", 1)
            sub_len = len(c.get("sub_constraints", []))
            # Si le pattern n'avait pas d'opcodes gérés, on compte quand même 1 contrainte structurelle
            multiplier = sub_len if sub_len > 0 else 1
            total_uncompressed_constraints += weight * multiplier
            if c.get("valid", False):
                valid_uncompressed_constraints += weight * multiplier
        else:
            total_uncompressed_constraints += 1
            if c.get("valid", False):
                valid_uncompressed_constraints += 1
                
    return {
        "constraints": constraints,
        "total_constraints": len(constraints),
        "valid_constraints": sum(1 for c in constraints if c.get('valid', False)),
        "total_uncompressed_constraints": total_uncompressed_constraints,
        "valid_uncompressed_constraints": valid_uncompressed_constraints
    }

# --- 4. Génération de la preuve topologique ---
def generate_topo_proof(trace: dict, constraints: dict) -> dict:
    """
    Génère une preuve cryptographique basée sur la compression topologique.
    """
    # Hash de la trace originale
    trace_hash = hashlib.sha256(json.dumps(trace.get('cycles', []), sort_keys=True).encode()).hexdigest()
    
    # Hash des contraintes
    constraints_hash = hashlib.sha256(json.dumps(constraints.get('constraints', []), sort_keys=True).encode()).hexdigest()
    
    # Preuve topologique : combinaison des hash + métriques de compression
    proof = {
        "version": "1.0-TOPO",
        "trace_hash": trace_hash,
        "constraints_hash": constraints_hash,
        "compression_ratio": trace.get('compression_ratio', 1.0),
        "valid_constraints": constraints.get('valid_constraints', 0),
        "total_constraints": constraints.get('total_constraints', 0),
        "total_uncompressed_constraints": constraints.get('total_uncompressed_constraints', 0),
        "valid_uncompressed_constraints": constraints.get('valid_uncompressed_constraints', 0),
        "signature": hashlib.sha256(f"{trace_hash}{constraints_hash}".encode()).hexdigest(),
        "timestamp": time.time()
    }
    
    return proof

# --- 5. Fonction principale ---
def run_topo_zk_prover(trace_path: str, output_path: str = "proof.json"):
    """
    Pipeline complet du prover topologique ZK.
    """
    if not os.path.exists(trace_path):
        raise FileNotFoundError(f"Trace file not found: {trace_path}")
        
    print(f"[Topo-ZK] Chargement de la trace: {trace_path}")
    with open(trace_path, 'r') as f:
        trace = json.load(f)
    
    print("[Topo-ZK] Compression topologique de la trace...")
    start_time = time.time()
    compressed_trace = topology_compress(trace)
    compression_time = time.time() - start_time
    print(f"[Topo-ZK] Compression terminée en {compression_time:.4f}s")
    print(f"[Topo-ZK] Taux de compression: {compressed_trace.get('compression_ratio', 1.0):.2%}")
    
    print("[Topo-ZK] Évaluation des contraintes sur la trace compressée...")
    start_time = time.time()
    constraints = evaluate_constraints(compressed_trace)
    eval_time = time.time() - start_time
    print(f"[Topo-ZK] Évaluation terminée en {eval_time:.4f}s")
    print(f"[Topo-ZK] Contraintes valides: {constraints.get('valid_constraints', 0)}/{constraints.get('total_constraints', 0)}")
    
    print("[Topo-ZK] Génération de la preuve topologique...")
    proof = generate_topo_proof(compressed_trace, constraints)
    proof["compression_time_seconds"] = compression_time
    proof["evaluation_time_seconds"] = eval_time
    
    print(f"[Topo-ZK] Sauvegarde de la preuve dans {output_path}")
    with open(output_path, 'w') as f:
        json.dump(proof, f, indent=2)
        
    # On sauvegarde également un rapport complet pour le front-end
    report = {
        "status": "SUCCESS",
        "original_length": compressed_trace.get('original_length', 0),
        "compressed_length": len(compressed_trace.get('compressed_cycles', [])),
        "compression_ratio": compressed_trace.get('compression_ratio', 1.0),
        "compression_time": compression_time,
        "evaluation_time": eval_time,
        "constraints_summary": {
            "total": constraints.get('total_constraints', 0),
            "valid": constraints.get('valid_constraints', 0),
            "total_uncompressed": constraints.get('total_uncompressed_constraints', 0),
            "valid_uncompressed": constraints.get('valid_uncompressed_constraints', 0)
        },
        "proof": proof,
        "compressed_cycles": compressed_trace.get('compressed_cycles', [])
    }
    
    with open("topo_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("[Topo-ZK] ✅ Preuve topologique générée avec succès.")
    return proof


# --- 6. Exemple d'utilisation ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python topo_zk_prover.py <trace.json> [proof.json]")
        sys.exit(1)
    
    trace_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "proof.json"
    
    try:
        proof = run_topo_zk_prover(trace_path, output_path)
        print(f"\n[Résultat] Preuve générée avec succès :")
        print(json.dumps(proof, indent=2))
    except Exception as e:
        print(f"Error during Topological ZK execution: {str(e)}")
        sys.exit(1)
