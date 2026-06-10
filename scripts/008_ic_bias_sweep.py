#!/usr/bin/env python3
"""Runner standalone: sesgo vs condiciones iniciales (S2, notebook 008).

Lanzar en background con Mac cerrada:
    caffeinate -i -s nohup python scripts/008_ic_bias_sweep.py \
        > bias_ic_results/run.log 2>&1 &
    disown

Resume automático: cada (job) se persiste como parquet apenas termina.
Re-lanzar el script salta los ya completados.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Permitir `python scripts/008_ic_bias_sweep.py` desde la raíz del repo.
sys.path.insert(0, str(Path(__file__).parent))
from _bias_lib import (  # noqa: E402
    A_S2_RG, E_S2, I_S2, SPIN_DEFAULT,
    aggregate_bias, run_one_ic,
)


# ---------------------------------------------------------------------------
# Grids
# ---------------------------------------------------------------------------
N_INDEP = 100   # puntos por eje independiente
N_PAIR_AX = 10  # 10×10 = 100 puntos por par conjunto

SPIN_RANGE = np.linspace(0.8, 1.0, N_INDEP, endpoint=False)
A_RANGE = np.linspace(0.5, 1.5, N_INDEP) * A_S2_RG
E_RANGE = np.linspace(0.0, 0.95, N_INDEP)
INC_RANGE = np.linspace(0.0, 85.0, N_INDEP)

SPIN_PAIR = np.linspace(0.8, 1.0, N_PAIR_AX, endpoint=False)
A_PAIR = np.linspace(0.5, 1.5, N_PAIR_AX) * A_S2_RG
E_PAIR = np.linspace(0.0, 0.95, N_PAIR_AX)
INC_PAIR = np.linspace(0.0, 85.0, N_PAIR_AX)

DEFAULTS = dict(spin=SPIN_DEFAULT, a=A_S2_RG, e=E_S2, inc=I_S2)

AXES = {
    "spin": SPIN_RANGE,
    "a": A_RANGE,
    "e": E_RANGE,
    "inc": INC_RANGE,
}
AXES_PAIR = {
    "spin": SPIN_PAIR,
    "a": A_PAIR,
    "e": E_PAIR,
    "inc": INC_PAIR,
}
PAIRS = [
    ("spin", "a"), ("spin", "e"), ("spin", "i"),
    ("a", "e"), ("a", "i"), ("e", "i"),
]


def _pair_key(ax: str) -> str:
    return "inc" if ax == "i" else ax


def _make_indep_job(axis: str, idx: int, v: float) -> dict:
    params = dict(DEFAULTS)
    params[axis] = float(v)
    return {
        "mode": "indep", "axis": axis, "idx": idx, "params": params,
        "out": f"indep/{axis}/{idx:03d}.json",
    }


def _make_pair_job(ax1: str, ax2: str, i: int, j: int, v1: float, v2: float) -> dict:
    params = dict(DEFAULTS)
    params[_pair_key(ax1)] = float(v1)
    params[_pair_key(ax2)] = float(v2)
    return {
        "mode": "pair", "pair": f"{ax1}-{ax2}", "i": i, "j": j,
        "params": params,
        "out": f"pair/{ax1}-{ax2}/{i:02d}-{j:02d}.json",
    }


def build_jobs() -> list[dict]:
    """Round-robin: cada ronda k (0..99) avanza 1 punto en cada panel.

    Layout por ronda (10 jobs):
        4 indep (spin[k], a[k], e[k], inc[k])
        6 pair (cada par evalúa su (i,j) = (k//10, k%10))

    Total: 100 rondas × 10 = 1000 jobs. Permite ver el dashboard llenándose
    de forma uniforme en todos los paneles.
    """
    jobs = []
    for k in range(N_INDEP):
        # 4 indep
        for axis in AXES:
            jobs.append(_make_indep_job(axis, k, AXES[axis][k]))
        # 6 pair (mismo k → (i, j) = (k//10, k%10))
        i, j = k // N_PAIR_AX, k % N_PAIR_AX
        for ax1, ax2 in PAIRS:
            k1, k2 = _pair_key(ax1), _pair_key(ax2)
            jobs.append(_make_pair_job(
                ax1, ax2, i, j, AXES_PAIR[k1][i], AXES_PAIR[k2][j]))
    return jobs


def write_manifest(results_dir: Path):
    manifest = {
        "defaults": DEFAULTS,
        "indep": {ax: AXES[ax].tolist() for ax in AXES},
        "pair_axes": {ax: AXES_PAIR[ax].tolist() for ax in AXES_PAIR},
        "pairs": [list(p) for p in PAIRS],
        "n_indep": N_INDEP,
        "n_pair_ax": N_PAIR_AX,
    }
    (results_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


def save_atomic(out_path: Path, row: dict):
    """Escribe JSON de forma atómica (tmp + rename)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".tmp.json")
    # numpy → Python primitives
    clean = {}
    for k, v in row.items():
        if isinstance(v, (np.floating,)):
            clean[k] = float(v)
        elif isinstance(v, (np.integer,)):
            clean[k] = int(v)
        elif isinstance(v, float) and np.isnan(v):
            clean[k] = None
        else:
            clean[k] = v
    tmp.write_text(json.dumps(clean))
    os.replace(tmp, out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=None,
                        help="Default: bias_ic_results (cartesian) o "
                             "bias_ic_radec_results (radec).")
    parser.add_argument("--bank-dir", default="paths_bank_ic_sweep")
    parser.add_argument("--noise", choices=["cartesian", "radec"],
                        default="cartesian",
                        help="Modelo de error: cartesiano (008) o "
                             "astrométrico RA/DEC σ=50µas (009).")
    parser.add_argument("--limit", type=int, default=None,
                        help="Procesa solo los primeros N jobs (smoke test).")
    parser.add_argument("--n-jobs", type=int, default=-1,
                        help="joblib n_jobs para sweep_n_points (default -1).")
    args = parser.parse_args()

    if args.results_dir is None:
        args.results_dir = ("bias_ic_results" if args.noise == "cartesian"
                            else "bias_ic_radec_results")

    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    write_manifest(results_dir)

    jobs = build_jobs()
    if args.limit is not None:
        jobs = jobs[: args.limit]

    total = len(jobs)
    print(f"[runner] noise:       {args.noise}", flush=True)
    print(f"[runner] total jobs: {total}", flush=True)
    print(f"[runner] results dir: {results_dir.resolve()}", flush=True)
    print(f"[runner] bank dir:    {Path(args.bank_dir).resolve()}", flush=True)

    t_global = time.time()
    done = 0
    skipped = 0

    for k, job in enumerate(jobs):
        out_path = results_dir / job["out"]
        if out_path.exists():
            skipped += 1
            continue

        params = job["params"]
        tag = (f"[{k+1}/{total}] {job['out']}  "
               f"spin={params['spin']:.4f} a={params['a']:.2f} "
               f"e={params['e']:.4f} inc={params['inc']:.3f}")
        print(tag, flush=True)
        t0 = time.time()

        try:
            df = run_one_ic(
                spin=params["spin"], a=params["a"],
                e=params["e"], inc_deg=params["inc"],
                bank_dir=args.bank_dir, n_jobs=args.n_jobs,
                noise=args.noise,
            )
            metrics = aggregate_bias(df)
            row = {**params, **metrics,
                   "mode": job["mode"], "key": job["out"],
                   "elapsed_s": time.time() - t0}
        except Exception as ex:
            row = {**params,
                   "med_abs_z_Lz": np.nan, "med_abs_z_Q": np.nan,
                   "n_valid_Lz": 0, "n_valid_Q": 0, "n_total": 0,
                   "mode": job["mode"], "key": job["out"],
                   "elapsed_s": time.time() - t0,
                   "error": repr(ex)}
            print(f"  FAILED: {ex!r}", flush=True)

        save_atomic(out_path, row)
        done += 1

        if done % 5 == 0 or k == total - 1:
            elapsed = time.time() - t_global
            rate = done / max(elapsed, 1e-9)
            remaining = total - (k + 1)
            eta_h = remaining / max(rate, 1e-9) / 3600.0
            print(f"  progress: {k+1}/{total}  done={done} skipped={skipped}  "
                  f"rate={rate*60:.2f}/min  ETA={eta_h:.2f}h", flush=True)

    print(f"[runner] FINISHED  done={done} skipped={skipped}  "
          f"total_time={(time.time()-t_global)/3600:.2f}h", flush=True)


if __name__ == "__main__":
    main()
