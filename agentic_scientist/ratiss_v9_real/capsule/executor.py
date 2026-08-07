#!/usr/bin/env python3
"""
RATISS V9 AEON PRIME - CAPSULE D'EXÉCUTION SOUVERAINE VEGA8-SAFE
Hardware Target: AMD Ryzen 5 PRO 2500U (4C/8T) + AMD Radeon Vega 8 + 8GB RAM Shared
"""
import os
import sys
import json
import tempfile
import shutil
import subprocess
import time
from pathlib import Path

# Configuration
PYTHON_BIN = sys.executable
CACHE_DIR = Path.home() / ".cache" / "pip" / "ratiss_deps"
TIMEOUT_SEC = 300
MAX_MEM_MB = 7500

def create_ephemeral_venv():
    """Crée un venv éphémère dans /tmp avec fallback --without-pip et accès aux paquets système"""
    tmpdir = tempfile.mkdtemp(prefix="ratiss_capsule_")
    venv_path = Path(tmpdir) / "venv"
    try:
        subprocess.run([PYTHON_BIN, "-m", "venv", "--system-site-packages", str(venv_path)], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        subprocess.run([PYTHON_BIN, "-m", "venv", "--system-site-packages", "--without-pip", str(venv_path)], check=True, capture_output=True)
    return venv_path, tmpdir

def install_deps_cached(venv_path):
    """Installe les dépendances depuis le cache local si disponible"""
    pip_bin = venv_path / "bin" / "pip"
    if not pip_bin.exists():
        return
    wheels = list(CACHE_DIR.glob("*.whl")) if CACHE_DIR.exists() else []
    if wheels:
        cmd = [str(pip_bin), "install", "--no-index", "--find-links", str(CACHE_DIR)] + [str(w) for w in wheels]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)

def execute_module(venv_path, module_name, params_json):
    """Exécute le module cible dans le venv temporaire avec isolation stricte CPU-only"""
    python_bin = venv_path / "bin" / "python"
    project_root = Path(__file__).resolve().parent.parent.parent

    script = """
import sys, os, json
sys.path.insert(0, os.environ.get('RATISS_PROJECT_ROOT', ''))
mod_name = os.environ.get('RATISS_MODULE_NAME', '')

try:
    target_func_name = None
    if ':' in mod_name:
        mod_name, target_func_name = mod_name.split(':', 1)

    if mod_name.startswith('ratiss_v9_real.'):
        mod = __import__(mod_name, fromlist=['*'])
    elif '.' in mod_name:
        mod = __import__('ratiss_v9_real.' + mod_name, fromlist=['*'])
    else:
        try:
            mod = __import__('ratiss_v9_real.' + mod_name, fromlist=['*'])
        except ImportError:
            try:
                mod = __import__('ratiss_v9_real.solvers.' + mod_name, fromlist=['*'])
            except ImportError:
                mod = __import__('ratiss_v9_real.core.' + mod_name, fromlist=['*'])

    params = json.loads(os.environ.get('RATISS_CAPSULE_PARAMS', '{}'))
    
    if target_func_name and hasattr(mod, target_func_name):
        target_func = getattr(mod, target_func_name)
    else:
        local_funcs = [getattr(mod, k) for k in dir(mod) if callable(getattr(mod, k)) and not k.startswith('_') and getattr(getattr(mod, k), '__module__', '').startswith('ratiss_v9_real')]
        if not local_funcs:
            local_funcs = [getattr(mod, k) for k in dir(mod) if callable(getattr(mod, k)) and not k.startswith('_')]
        
        if not local_funcs:
            print(json.dumps({"error": "Aucune fonction trouvée", "verdict": "NO_FUNC"}))
            sys.exit(1)

        import inspect
        target_func = None
        for fn in local_funcs:
            try:
                sig = inspect.signature(fn)
                if any(p in sig.parameters for p in params.keys()):
                    target_func = fn
                    break
            except Exception:
                pass

        if not target_func:
            for fn in local_funcs:
                name = getattr(fn, '__name__', '')
                if name.startswith(('solve_quantum', 'pre_filter_', 'solve_', 'run_', 'build_')):
                    target_func = fn
                    break

        if not target_func:
            target_func = local_funcs[0]

    import inspect
    sig = inspect.signature(target_func)
    if 'config' in sig.parameters and 'config' not in params:
        result = target_func(config=params)
    elif 'params' in sig.parameters and 'params' not in params:
        result = target_func(params=params)
    else:
        try:
            result = target_func(**params) if params else target_func()
        except TypeError:
            result = target_func(params) if params else target_func()

    print(json.dumps(result))
except Exception as e:
    import traceback
    print(json.dumps({"error": str(e), "details": traceback.format_exc(), "verdict": "ZK-CPU-REJECTED"}))
    sys.exit(1)
"""

    env_vars = {
        **os.environ,
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "PYTHONPATH": str(project_root),
        "RATISS_PROJECT_ROOT": str(project_root),
        "RATISS_MODULE_NAME": module_name,
        "RATISS_CAPSULE_PARAMS": params_json
    }

    proc = subprocess.run(
        [str(python_bin), "-c", script],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SEC,
        env=env_vars
    )

    if proc.returncode != 0:
        err_msg = proc.stderr.strip() or proc.stdout.strip()
        return {"error": err_msg, "verdict": "ZK-CPU-REJECTED"}

    stdout_text = proc.stdout.strip()
    # Find JSON block in stdout
    lines = [line.strip() for line in stdout_text.splitlines() if line.strip()]
    for line in reversed(lines):
        if (line.startswith("{") and line.endswith("}")) or (line.startswith("[") and line.endswith("]")):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

    try:
        return json.loads(stdout_text)
    except json.JSONDecodeError:
        return {"error": "JSON invalide", "raw": stdout_text[:500], "verdict": "ZK-CPU-REJECTED"}

def cleanup(venv_path, tmpdir):
    """Nettoyage éphémère post-exécution sans fuite de mémoire ou processus orphelin"""
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        subprocess.run(["pkill", "-f", str(venv_path)], capture_output=True)
        time.sleep(0.5)
        shutil.rmtree(tmpdir, ignore_errors=True)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Encapsuleur d'Exécution Souverain RATISS V9")
    parser.add_argument("--module", required=True, help="Module cible (ex: solvers.quantum_solver, core.refinery)")
    parser.add_argument("--params", default="{}", help="Paramètres JSON pour la fonction")
    args = parser.parse_args()

    venv_path, tmpdir = None, None
    try:
        venv_path, tmpdir = create_ephemeral_venv()
        install_deps_cached(venv_path)
        result = execute_module(venv_path, args.module, args.params)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e), "verdict": "ZK-CPU-REJECTED"}))
        sys.exit(1)
    finally:
        if venv_path and tmpdir:
            cleanup(venv_path, tmpdir)

if __name__ == "__main__":
    main()
