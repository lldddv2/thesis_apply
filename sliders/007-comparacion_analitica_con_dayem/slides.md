---
title: "Comparación analítica con Dayem"
author: "Luis Daniel Díaz Durango"
date: "2026-05-12"
start_date: "2026-05-06"
end_date: "2026-05-12"
active: true
---

type: title

---

type: toc

---

header: "Anuncios"
footer: "Luis D. Díaz — 2026-05-12"
task: announcement

## Anuncios

- **CEFVA 2026** — 20 y 21 de mayo
- Por lo tanto, no habrá reunión esa semana

---

header: "Coordenadas del spin"
footer: "Luis D. Díaz — 2026-05-12"
task: library

## Orientación del spin

Spin de Sgr A* parametrizado por:

$$\zeta \in [0°, 180°], \quad \eta \in [0°, 360°]$$

→ `ApparentOrbitalElements`: relación entre marco del agujero negro y elementos orbitales observados.

<!-- row -->

<!-- html:"spin_axis_sky_coords_v7.html"-->

<!-- col -->

<!-- html:"orbit_coordinate_validation.html"-->

---

header: "S2 — spin en línea de la visual"
footer: "Luis D. Díaz — 2026-05-12"
task: scientific_result

## Setup ($\zeta = 0°$)

- Parámetros orbitales S2 (GRAVITY 2020)
- $\chi = 0.9$, barrido $\chi \in \{0.1, 0.3, 0.5, 0.7, 0.9\}$
- Comparación: Dayem (2025) vs geodésica Kerr exacta (Fujita)

**Error en $\Delta\omega$: $\sim 2 \times 10^{-4}$ °/órbita**


<!-- img:"s2_spin_sweep_errors.jpg"-->

---

header: "Barrido en $\zeta$"
footer: "Luis D. Díaz — 2026-05-12"
task: scientific_result

## Setup ($\chi = 0.9$)

$\zeta \in \{15°, 30°, 45°, 60°, 75°\}$ con parámetros de S2.

Las tres precesiones ($\Delta\omega$, $\Delta\iota$, $\sin\iota\cdot\Delta\Omega$) concuerdan en todos los casos.

Error en $\Delta\omega$: $\sim 10^{-4}$ °/órbita, débil dependencia en $\zeta$.


<!-- img:"sweep_zeta_comparison.jpg"-->

---

type: next-steps

- Terminar coordenadas ecuatoriales (RA y DEC)
- Barrido $\zeta$, $\eta$, $a \in \pm[0.8, 1)$ con paso $0.01$
- Inferencia bayesiana: $P(\zeta, \eta, a \mid \Delta\text{RA}, \Delta\text{DEC})$
