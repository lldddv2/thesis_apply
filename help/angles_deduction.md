# Relation between Dayem (θ, β) and RelatiPy (ζ, η)

## Conventions

**RelatiPy `ApparentOrbitalElements`** — sky frame $(\hat{x}_{\mathrm{sky}}, \hat{y}_{\mathrm{sky}}, \hat{z}_{\mathrm{sky}})$ with $\hat{z}_{\mathrm{sky}}$ along the line of sight (LOS):

$$
\hat{s}_{\mathrm{sky}} = (\sin\zeta\cos\eta,\; \sin\zeta\sin\eta,\; \cos\zeta).
$$

- $\zeta$ = polar angle of spin from LOS, $\zeta\in[0,\pi]$
- $\eta$ = position angle of spin projection in sky plane, measured from $\hat{x}_{\mathrm{sky}}$, $\eta\in[0,2\pi)$

**Dayem 2025 (Appendix B, Fig. B.1)** — observer/sky frame $(\mathbf{X}, \mathbf{Y}, \mathbf{Z})$ with $\mathbf{Z}$ along LOS. Eq. (B.4):

$$
\mathbf{z}_{bh} = \sin i'\cos\Omega'\,\mathbf{X} + \sin i'\sin\Omega'\,\mathbf{Y} + \cos i'\,\mathbf{Z}.
$$

- $i'$ = polar angle of spin from LOS
- $\Omega'$ = azimuth of spin from $\mathbf{X}$ in the sky plane

**Dayem $(\theta, \beta)$** — orbit-frame description, Fig. 2:

