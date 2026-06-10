"""Bias-vs-ICs sweep library extracted from notebook 008.

Funciones reutilizables para correr `sweep_n_points` con condiciones iniciales
variables (spin, a, e, inc). Importable desde el runner y desde notebook.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.integrate import cumulative_trapezoid
from scipy.stats import gaussian_kde, norm

from astropy import units as u

from relatipy.numeric.constants import _L_ref
from relatipy.numeric.coordinates import (
    ApparentOrbitalElements,
    BoyerLindquist,
    Cartesian,
)
from relatipy.numeric.coordinates.apparent_orbital_elements import _build_rotation
from relatipy.numeric.metrics import Kerr
from relatipy.numeric.utils.banks import PathsBank, init_bank


# ---------------------------------------------------------------------------
# S2 constantes (GRAVITY Collaboration 2020, A&A 636, L5)
# ---------------------------------------------------------------------------
A_MAS = 125.058
DIST_PC = 8277.0
M_SGRA = 4.154e6  # M_sun
G_SI = 6.674e-11
C_SI = 2.998e8
MSUN = 1.989e30
AU_M = 1.496e11

_a_au = (A_MAS / 1e3) * DIST_PC
_r_g_m = G_SI * M_SGRA * MSUN / C_SI**2
_r_g_au = _r_g_m / AU_M
A_S2_RG = _a_au / _r_g_au  # ≈ 2911.475

E_S2 = 0.884649
I_S2 = 134.567
OMEGA_S2 = 228.171
omega_s2 = 66.263
SPIN_DEFAULT = 0.9

ERR_TIME = 0.0001
ERR_POS = 0.005 * A_S2_RG
SIGMA_RADEC_UAS = 50.0  # error astrométrico 1σ en RA y DEC (µas)
DEG2UAS = 3.6e9


# ---------------------------------------------------------------------------
# PathWithError + helpers (extraído verbatim del notebook 008)
# ---------------------------------------------------------------------------
class PathWithError:
    def __init__(self, path, sigma, sigma_t=0.0, N_points=10, seed=None):
        self.path_original = path
        self.N_points = N_points
        self.seed = seed

        cart = path.convert_to("Cartesian")
        sv = cart.state_vector
        self._times = sv[0]
        self._xyz_clean = sv[1:4]

        sigma = np.asarray(sigma, dtype=float)
        if sigma.ndim == 0:
            sigma = np.full(3, float(sigma))
        if sigma.shape != (3,):
            raise ValueError(f"sigma must be scalar or shape (3,), got {sigma.shape}")
        self.sigma = sigma
        self.sigma_t = float(sigma_t)

        self._sample()
        self._compute_velocities()

    def _sample(self):
        rng = np.random.default_rng(self.seed)
        T = self._xyz_clean.shape[1]
        N = min(self.N_points, T)
        idx = rng.choice(T, size=N, replace=False)
        idx.sort()
        self.indices = idx
        self.times_clean = self._times[idx]

        time_noise = rng.normal(loc=0.0, scale=self.sigma_t, size=N)
        self.times = self.times_clean + time_noise
        self.time_errors = np.full(N, self.sigma_t)

        self.points_clean = self._xyz_clean[:, idx]
        noise = rng.normal(loc=0.0, scale=self.sigma[:, None], size=(3, N))
        self.points = self.points_clean + noise
        self.errors = np.broadcast_to(self.sigma[:, None], (3, N)).copy()

    def _compute_velocities(self):
        t = self.times
        x = self.points
        sx = self.sigma[:, None]
        st = self.sigma_t

        dt = np.diff(t)
        dx = np.diff(x, axis=1)
        v = dx / dt

        t_mid = 0.5 * (t[1:] + t[:-1])
        x_mid = 0.5 * (x[:, 1:] + x[:, :-1])

        st_mid = np.full_like(t_mid, st / np.sqrt(2))
        sx_mid = np.broadcast_to(sx / np.sqrt(2), v.shape).copy()
        sv = np.sqrt((2.0 * sx**2 + 2.0 * (v * st) ** 2) / dt**2)

        self.times_mid = t_mid
        self.points_mid = x_mid
        self.velocities = v
        self.time_mid_errors = st_mid
        self.point_mid_errors = sx_mid
        self.velocity_errors = sv


def _mc_eq_samples(pwe, i, kerr, N_mc=500, seed=None):
    rng = np.random.default_rng(seed)
    mu_x = pwe.points_mid[:, i]
    s_x = pwe.point_mid_errors[:, i]
    mu_v = pwe.velocities[:, i]
    s_v = pwe.velocity_errors[:, i]
    t = float(pwe.times_mid[i])

    xs = rng.normal(mu_x[:, None], s_x[:, None], size=(3, N_mc))
    vs = rng.normal(mu_v[:, None], s_v[:, None], size=(3, N_mc))
    ts = np.full((1, N_mc), t)
    xs_4 = np.vstack([ts, xs])

    a = kerr.kwargs["a"]
    try:
        cart = Cartesian(xs=xs_4, vels=vs, from_dxs_dt=True)
        bl = cart.convert_to("BoyerLindquist", a=a)
        Es = np.asarray(bl._get_E(kerr), dtype=float)
        Qs = np.asarray(bl._get_Q(kerr), dtype=float)
    except Exception:
        return np.array([]), np.array([])

    ok = np.isfinite(Es) & np.isfinite(Qs)
    return Es[ok], Qs[ok]


def lz_samples_point(pwe, i, N_mc=500, seed=None):
    rng = np.random.default_rng(seed)
    x = rng.normal(pwe.points_mid[0, i], pwe.point_mid_errors[0, i], N_mc)
    y = rng.normal(pwe.points_mid[1, i], pwe.point_mid_errors[1, i], N_mc)
    vx = rng.normal(pwe.velocities[0, i], pwe.velocity_errors[0, i], N_mc)
    vy = rng.normal(pwe.velocities[1, i], pwe.velocity_errors[1, i], N_mc)
    return -(x * vy - y * vx)


def lz_samples_all(pwe, N_mc=500, seed=0):
    N_pts = pwe.points_mid.shape[1]
    return np.stack([lz_samples_point(pwe, i, N_mc, seed + i) for i in range(N_pts)])


def q_samples_all(pwe, kerr, N_mc=500, seed=0):
    N_pts = pwe.points_mid.shape[1]
    out = []
    for i in range(N_pts):
        _, Qs = _mc_eq_samples(pwe, i, kerr, N_mc=N_mc, seed=seed + i)
        out.append(Qs)
    m = min(len(o) for o in out)
    if m < 10:
        raise RuntimeError(f"q_samples_all: muy pocas muestras válidas ({m})")
    return np.stack([o[:m] for o in out])


def joint_pdf_numeric(samples_per_point, grid_size=4096, pad_sigmas=6):
    S = np.asarray(samples_per_point)
    mus = S.mean(axis=1)
    sigmas = S.std(axis=1, ddof=1)
    lo = (mus - pad_sigmas * sigmas).min()
    hi = (mus + pad_sigmas * sigmas).max()
    grid = np.linspace(lo, hi, grid_size)

    log_joint = np.zeros_like(grid)
    for row in S:
        kde = gaussian_kde(row)
        log_joint += np.log(kde(grid) + 1e-300)

    log_joint -= log_joint.max()
    pdf = np.exp(log_joint)
    Z = np.trapezoid(pdf, grid)
    if not np.isfinite(Z) or Z <= 0:
        raise RuntimeError("joint_pdf_numeric: normalización degenerada")
    pdf /= Z
    cdf = cumulative_trapezoid(pdf, grid, initial=0.0)
    cdf /= cdf[-1]
    return grid, pdf, cdf


def sigma_distance(grid, cdf, true_value):
    if true_value < grid[0]:
        F = 1e-12
    elif true_value > grid[-1]:
        F = 1 - 1e-12
    else:
        F = float(np.interp(true_value, grid, cdf))
        F = np.clip(F, 1e-12, 1 - 1e-12)
    return float(norm.ppf(F))


def _one_run(path, sigma_pos, sigma_t, kerr, N, seed, N_mc, Lz_real, Q_real):
    try:
        pwe_n = PathWithError(path, sigma=sigma_pos, sigma_t=sigma_t,
                              N_points=N, seed=seed)
        S_lz = lz_samples_all(pwe_n, N_mc=N_mc, seed=seed)
        gL, _, cL = joint_pdf_numeric(S_lz)
        z_lz = sigma_distance(gL, cL, Lz_real)

        S_q = q_samples_all(pwe_n, kerr, N_mc=N_mc, seed=seed + 10_000)
        gQ, _, cQ = joint_pdf_numeric(S_q)
        z_q = sigma_distance(gQ, cQ, Q_real)
    except Exception as e:
        return {"N": N, "seed": seed, "z_Lz": np.nan, "z_Q": np.nan, "err": repr(e)}
    return {"N": N, "seed": seed, "z_Lz": z_lz, "z_Q": z_q, "err": ""}


def sweep_n_points(path, sigma_pos, sigma_t, kerr, N_list,
                   n_seeds=10, N_mc=300, n_jobs=-1, verbose=0):
    Lz_real = float(path._get_Lz(kerr).mean())
    Q_real = float(path._get_Q(kerr).mean())
    jobs = [(N, s) for N in N_list for s in range(n_seeds)]
    rows = Parallel(n_jobs=n_jobs, backend="loky", verbose=verbose)(
        delayed(_one_run)(path, sigma_pos, sigma_t, kerr,
                          N, s, N_mc, Lz_real, Q_real)
        for (N, s) in jobs
    )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Modelo de error RA/DEC (notebook 009)
# ---------------------------------------------------------------------------
def cartesian_to_radec(xyz_rg, zeta, eta, dist_m, mass_solar):
    """Proyección vectorizada BH-frame → (RA, DEC) en grados + z_LOS en metros.

    Misma convención que EquatorialCoordinate (relatipy): r_sky = Rᵀ r_BH,
    α = arctan2(y_E, d), δ = arctan2(x_N, √(d² + y_E²)).
    xyz_rg: (3, T) en unidades geométricas GM☉/c².
    """
    r_bh_m = np.asarray(xyz_rg, dtype=float) * mass_solar * _L_ref
    R = _build_rotation(np.deg2rad(zeta), np.deg2rad(eta))
    r_sky = R.T @ r_bh_m
    x_n, y_e, z_los = r_sky
    ra = np.degrees(np.arctan2(y_e, dist_m))
    dec = np.degrees(np.arctan2(x_n, np.sqrt(dist_m**2 + y_e**2)))
    return ra, dec, z_los


def radec_to_cartesian(ra_deg, dec_deg, z_los_m, zeta, eta, dist_m, mass_solar):
    """Inversa exacta de cartesian_to_radec. Devuelve (3, N) en r_g."""
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    y_e = dist_m * np.tan(ra)
    x_n = np.tan(dec) * np.sqrt(dist_m**2 + y_e**2)
    r_sky = np.vstack([x_n, y_e, np.asarray(z_los_m, dtype=float)])
    R = _build_rotation(np.deg2rad(zeta), np.deg2rad(eta))
    return (R @ r_sky) / (mass_solar * _L_ref)


class PathWithErrorRADEC(PathWithError):
    """Ruido gaussiano en RA/DEC (µas) en lugar de cartesianas.

    z_LOS verdadera y sin error. Reconstrucción cartesiana exacta; el resto
    del pipeline (velocidades, estimadores) se hereda de PathWithError.
    """

    def __init__(self, path, sigma_radec_uas=SIGMA_RADEC_UAS, zeta=0.0, eta=0.0,
                 distance=DIST_PC * u.pc, mass=M_SGRA,
                 sigma_t=0.0, N_points=10, seed=None):
        self.sigma_radec_uas = float(sigma_radec_uas)
        self.zeta = float(zeta)
        self.eta = float(eta)
        self.dist_m = float(distance.to(u.m).value)
        self.mass_solar = float(mass)

        # σ cartesiano equivalente (ángulos ≪ 1 → lineal): σ_N = σ_E = d·σ_rad.
        sigma_sky_rg = (
            self.dist_m * np.radians(self.sigma_radec_uas / DEG2UAS)
            / (self.mass_solar * _L_ref)
        )
        super().__init__(path, sigma=[sigma_sky_rg, sigma_sky_rg, 0.0],
                         sigma_t=sigma_t, N_points=N_points, seed=seed)

    def _sample(self):
        rng = np.random.default_rng(self.seed)
        T = self._xyz_clean.shape[1]
        N = min(self.N_points, T)
        idx = rng.choice(T, size=N, replace=False)
        idx.sort()
        self.indices = idx

        self.times_clean = self._times[idx]
        time_noise = rng.normal(loc=0.0, scale=self.sigma_t, size=N)
        self.times = self.times_clean + time_noise
        self.time_errors = np.full(N, self.sigma_t)

        self.ra_path, self.dec_path, z_los_path = cartesian_to_radec(
            self._xyz_clean, self.zeta, self.eta, self.dist_m, self.mass_solar
        )
        self.points_clean = self._xyz_clean[:, idx]
        self.ra_clean = self.ra_path[idx]
        self.dec_clean = self.dec_path[idx]
        z_los_true = z_los_path[idx]

        sigma_deg = self.sigma_radec_uas / DEG2UAS
        self.ra_obs = self.ra_clean + rng.normal(0.0, sigma_deg, size=N)
        self.dec_obs = self.dec_clean + rng.normal(0.0, sigma_deg, size=N)
        self.radec_errors = np.full((2, N), sigma_deg)

        self.points = radec_to_cartesian(
            self.ra_obs, self.dec_obs, z_los_true,
            self.zeta, self.eta, self.dist_m, self.mass_solar,
        )
        self.errors = np.broadcast_to(self.sigma[:, None], (3, N)).copy()


def _one_run_radec(path, sigma_uas, sigma_t, kerr, N, seed, N_mc,
                   Lz_real, Q_real, zeta=0.0, eta=0.0,
                   distance=DIST_PC * u.pc, mass=M_SGRA):
    try:
        pwe_n = PathWithErrorRADEC(path, sigma_radec_uas=sigma_uas,
                                   zeta=zeta, eta=eta,
                                   distance=distance, mass=mass,
                                   sigma_t=sigma_t, N_points=N, seed=seed)
        S_lz = lz_samples_all(pwe_n, N_mc=N_mc, seed=seed)
        gL, _, cL = joint_pdf_numeric(S_lz)
        z_lz = sigma_distance(gL, cL, Lz_real)

        S_q = q_samples_all(pwe_n, kerr, N_mc=N_mc, seed=seed + 10_000)
        gQ, _, cQ = joint_pdf_numeric(S_q)
        z_q = sigma_distance(gQ, cQ, Q_real)
    except Exception as e:
        return {"N": N, "seed": seed, "z_Lz": np.nan, "z_Q": np.nan, "err": repr(e)}
    return {"N": N, "seed": seed, "z_Lz": z_lz, "z_Q": z_q, "err": ""}


def sweep_n_points_radec(path, sigma_uas, sigma_t, kerr, N_list,
                         n_seeds=10, N_mc=300, n_jobs=-1, verbose=0,
                         zeta=0.0, eta=0.0,
                         distance=DIST_PC * u.pc, mass=M_SGRA):
    Lz_real = float(path._get_Lz(kerr).mean())
    Q_real = float(path._get_Q(kerr).mean())
    jobs = [(N, s) for N in N_list for s in range(n_seeds)]
    rows = Parallel(n_jobs=n_jobs, backend="loky", verbose=verbose)(
        delayed(_one_run_radec)(path, sigma_uas, sigma_t, kerr,
                                N, s, N_mc, Lz_real, Q_real,
                                zeta, eta, distance, mass)
        for (N, s) in jobs
    )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# IC builder
# ---------------------------------------------------------------------------
def build_ics_bl(spin: float, a: float, e: float, inc_deg: float,
                 Omega_deg: float = OMEGA_S2, omega_deg: float = omega_s2):
    """Construye BoyerLindquist desde elementos orbitales aparentes.

    Replica el patrón comentado en la celda 3 del notebook:
    ApparentOrbitalElements(...).convert_to("BoyerLindquist", a=spin).
    Devuelve (ics_bl, P) donde P es el período orbital.
    """
    ics_app = ApparentOrbitalElements(
        a=a, e=e, inc=inc_deg,
        Omega=Omega_deg, omega=omega_deg,
        zeta=0.0, eta=0.0, mass=M_SGRA,
    )
    P = float(ics_app._get_period())
    ics_bl = ics_app.convert_to("BoyerLindquist", a=spin)
    return ics_bl, P


# ---------------------------------------------------------------------------
# Sweep params reducidos (decisión del plan)
# ---------------------------------------------------------------------------
P_FACTORS = np.round(np.linspace(0.5, 2.0, 6), 3).tolist()
N_LIST = np.arange(10, 101, 10).tolist()
N_SEEDS = 5
N_MC = 300


def run_one_ic(spin: float, a: float, e: float, inc_deg: float,
               bank_dir: str | Path = "./paths_bank_ic_sweep",
               n_jobs: int = -1, noise: str = "cartesian") -> pd.DataFrame:
    """Corre el sweep interno (P_FACTORS × N_LIST × N_SEEDS) para una IC.

    noise: "cartesian" (σ=ERR_POS en xyz) o "radec" (σ=SIGMA_RADEC_UAS en
    el plano del cielo, z_LOS exacta). Mismos paths del bank en ambos casos.
    Devuelve DataFrame con columnas (N, seed, z_Lz, z_Q, err, P_factor).
    Tolera fallos por P_factor (los marca con NaN sin abortar).
    """
    if noise not in ("cartesian", "radec"):
        raise ValueError(f"noise debe ser 'cartesian' o 'radec', no {noise!r}")

    bank = PathsBank(str(bank_dir))
    init_bank(bank)

    kerr = Kerr(1, spin)
    ics_bl, P = build_ics_bl(spin, a, e, inc_deg)

    dfs = []
    for pf in P_FACTORS:
        try:
            path_pf = bank.get_path(
                kerr, ics_bl, np.array([0.0, pf * P]),
                integrator="Radau2",
            )
            if noise == "radec":
                df_pf = sweep_n_points_radec(
                    path_pf, sigma_uas=SIGMA_RADEC_UAS, sigma_t=ERR_TIME,
                    kerr=kerr, N_list=N_LIST, n_seeds=N_SEEDS, N_mc=N_MC,
                    n_jobs=n_jobs,
                )
            else:
                df_pf = sweep_n_points(
                    path_pf, sigma_pos=ERR_POS, sigma_t=ERR_TIME, kerr=kerr,
                    N_list=N_LIST, n_seeds=N_SEEDS, N_mc=N_MC, n_jobs=n_jobs,
                )
        except Exception as ex:
            df_pf = pd.DataFrame([{
                "N": N, "seed": s, "z_Lz": np.nan, "z_Q": np.nan,
                "err": f"path_or_sweep_failed:{ex!r}",
            } for N in N_LIST for s in range(N_SEEDS)])
        df_pf["P_factor"] = pf
        dfs.append(df_pf)

    return pd.concat(dfs, ignore_index=True)


def aggregate_bias(df: pd.DataFrame) -> dict:
    """Reduce el DataFrame del sweep a dos escalares: med|z_Lz|, med|z_Q|."""
    abs_lz = df["z_Lz"].abs()
    abs_q = df["z_Q"].abs()
    return {
        "med_abs_z_Lz": float(np.nanmedian(abs_lz)),
        "med_abs_z_Q": float(np.nanmedian(abs_q)),
        "n_valid_Lz": int(np.isfinite(abs_lz).sum()),
        "n_valid_Q": int(np.isfinite(abs_q).sum()),
        "n_total": int(len(df)),
    }


# ---------------------------------------------------------------------------
# Loaders + plotters (notebook side)
# ---------------------------------------------------------------------------
import json  # noqa: E402

INDEP_AXES = ["spin", "a", "e", "inc"]
PAIR_LIST = [
    ("spin", "a"), ("spin", "e"), ("spin", "i"),
    ("a", "e"), ("a", "i"), ("e", "i"),
]

_AXIS_LABEL = {
    "spin": r"$a_\star$ (spin)",
    "a": r"$a$ (semieje mayor) [$r_g$]",
    "e": "$e$ (excentricidad)",
    "inc": r"$i$ (inclinación) [deg]",
    "i": r"$i$ (inclinación) [deg]",
}


def _pair_key(ax: str) -> str:
    return "inc" if ax == "i" else ax


def load_all_results(results_dir: str | Path = "./bias_ic_results"):
    """Lee manifest + todos los parquets disponibles.

    Devuelve dict:
        {
          "manifest": {...},
          "indep": {axis: DataFrame(idx, value, med_abs_z_Lz, med_abs_z_Q)},
          "pair":  {"spin-a": DataFrame(i, j, v1, v2, med_abs_z_Lz, med_abs_z_Q), ...},
        }
    Tolera ausencia de parquets: solo carga lo que existe.
    """
    rdir = Path(results_dir)
    empty_manifest = {
        "defaults": {}, "indep": {}, "pair_axes": {}, "pairs": [],
        "n_indep": 0, "n_pair_ax": 0,
    }
    if not rdir.exists() or not (rdir / "manifest.json").exists():
        return {"manifest": empty_manifest,
                "indep": {ax: pd.DataFrame() for ax in INDEP_AXES},
                "pair": {f"{a}-{b}": pd.DataFrame() for a, b in PAIR_LIST}}
    manifest = json.loads((rdir / "manifest.json").read_text())

    indep_data = {}
    for ax in INDEP_AXES:
        rows = []
        d = rdir / "indep" / ax
        if not d.exists():
            indep_data[ax] = pd.DataFrame()
            continue
        for f in sorted(d.glob("*.json")):
            try:
                rows.append(json.loads(f.read_text()))
            except Exception:
                pass
        indep_data[ax] = pd.DataFrame(rows) if rows else pd.DataFrame()

    pair_data = {}
    for ax1, ax2 in PAIR_LIST:
        key = f"{ax1}-{ax2}"
        rows = []
        d = rdir / "pair" / key
        if not d.exists():
            pair_data[key] = pd.DataFrame()
            continue
        for f in sorted(d.glob("*.json")):
            try:
                row = json.loads(f.read_text())
                ii, jj = f.stem.split("-")
                row["i"] = int(ii)
                row["j"] = int(jj)
                rows.append(row)
            except Exception:
                pass
        pair_data[key] = pd.DataFrame(rows) if rows else pd.DataFrame()

    return {"manifest": manifest, "indep": indep_data, "pair": pair_data}


def plot_independent(res: dict, metric: str = "both", figsize=(11, 8.5)):
    """Grafica los 4 barridos 1D en grid 2×2.

    metric: 'lz' | 'q' | 'both' (dos curvas por panel).
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=figsize)
    layout = [("spin", axes[0, 0]), ("a", axes[0, 1]),
              ("e", axes[1, 0]), ("inc", axes[1, 1])]

    for ax_name, ax in layout:
        df = res["indep"].get(ax_name, pd.DataFrame())
        ax.set_xlabel(_AXIS_LABEL[ax_name])
        ax.set_ylabel(r"mediana $|z|$")
        ax.grid(True, alpha=0.3)
        if df.empty:
            ax.set_title(f"{ax_name} — sin datos aún")
            continue
        df = df.sort_values(ax_name)
        x = df[ax_name].values
        if metric in ("lz", "both"):
            ax.plot(x, df["med_abs_z_Lz"], "o-", ms=3, lw=1.0,
                    color="steelblue", label=r"$|z_{L_z}|$")
        if metric in ("q", "both"):
            ax.plot(x, df["med_abs_z_Q"], "s-", ms=3, lw=1.0,
                    color="firebrick", label=r"$|z_Q|$")
        ax.axhline(1.0, color="gray", ls="--", lw=0.8, alpha=0.6)
        ax.axhline(3.0, color="gray", ls=":", lw=0.8, alpha=0.6)
        ax.set_title(f"{ax_name}  (n={len(df)})")
        ax.legend(fontsize=8)

    fig.suptitle("Sesgo vs IC — ejes independientes", fontsize=12)
    fig.tight_layout()
    return fig


