"""
RATISS V9 AEON PRIME - MEMORY & PERFORMANCE BENCHMARK
Hardware Target: AMD Ryzen 5 PRO 2500U (4C/8T) + AMD Radeon Vega 8 Graphics + 8GB RAM

Profiles peak Resident Set Size (RSS) memory and execution time across all stages.
"""

import time
import random
import logging
from ratiss_v9_real.system.memory_guard import get_current_memory_mb, free_memory
from ratiss_v9_real.core.refinery import pre_filter_topology, build_tj_symmetries_config
from ratiss_v9_real.solvers.topo_solver import solve_persistent_homology
from ratiss_v9_real.solvers.quantum_solver import solve_tj_ground_state

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logging.basicConfig(level=logging.INFO, format="[RATISS-BENCHMARK] %(asctime)s - %(message)s")

def run_benchmark():
    logging.info("="*65)
    logging.info("STARTING RATISS V9 AEON PRIME HARDWARE BENCHMARK")
    logging.info("TARGET: AMD Ryzen 5 PRO 2500U (4 Cores / 8 Threads) + AMD Radeon Vega 8 Graphics | RAM MAX: 8.0 GB")
    logging.info("="*65)
    
    start_total_time = time.time()
    mem_initial = get_current_memory_mb()
    peak_mem = mem_initial
    
    # Étape 1 : Injection de données massives (Simulé OPF 50,000 nodes)
    logging.info("\n--- STEP 1: DENSE DATA INGESTION ---")
    t0 = time.time()
    if HAS_NUMPY:
        raw_data = np.random.randn(50000, 3).astype(np.float32)
    else:
        random.seed(42)
        raw_data = [[random.gauss(0, 1) for _ in range(3)] for _ in range(50000)]

    m1 = get_current_memory_mb()
    peak_mem = max(peak_mem, m1)
    logging.info(f"Generated 50,000 points. RAM: {m1:.2f} MB (Delta: +{m1-mem_initial:.2f} MB) in {time.time()-t0:.3f}s")
    
    # Étape 2 : Raffinerie Topologique
    logging.info("\n--- STEP 2: TOPOLOGICAL REFINERY ---")
    t0 = time.time()
    refinery_res = pre_filter_topology(raw_data, target_landmarks=300)
    landmarks = refinery_res["landmarks"]
    m2 = get_current_memory_mb()
    peak_mem = max(peak_mem, m2)
    logging.info(f"Refinery compressed data by {refinery_res['compression_ratio']:.1f}x. RAM: {m2:.2f} MB in {time.time()-t0:.3f}s")
    
    # Cleanup intermédiaire
    del raw_data
    free_memory()
    
    # Étape 3 : Résolution Topologique (GUDHI/Natif)
    logging.info("\n--- STEP 3: PERSISTENT HOMOLOGY SOLVER ---")
    t0 = time.time()
    topo_res = solve_persistent_homology(landmarks, max_dimension=2)
    m3 = get_current_memory_mb()
    peak_mem = max(peak_mem, m3)
    logging.info(f"Homology calculated (Betti={topo_res['betti_numbers']}). RAM: {m3:.2f} MB in {time.time()-t0:.3f}s")
    
    # Étape 4 : Raffinerie & Résolveur Quantique t-J
    logging.info("\n--- STEP 4: QUANTUM t-J MODEL SOLVER ---")
    t0 = time.time()
    tj_config = build_tj_symmetries_config(Lx=4, Ly=4, N_fermions=4, Sz=0)
    q_res = solve_tj_ground_state(tj_config, t=1.0, J=0.4)
    m4 = get_current_memory_mb()
    peak_mem = max(peak_mem, m4)
    logging.info(f"Ground state solved (E0={q_res['ground_state_energy']:.4f}). RAM: {m4:.2f} MB in {time.time()-t0:.3f}s")
    
    total_duration = time.time() - start_total_time
    
    logging.info("\n" + "="*65)
    logging.info("BENCHMARK SUMMARY REPORT")
    logging.info("="*65)
    logging.info(f"Total Time Elapsed    : {total_duration:.2f} seconds")
    logging.info(f"Initial RAM Usage     : {mem_initial:.2f} MB")
    logging.info(f"PEAK RAM USAGE        : {peak_mem:.2f} MB / 7500 MB MAX LIMIT")
    logging.info(f"RAM Margin Remaining  : {7500.0 - peak_mem:.2f} MB")
    
    if peak_mem < 7500.0:
        logging.info("STATUS: SUCCESS - PERFECT EMBEDDED RAM COMPLIANCE!")
    else:
        logging.warning("STATUS: WARNING - RAM BREACH DETECTED!")
        
    return {
        "total_duration_sec": total_duration,
        "peak_ram_mb": peak_mem,
        "margin_mb": 7500.0 - peak_mem
    }

if __name__ == "__main__":
    run_benchmark()