- $\theta\in[0,\pi]$ = angle between $\mathbf{z}_{\mathrm{orb}}$ and $\mathbf{z}_{bh}$
- $\beta\in[0,2\pi]$ = rotation about $\mathbf{z}_{\mathrm{orb}}$ from line of nodes $\mathcal{L}_{\mathrm{orb//sky}}$ to projection of $\mathbf{z}_{bh}$ on the orbit plane
- Auxiliary: $\psi \equiv \beta - \omega$ (observer-independent)

## Direct identification: $(\zeta,\eta) = (i',\Omega')$

Comparing RelatiPy $\hat{s}_{\mathrm{sky}}$ with Dayem Eq. (B.4) component by component:

$$
\boxed{\;\zeta = i', \qquad \eta = \Omega'.\;}
$$

Same convention: polar angle from LOS and azimuth in sky plane from sky $\mathbf{X}$. RelatiPy's $(\zeta,\eta)$ is exactly Dayem's $(i',\Omega')$.

> Note: RelatiPy stores the LOS in the BH Cartesian frame as $\hat{d} = (-\sin\zeta, 0, \cos\zeta)$. That is the inverse rotation $R_z(-\eta)R_y(-\zeta)$ applied to $\hat{Z}_{\mathrm{sky}}$: the η-rotation is absorbed by aligning BH-x with the projection axis, leaving the LOS in the BH xz-plane.

## Derivation: $(\theta,\beta)\;\leftrightarrow\;(\zeta,\eta,\iota,\Omega,\omega)$

From Dayem Eq. (B.5) (i.e. the three scalar products $\mathbf{z}_{bh}\cdot\{\mathbf{n}_{\mathrm{orb}}, \mathbf{m}_{\mathrm{orb}}, \mathbf{z}_{\mathrm{orb}}\}$), evaluated at $\varphi=0$ (so $\mathbf{n}_{\mathrm{orb}}\to$ ascending-node direction, $\mathbf{m}_{\mathrm{orb}}\to$ in-plane tangent):

$$
\begin{align*}
\sin\theta\cos\beta &= \sin i'\cos(\Omega-\Omega'),\\
\sin\theta\sin\beta &= \cos i'\sin\iota - \sin i'\cos\iota\sin(\Omega-\Omega'),\\
\cos\theta &= \cos i'\cos\iota + \sin i'\sin\iota\sin(\Omega-\Omega').
\end{align*}
$$

Substituting $i'=\zeta$, $\Omega'=\eta$:

$$
\boxed{\;
\begin{align*}
\cos\theta &= \cos\zeta\cos\iota + \sin\zeta\sin\iota\sin(\Omega-\eta),\\
\sin\theta\cos\beta &= \sin\zeta\cos(\Omega-\eta),\\
\sin\theta\sin\beta &= \cos\zeta\sin\iota - \sin\zeta\cos\iota\sin(\Omega-\eta).
\end{align*}
\;}
$$

Equivalently, using $\psi = \beta - \omega$:

$$
\begin{align*}
\tan\beta &= \frac{\cos\zeta\sin\iota - \sin\zeta\cos\iota\sin(\Omega-\eta)}{\sin\zeta\cos(\Omega-\eta)},\\
\theta &= \arccos\!\big[\cos\zeta\cos\iota + \sin\zeta\sin\iota\sin(\Omega-\eta)\big].
\end{align*}
$$

## Inverse: $(\zeta,\eta)\leftarrow(\theta,\beta,\iota,\Omega,\omega)$

The spin in the orbit frame is (Dayem Eq. 50):

$$
\mathbf{z}_{bh} = \sin\theta\cos\psi\,\mathbf{x}_{\mathrm{orb}} + \sin\theta\sin\psi\,\mathbf{y}_{\mathrm{orb}} + \cos\theta\,\mathbf{z}_{\mathrm{orb}}, \qquad \psi = \beta - \omega.
$$

Rotating to the sky frame with the standard Euler rotation $R_z(\Omega)R_x(\iota)R_z(\omega)$ and matching to $\hat{s}_{\mathrm{sky}}=(\sin\zeta\cos\eta, \sin\zeta\sin\eta, \cos\zeta)$ gives:

$$
\boxed{\;
\begin{align*}
\cos\zeta &= \sin\theta\sin\psi\sin\iota + \cos\theta\cos\iota,\\
\sin\zeta\cos(\eta-\Omega) &= \sin\theta\cos\psi,\\
\sin\zeta\sin(\eta-\Omega) &= \cos\theta\sin\iota - \sin\theta\sin\psi\cos\iota.
\end{align*}
\;}
$$

## Summary table

| RelatiPy | Dayem | Frame | Meaning |
|---|---|---|---|
| $\zeta$ | $i'$ | sky | polar angle of spin from LOS |
| $\eta$ | $\Omega'$ | sky | azimuth of spin projection in sky plane from $\hat{x}_{\mathrm{sky}}$ |
| — | $\theta$ | orbit | angle between $\mathbf{z}_{\mathrm{orb}}$ and $\mathbf{z}_{bh}$ |
| — | $\beta$ | orbit | azimuth of spin projection in orbit plane from line of nodes |
| — | $\psi=\beta-\omega$ | orbit | observer-independent azimuth of spin in orbit frame |

## Limits / sanity checks

- **Face-on orbit** ($\iota=0$): $\cos\theta=\cos\zeta$, so $\theta=\zeta$. The line of nodes is degenerate, so $\beta$ depends on the chosen reference; the relations give $\sin\theta\cos\beta=\sin\zeta\cos(\Omega-\eta)$, $\sin\theta\sin\beta=-\sin\zeta\cos(\Omega-\eta)\cdot 0$, recovering $\beta = \Omega-\eta$ (modulo convention).
- **Spin along LOS** ($\zeta=0$): $\cos\theta=\cos\iota$, so $\theta=\iota$, and the spin lies along $\mathbf{Z}=\hat{z}_{\mathrm{sky}}$.
- **Spin in sky plane** ($\zeta=\pi/2$): $\cos\theta=\sin\iota\sin(\Omega-\eta)$. Reduces to standard inclination of two great circles.