def _grid_from_pair(df: pd.DataFrame, ax1: str, ax2: str, manifest: dict,
                    value_col: str):
    """Reconstruye matriz 10×10 desde rows (i, j, value). NaN donde falta."""
    k1, k2 = _pair_key(ax1), _pair_key(ax2)
    v1 = np.array(manifest["pair_axes"][k1])
    v2 = np.array(manifest["pair_axes"][k2])
    n1, n2 = len(v1), len(v2)
    Z = np.full((n1, n2), np.nan)
    for _, r in df.iterrows():
        i, j = int(r["i"]), int(r["j"])
        if 0 <= i < n1 and 0 <= j < n2:
            Z[i, j] = r[value_col]
    return v1, v2, Z


def plot_joint(res: dict, metric: str = "lz", figsize=(14, 12), levels=12):
    """Grafica los 6 contornos 2D en layout triangular.

    Layout (filas crecientes en nº paneles):
        spin-a
        spin-e | a-e
        spin-i | a-i | e-i

    metric: 'lz' o 'q' (una figura por métrica).
    """
    import matplotlib.pyplot as plt

    value_col = "med_abs_z_Lz" if metric == "lz" else "med_abs_z_Q"
    title = (r"$|z_{L_z}|$" if metric == "lz" else r"$|z_Q|$")

    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 3, hspace=0.32, wspace=0.32)
    layout = [
        (("spin", "a"), fig.add_subplot(gs[0, 0])),
        (("spin", "e"), fig.add_subplot(gs[1, 0])),
        (("a",    "e"), fig.add_subplot(gs[1, 1])),
        (("spin", "i"), fig.add_subplot(gs[2, 0])),
        (("a",    "i"), fig.add_subplot(gs[2, 1])),
        (("e",    "i"), fig.add_subplot(gs[2, 2])),
    ]

    for (ax1, ax2), ax in layout:
        key = f"{ax1}-{ax2}"
        df = res["pair"].get(key, pd.DataFrame())
        ax.set_xlabel(_AXIS_LABEL[ax2])
        ax.set_ylabel(_AXIS_LABEL[ax1])
        if df.empty:
            ax.set_title(f"{key} — sin datos aún")
            continue
        v1, v2, Z = _grid_from_pair(df, ax1, ax2, res["manifest"], value_col)
        X, Y = np.meshgrid(v2, v1)
        finite_mask = np.isfinite(Z)
        if finite_mask.sum() < 3:
            ax.set_title(f"{key}  ({finite_mask.sum()} pts)")
            continue
        cf = ax.contourf(X, Y, Z, levels=levels, cmap="viridis")
        cs = ax.contour(X, Y, Z, levels=levels, colors="black",
                        linewidths=0.5, alpha=0.6)
        ax.clabel(cs, inline=True, fontsize=7, fmt="%.2f")
        fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.04)
        ax.set_title(f"{key}  ({finite_mask.sum()}/{Z.size})")

    fig.suptitle(f"Sesgo conjunto — {title}", fontsize=12)
    return fig
