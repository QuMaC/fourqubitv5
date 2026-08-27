"""
legacy_engine_demos.py
======================
The demo / sanity-check functions that used to live at the bottom of
``engine/two_q_pulse_sim.py``: the hard-wired c1t2 setup, the bare and
echoed CR duration sweeps. Kept for reference; the maintained versions of
these sweeps are the experiment classes in this folder (``cr_len_sweep.py``
etc.), which build their device from ``TwoQubitSimulatorBase``.
"""

import numpy as np
import qutip as qt

from Configuration_Files.config_dictionaries import *
from HM.simulator.two_qubit_simulator.base_classes.device_base import (
    DriveLine,
    Qubit,
)
from HM.simulator.two_qubit_simulator.engine.pulses import (
    Timeline,
    flat_pulse_for_rotation,
    gaussian_flat_top,
)
from HM.simulator.two_qubit_simulator.engine.two_q_pulse_sim import (
    TwoQubitPulseSimulator,
)


def build_c1t2_demo() -> TwoQubitPulseSimulator:

    # qubit-qubit detuning: validate_simulator.py notes the CR drive sits
    # 103 MHz from Q1 on its mixer, i.e. f_Q1 - f_Q2 = 103 MHz.
    DELTA_QQ_MHZ = fq_vals["fq_vals"]["1"] - fq_vals["fq_vals"]["2"]
    J_MHZ        = coupling_vals["c1_t2"]["J_mhz"]                    # validate_simulator.py
    ALPHA1_MHZ   = anharmonicities["1"]                    # PLACEHOLDER -> anharmonicities.json
    ALPHA2_MHZ   = anharmonicities["2"]                    # PLACEHOLDER -> anharmonicities.json

    # Frames = own frequencies; only the difference matters. Q1 at 0,
    # Q2 sits 103 MHz below.
    qubits = [
        Qubit(anharm_MHz=ALPHA1_MHZ, frame_MHz=0.0,           n_levels=3),
        Qubit(anharm_MHz=ALPHA2_MHZ, frame_MHz=-DELTA_QQ_MHZ, n_levels=3),
    ]
    # q1_drive / q2_drive: self-drives (carrier = own frame -> detuning 0).
    # cr_drive: control's line (target=0) at the TARGET's frequency
    # (carrier = -DELTA_QQ) -> detuning -103 MHz. This is cross-resonance.
    drive_lines = [
        DriveLine(name="q1_drive", target=0, carrier_MHz=0.0),
        DriveLine(name="q2_drive", target=1, carrier_MHz=-DELTA_QQ_MHZ),
        DriveLine(name="cr_drive", target=0, carrier_MHz=-DELTA_QQ_MHZ),
    ]
    # PLACEHOLDER confusion matrices, M[measured, prepared] -> Chapter 8 readout.
    M1 = np.array([[0.98, 0.03], [0.02, 0.97]])
    M2 = np.array([[0.96, 0.05], [0.04, 0.95]])

    return TwoQubitPulseSimulator(qubits, J_MHZ, drive_lines, (M1, M2))


def _fmt(counts: dict[str, int]) -> str:
    tot = sum(counts.values())
    return "  ".join(f"{k}:{v:5d} ({100*v/tot:5.1f}%)" for k, v in counts.items())


