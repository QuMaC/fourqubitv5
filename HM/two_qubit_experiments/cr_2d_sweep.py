#need to sweep amplitude and duration of the CR sequence
# then I need to measure the population about two/three axes
# then I plot the radial vector of the population in one color plot and
#the phase of the two qubits in another color plot?
# to get the expectation values I need to take the rabi oscillation min and max val after rotation
# or I need to average over shots. 
# for shots I need to classify each shot. 
# for signal I just need to rotate the IQ data. 
"""
GRAPE with echo for Q1-Q4 CR gate
Sign convention flipped (phase -> -phase) to match hardware.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.optimize import minimize

# ─── Params ─────────────────────────────────────────────
wc, wt = 5.085103, 4.964174       # GHz
ac, at = -0.2672, -0.2680         # GHz
J      = 0.003032                 # GHz
T_rise, T_flat, T_fall = 16.0, 272.0, 16.0
T_cr   = T_rise + T_flat + T_fall    # 304 ns per CR half
T_pi   = 52.0                        # π pulse duration on Q1
amp_to_MHz = 16.70
amp_norm   = 0.5587
amp_MHz    = amp_norm*amp_to_MHz     # 9.33 MHz
amp_GHz    = amp_MHz*1e-3
phase      = -0.4384                 # SIGN FLIPPED to match hardware convention
sigma      = T_rise/2

u_max_GHz  = amp_to_MHz*1e-3         # 1.0 norm = 16.7 MHz

hw_dt = 4.0
dt    = hw_dt
N_cr  = int(round(T_cr/dt))   # 76 slices per CR half
N_pi  = int(round(T_pi/dt))   # 13 slices per π pulse
print(f"Slices: {N_cr} per CR half, {N_pi} per π, dt={dt} ns")

# ─── Operators ──────────────────────────────────────────
NLEV = 3; DIM = 9
a3 = np.zeros((3,3), dtype=complex)
for i in range(2): a3[i,i+1] = np.sqrt(i+1)
adag = a3.conj().T; n3 = adag@a3; I3 = np.eye(3, dtype=complex)

def Htr(w, al): return 2*np.pi*(w*n3 + (al/2)*n3@(n3-I3))
H_drift = (np.kron(Htr(wc-wt, ac), I3)
           + np.kron(I3, Htr(0.0, at))
           + 2*np.pi*J*(np.kron(a3,adag) + np.kron(adag,a3)))
Xc = 2*np.pi*np.kron(a3+adag, I3)
Yc = 2*np.pi*np.kron(1j*(adag-a3), I3)

# ─── π pulse on Q1 (fixed, not optimised) ───────────────
# Q1 π pulse in rotating frame at wt → off-resonant from Q1 by (wc-wt)
# Rabi rate for π in 52ns: Ω = π/(52 ns) in angular → 9.615 MHz
Omega_pi_MHz = 1.0/(2*T_pi)*1e3   # MHz = 9.615
Omega_pi_GHz = Omega_pi_MHz*1e-3

# Q1 pulse is on resonance with Q1 → in our frame (rotating at wt) it oscillates at (wc-wt)
# Simpler: apply it as a separate "exact" Xπ on the control qubit (treat as instantaneous in logic,
# but use the full 52 ns duration with correct phase to get correct accumulated drift)
def pi_pulse_propagator():
    """Propagator for a 52-ns π pulse on Q1 at resonance (in lab frame)."""
    # In rotating frame at wt, the Q1 drive at its resonance (wc) shows up as an off-resonant
    # drive at detuning (wc-wt). But IF we model the π pulse as applied at wc in the hardware
    # frame, the ideal effect on Q1 is Rx(π). Approximate by applying a short drive at wc.
    U = np.eye(DIM, dtype=complex)
    N_slices = N_pi
    for _ in range(N_slices):
        # drive on Q1 at its own frequency → need to be in Q1's rotating frame
        # Approximation: apply ideal X_c on control with phases absorbed
        pass
    # Simplest: apply exact Rx(π) on Q1 computational subspace, identity on rest
    Rx_pi = np.array([[0, -1j, 0],[-1j, 0, 0],[0, 0, 1]], dtype=complex)  # Rx(π) in 3-level
    U_pi = np.kron(Rx_pi, I3)
    # Now need to include drift for 52 ns (free evolution between pulses happens during π)
    U_drift = expm(-1j*H_drift*T_pi)
    return U_pi @ U_drift  # π pulse then drift (or drift then π — approximation)

U_pi_ctrl = pi_pulse_propagator()

# ─── ZX_90 target ──────────────────────────────────────
comp_idx = [0,1,3,4]; d=4
c2 = 1/np.sqrt(2)
ZX = c2*np.array([[1,-1j,0,0],[-1j,1,0,0],[0,0,1,1j],[0,0,1j,1]], dtype=complex)
U_target = np.eye(DIM, dtype=complex)
for i,ri in enumerate(comp_idx):
    for j,rj in enumerate(comp_idx): U_target[ri,rj] = ZX[i,j]
P = np.zeros((DIM,DIM), dtype=complex)
for idx in comp_idx: P[idx,idx] = 1.0

# ─── Propagation ──────────────────────────────────────
def slice_prop(uI, uQ):
    H = H_drift + uI*Xc + uQ*Yc
    return expm(-1j*H*dt)

def cr_half_propagator(u):
    U = np.eye(DIM, dtype=complex)
    for k in range(N_cr):
        U = slice_prop(u[k,0], u[k,1]) @ U
    return U

def echoed_propagator(u):
    """
    Sequence: CR(+u)  ·  X_π  ·  CR(-u)  ·  X_π
    Returns the full unitary.
    """
    U1 = cr_half_propagator(u)
    U2 = cr_half_propagator(-u)   # phase flip = negate amplitudes
    U_full = U_pi_ctrl @ U2 @ U_pi_ctrl @ U1
    return U_full

def neg_fidelity(u_flat):
    u = u_flat.reshape(N_cr, 2)
    U_full = echoed_propagator(u)
    M = U_target.conj().T @ P @ U_full @ P
    F = abs(np.trace(M))**2 / d**2
    return -F

# ─── Gaussian flat-top seed ───────────────────────────
def gaussian_flattop(t, amp, sig, tr, tf, ph):
    te = tr + tf
    env = np.where(t<tr, np.exp(-0.5*((t-tr)/sig)**2),
           np.where(t<=te, 1.0, np.exp(-0.5*((t-te)/sig)**2)))
    env *= amp
    return np.column_stack([env*np.cos(ph), env*np.sin(ph)])

t_arr = np.arange(N_cr)*dt + dt/2
u_seed = gaussian_flattop(t_arr, amp_GHz, sigma, T_rise, T_flat, phase)
F_seed = -neg_fidelity(u_seed.ravel())
print(f"\nSeed (calibrated pulse, echoed): F = {F_seed:.6f}")
print(f"  infidelity = {1-F_seed:.2e}")

# ─── Stage 1: parametric (amp, phase, sigma) ──────────
def neg_F_param(params):
    amp_M, ph, sig = params
    u = gaussian_flattop(t_arr, amp_M*1e-3, sig, T_rise, T_flat, ph)
    return neg_fidelity(u.ravel())

print("\nStage 1 — parametric (amp, phase, sigma)")
res1 = minimize(neg_F_param, [amp_MHz, phase, sigma],
                method='L-BFGS-B',
                bounds=[(0.0, 16.7), (-np.pi, np.pi), (2.0, T_rise)],
                options={'maxiter': 80, 'ftol': 1e-10, 'eps': 1e-5})
amp1, ph1, sig1 = res1.x
F1 = -res1.fun
print(f"  amp = {amp1:.3f} MHz  phase = {ph1:.4f} rad  sigma = {sig1:.3f} ns")
print(f"  F = {F1:.6f}  (infidelity = {1-F1:.2e})")

u_stage1 = gaussian_flattop(t_arr, amp1*1e-3, sig1, T_rise, T_flat, ph1)

# ─── Stage 2: full GRAPE ──────────────────────────────
print("\nStage 2 — full I/Q GRAPE (init from Stage 1)")
F_hist = [F1]
def cb(x): F_hist.append(-neg_fidelity(x))

bounds2 = [(-u_max_GHz, u_max_GHz)]*(N_cr*2)
res2 = minimize(neg_fidelity, u_stage1.ravel(), method='L-BFGS-B',
                bounds=bounds2, callback=cb,
                options={'maxiter': 300, 'ftol': 1e-13, 'gtol': 1e-8, 'eps': 1e-7})
u_final = res2.x.reshape(N_cr, 2)
F_final = -res2.fun
print(f"  iterations: {len(F_hist)-1}")
print(f"  F_final = {F_final:.6f}  (infidelity = {1-F_final:.2e})")
print(f"  improvement: {(F_final-F1):+.4e}")

# ─── Save ──────────────────────────────────────────────
u_final_MHz  = u_final*1e3
u_final_norm = u_final_MHz/amp_to_MHz
np.savez('grape_q1q4_echoed.npz',
         t=t_arr, uI_MHz=u_final_MHz[:,0], uQ_MHz=u_final_MHz[:,1],
         uI_norm=u_final_norm[:,0], uQ_norm=u_final_norm[:,1],
         F_seed=F_seed, F_stage1=F1, F_final=F_final,
         F_history=np.array(F_hist))
print("Saved grape_q1q4_echoed.npz")

# ─── Plot ──────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(12, 9))
fig.patch.set_facecolor('#0f1117')

u_seed_M = u_seed*1e3
u_s1_M   = u_stage1*1e3

ax = axes[0]; ax.set_facecolor('#0f1117')
ax.plot(t_arr, u_seed_M[:,0], color='#888', lw=1.0, ls='--', label='Seed I (calibrated)')
ax.plot(t_arr, u_seed_M[:,1], color='#666', lw=1.0, ls='--', label='Seed Q')
ax.set_xlim(0, T_cr); ax.set_ylabel('MHz', color='#ccc')
ax.set_title(f'Stage 0 — Seed pulse (1 CR half)   |   F_echo = {F_seed:.4f}',
             color='white', fontsize=11)
ax.legend(facecolor='#1e1e2e', labelcolor='white', fontsize=9, loc='upper right')
ax.tick_params(colors='#aaa')
for s in ax.spines.values(): s.set_color('#333')

ax = axes[1]; ax.set_facecolor('#0f1117')
ax.plot(t_arr, u_s1_M[:,0], color='#4fc3f7', lw=1.5, label='Stage 1 I')
ax.plot(t_arr, u_s1_M[:,1], color='#ef5350', lw=1.5, alpha=0.85, label='Stage 1 Q')
ax.plot(t_arr, u_final_MHz[:,0], color='#00e676', lw=1.8, label='Stage 2 I (GRAPE)')
ax.plot(t_arr, u_final_MHz[:,1], color='#ffb74d', lw=1.8, alpha=0.9, label='Stage 2 Q (GRAPE)')
ax.axhline(0, color='#444', lw=0.6, ls='--')
ax.set_xlim(0, T_cr); ax.set_ylabel('MHz', color='#ccc')
ax.set_title(f'Stage 1 → Stage 2   |   F = {F1:.4f} → {F_final:.4f}',
             color='white', fontsize=11)
ax.legend(facecolor='#1e1e2e', labelcolor='white', fontsize=9, ncol=2, loc='upper right')
ax.tick_params(colors='#aaa')
for s in ax.spines.values(): s.set_color('#333')

ax = axes[2]; ax.set_facecolor('#0f1117')
it = np.arange(len(F_hist))
ax.plot(it, 1-np.array(F_hist), color='#a5d6a7', lw=1.8)
ax.fill_between(it, 1-np.array(F_hist), alpha=0.15, color='#a5d6a7')
ax.set_yscale('log')
ax.set_xlim(0, max(1, len(F_hist)-1))
ax.set_xlabel('Iteration', color='#ccc'); ax.set_ylabel('Infidelity', color='#ccc')
ax.set_title('Convergence (Stage 2)', color='white', fontsize=11)
ax.grid(alpha=0.15, color='#444')
ax.tick_params(colors='#aaa')
for s in ax.spines.values(): s.set_color('#333')

plt.tight_layout()
plt.savefig('grape_q1q4_echoed.png', dpi=150, facecolor='#0f1117')
print("Saved grape_q1q4_echoed.png")