def main() -> None:
    sim = build_c1t2_demo()
    channels = list(sim.drive_lines)
    rng = np.random.default_rng(0)

    print("=" * 70)
    print("two_qubit_pulse_sim.py  --  demo / sanity checks (QuTiP build)")
    print("=" * 70)
    print(f"Hilbert space dim      : {sim.dim} (two qutrits)")
    print(f"qubit-qubit detuning   : {sim.delta_qq_MHz:+.1f} MHz")
    print(f"coupling J             : {sim.J_MHz:.4f} MHz")
    print()

    # -- Check 1: idle ------------------------------------------------------
    # An empty timeline from |00> must stay |00>; from |01> it should stay
    # ~|01> (coupling to |10> is off-resonant, suppressed by J/Delta ~ 0.03).
    idle = {ch: np.zeros(60, dtype=complex) for ch in channels}   # 240 ns

    psi = sim.run_shot(idle, psi0=None)                            # |00>
    counts, info = sim.measure(psi, 8192, apply_confusion=False, rng=rng)
    print("Check 1a  idle from |00>, no confusion")
    print("          ", _fmt(counts), f"  leakage={info['leakage']:.2e}")

    counts, info = sim.measure(psi, 8192, apply_confusion=True, rng=rng)
    print("Check 1b  idle from |00>, WITH confusion (readout error visible)")
    print("          ", _fmt(counts))

    psi01 = qt.basis(sim.dims, [0, 1])                             # |01>
    psi = sim.run_shot(idle, psi0=psi01)
    counts, info = sim.measure(psi, 8192, apply_confusion=False, rng=rng)
    print("Check 1c  idle from |01>, no confusion (off-resonant coupling)")
    print("          ", _fmt(counts), f"  leakage={info['leakage']:.2e}")
    print()

    # -- Check 2: X90 on the control ---------------------------------------
    # Self-drive (detuning 0). |00> -> control in equal superposition.
    tl = Timeline(channels)
    x90 = flat_pulse_for_rotation(np.pi / 2, duration_ns=40.0)
    tl.add("q1_drive", start_ns=0.0, waveform=x90)
    psi = sim.run_shot(tl.finalize(), psi0=None)
    counts, info = sim.measure(psi, 8192, apply_confusion=False, rng=rng)
    print("Check 2   X90 on control (q1_drive), no confusion -- expect ~50/50 00,10")
    print("          ", _fmt(counts), f"  leakage={info['leakage']:.2e}")
    print()

    # -- Check 3: CR conditional rotation ----------------------------------
    # Same CR pulse from |00> and from |10>. The target's response must DIFFER
    # between the two -- that conditional rotation is what makes CR a gate.
    # This exercises the detuned-drive (delta != 0) path.
    tl = Timeline(channels)
    cr = gaussian_flat_top(amp=30.0, t_rise_ns=16, t_flat_ns=300, sigma_ns=5)
    tl.add("cr_drive", start_ns=0.0, waveform=cr)
    cr_timeline = tl.finalize()

    psi_c0 = sim.run_shot(cr_timeline, psi0=None)                  # control |0>
    psi10 = qt.basis(sim.dims, [1, 0])
    psi_c1 = sim.run_shot(cr_timeline, psi0=psi10)                 # control |1>

    def p_target_excited(psi):
        _, info = sim.measure(psi, 1, apply_confusion=False, rng=rng)
        p = info["probs_ideal"]              # [00,01,10,11]
        return p[1] + p[3]                   # target bit = 1

    pt0 = p_target_excited(psi_c0)
    pt1 = p_target_excited(psi_c1)
    print("Check 3   CR pulse on cr_drive -- target rotation conditioned on control")
    print(f"          P(target=1 | control=0) = {pt0:.4f}")
    print(f"          P(target=1 | control=1) = {pt1:.4f}")
    print(f"          conditional difference  = {abs(pt1 - pt0):.4f}"
          "   (non-zero => CR is acting)")
    print()
    print("All four code paths exercised: idle, self-drive, detuned (CR) drive,")
    print("measurement + confusion + sampling. Next: Phase 2 regression against")
    print("validate_simulator.py's six measured generators, then the Bell timeline.")


def cr_duration_sweep() -> None:
    """Sheldon-style CR Rabi: sweep CR pulse duration at fixed amplitude,
    measure <X>, <Y>, <Z> on the target for control prepared in |0> and |1>.
    Expectations computed directly from the state vector (no basis-rotation
    pulses) -- isolates the CR physics."""
    import matplotlib.pyplot as plt

    sim = build_c1t2_demo()
    channels = list(sim.drive_lines)

    # ----- sweep parameters -----
    AMP_MHZ      = 60.0          # CR Rabi amplitude on the target
    T_RISE_NS    = 16.0
    SIGMA_NS     = 5.0
    DURATIONS_NS = np.arange(20, 2004, 20)   # flat-top widths to sweep

    # ----- target single-qubit Pauli operators on the joint qutrit space -----
    # X_2 = b2^dag + b2, Y_2 = i(b2^dag - b2), Z_2 = I - 2 b2^dag b2
    # ...all projected onto the {|0>,|1>} subspace of qubit 2 (leakage ignored).
    n0, n1 = sim.dims
    I0 = qt.qeye(n0)
    # 2-level projector on qutrit-2
    P01_2 = qt.Qobj(np.diag([1, 1, 0]).astype(complex))
    sx_2 = qt.Qobj(np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex))
    sy_2 = qt.Qobj(np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex))
    sz_2 = qt.Qobj(np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex))
    X_op = qt.tensor(I0, sx_2)
    Y_op = qt.tensor(I0, sy_2)
    Z_op = qt.tensor(I0, sz_2)

    # ----- sweep -----
    psi00 = qt.basis(sim.dims, [0, 0])
    psi10 = qt.basis(sim.dims, [1, 0])
    results = {0: {"X": [], "Y": [], "Z": []},
               1: {"X": [], "Y": [], "Z": []}}

    for t_flat in DURATIONS_NS:
        tl = Timeline(channels)
        cr = gaussian_flat_top(amp=AMP_MHZ, t_rise_ns=T_RISE_NS,
                               t_flat_ns=float(t_flat), sigma_ns=SIGMA_NS)
        tl.add("cr_drive", start_ns=0.0, waveform=cr)
        timeline = tl.finalize()

        print(f"  t_flat = {t_flat:4d} ns  done")

    # ----- plot -----
    fig, axes = plt.subplots(4, 1, figsize=(8, 7), sharex=True)
    total_durations = DURATIONS_NS + 2 * T_RISE_NS   # total pulse length

    for ax, comp in zip(axes, ["X", "Y", "Z"]):
        ax.plot(total_durations, results[0][comp], "o-", label="control |0>",
                markersize=4, color="tab:blue")
        ax.plot(total_durations, results[1][comp], "s-", label="control |1>",
                markersize=4, color="tab:red")
        ax.set_ylabel(f"<{comp}> target")
        ax.set_ylim(-1.1, 1.1)
        ax.axhline(0, color="k", lw=0.5, alpha=0.3)
        ax.grid(alpha=0.3)
    R_mag = np.sqrt(
        (np.array(results[0]["X"]) + np.array(results[1]["X"]))**2 +
        (np.array(results[0]["Y"]) + np.array(results[1]["Y"]))**2 +
        (np.array(results[0]["Z"]) + np.array(results[1]["Z"]))**2
    )
    axes[3].plot(total_durations, R_mag, "o-", label="|R|",
                markersize=4, color="tab:green")
    axes[0].legend(loc="upper right")
    axes[-1].set_xlabel("Total CR pulse duration (ns)")
    axes[0].set_title(f"CR Rabi on target, amp = {AMP_MHZ} MHz")
    plt.tight_layout()
    plt.savefig("cr_duration_sweep.png", dpi=120)
    plt.show()
    print("Saved cr_duration_sweep.png")


def echoed_cr_duration_sweep() -> None:
    """Echoed CR Rabi: CR(+amp) -- X_pi on control -- CR(-amp) -- X_pi on control.
    Removes the IX, IZ, ZI, ZZ terms that the bare CR leaves behind, leaving
    (ideally) just ZX. The two control-state oscillations should now have the
    same frequency and opposite phase."""
    import matplotlib.pyplot as plt

    sim = build_c1t2_demo()
    channels = list(sim.drive_lines)

    # ----- sweep parameters -----
    AMP_MHZ      = 18.0          # same as the bare sweep, for comparison
    T_RISE_NS    = 16.0
    SIGMA_NS     = 5.0
    FLAT_HALF_NS = np.arange(20, 2004, 40)   # flat-top widths of EACH HALF

    # ----- X_pi pulse on the control (self-drive) -----
    # flat_pulse_for_rotation produces a flat pulse with the right area for a
    # pi rotation on the {0,1} subspace. No DRAG -- expect some leakage error.
    X_PI_DURATION_NS = 200.0
    x_pi_ctrl = flat_pulse_for_rotation(np.pi, duration_ns=X_PI_DURATION_NS)

    # ----- target single-qubit Pauli operators (same as before) -----
    n0, n1 = sim.dims
    I0 = qt.qeye(n0)
    sx_2 = qt.Qobj(np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex))
    sy_2 = qt.Qobj(np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex))
    sz_2 = qt.Qobj(np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex))
    X_op = qt.tensor(I0, sx_2)
    Y_op = qt.tensor(I0, sy_2)
    Z_op = qt.tensor(I0, sz_2)

    # ----- sweep -----
    psi00 = qt.basis(sim.dims, [0, 0])
    psi10 = qt.basis(sim.dims, [1, 0])
    results = {0: {"X": [], "Y": [], "Z": []},
               1: {"X": [], "Y": [], "Z": []}}

    for t_flat_half in FLAT_HALF_NS:
        tl = Timeline(channels)

        # First half: CR with +amp
        cr_plus = gaussian_flat_top(amp=+AMP_MHZ, t_rise_ns=T_RISE_NS,
                                    t_flat_ns=float(t_flat_half),
                                    sigma_ns=SIGMA_NS)
        t = tl.add("cr_drive", start_ns=0.0, waveform=cr_plus)

        # X_pi on control
        t = tl.add("q1_drive", start_ns=t, waveform=x_pi_ctrl)

        # Second half: CR with -amp
        cr_minus = gaussian_flat_top(amp=-AMP_MHZ, t_rise_ns=T_RISE_NS,
                                     t_flat_ns=float(t_flat_half),
                                     sigma_ns=SIGMA_NS)
        t = tl.add("cr_drive", start_ns=t, waveform=cr_minus)

        # Final X_pi on control (restores control state)
        tl.add("q1_drive", start_ns=t, waveform=x_pi_ctrl)

        timeline = tl.finalize()

        for ctrl_state, psi0 in [(0, psi00), (1, psi10)]:
            psi = sim.run_shot(timeline, psi0=psi0)
            results[ctrl_state]["X"].append(qt.expect(X_op, psi))
            results[ctrl_state]["Y"].append(qt.expect(Y_op, psi))
            results[ctrl_state]["Z"].append(qt.expect(Z_op, psi))
        print(f"  flat_half = {t_flat_half:4d} ns  done")

    #building |R|
    R_mag = np.sqrt(
        (np.array(results[0]["X"]) + np.array(results[1]["X"]))**2 +
        (np.array(results[0]["Y"]) + np.array(results[1]["Y"]))**2 +
        (np.array(results[0]["Z"]) + np.array(results[1]["Z"]))**2
    )

    # ----- plot -----
    # Total gate time per shot = 2*(2*t_rise + t_flat_half) + 2*X_PI_DURATION
    total_durations = 2 * (FLAT_HALF_NS + 2 * T_RISE_NS) + 2 * X_PI_DURATION_NS

    fig, axes = plt.subplots(4, 1, figsize=(8, 7), sharex=True)
    for ax, comp in zip(axes, ["X", "Y", "Z"]):
        ax.plot(total_durations, results[0][comp], "o-", label="control |0>",
                markersize=4, color="tab:blue")
        ax.plot(total_durations, results[1][comp], "s-", label="control |1>",
                markersize=4, color="tab:red")
        ax.set_ylabel(f"<{comp}> target")
        ax.set_ylim(-1.1, 1.1)
        ax.axhline(0, color="k", lw=0.5, alpha=0.3)
        ax.grid(alpha=0.3)
    axes[3].plot(total_durations, R_mag, "o-", label="|R|",
                markersize=4, color="tab:green")
    axes[0].legend(loc="upper right")
    axes[-1].set_xlabel("Total echoed CR gate duration (ns)")
    axes[0].set_title(f"Echoed CR Rabi on target, amp = {AMP_MHZ} MHz")
    plt.tight_layout()
    plt.savefig(f"echoed_cr_duration_sweep_low_amp_x_pi_duration_{X_PI_DURATION_NS}ns.png", dpi=120)
    plt.show()
    print(f"Saved echoed_cr_duration_sweep_low_amp_x_pi_duration_{X_PI_DURATION_NS}ns.png")


if __name__ == "__main__":
    # main()
    # cr_duration_sweep()
    echoed_cr_duration_sweep()
