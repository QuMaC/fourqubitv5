import os
import json
from concurrent.futures import ThreadPoolExecutor

import scipy.linalg as sla
from HM.simulator.two_qubit_simulator.engine.pulses import (
    calibrate_f_rabi_per_opx1,
    cr_rise_fall_flat_top,
    drag_grft_envelope_mhz,
)
from Configuration_Files.config_dictionaries import *
from HM.simulator.two_qubit_simulator.engine.pulses import Timeline
from HM.simulator.two_qubit_simulator.base_classes.device_base import TwoQubitSimulatorBase
from Helper_Functions.CR_fitters import  CR_Hamiltonian_tomography, bloch_functions
import qutip as qt
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

# All shared plotting (Bloch spheres, colour conventions, trajectory figures)
# now lives in plotting.py. Imported names are re-aliased to their historical
# underscore-prefixed spellings so existing importers keep working.
from HM.simulator.two_qubit_simulator.experiments import plotting
from HM.simulator.two_qubit_simulator.experiments.plotting import (
    CTRL_COLORS,
    CTRL_LABELS,
    MEDIA_DIR,
    _media_path,
    bloch_trajectory_arrays,
    draw_bloch_sphere,
    plot_bloch_path,
)

_CTRL_COLORS = CTRL_COLORS
_CTRL_LABELS = CTRL_LABELS
_draw_bloch_sphere = draw_bloch_sphere
_plot_bloch_path = plot_bloch_path

# Computational-subspace indices |00>,|01>,|10>,|11> in the qutrit tensor product.
_COMP_INDICES = [0, 1, 3, 4]
_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_PAULI4 = {
    "ZX": np.kron(_Z, _X), "IX": np.kron(_I2, _X),
    "ZY": np.kron(_Z, _Y), "IY": np.kron(_I2, _Y),
    "ZZ": np.kron(_Z, _Z), "IZ": np.kron(_I2, _Z),
}


def pauli_on_levels(which, n):
    """Single-qubit X/Y/Z acting on the {|0>,|1>} subspace of an n-level qudit.

    Works for any n >= 2 (entries on the |2>+ levels stay zero), so the same
    observables are valid whether the engine runs 2-level qubits or qutrits.
    """
    M = np.zeros((n, n), dtype=complex)
    if which == "X":
        M[0, 1] = M[1, 0] = 1.0
    elif which == "Y":
        M[0, 1], M[1, 0] = -1j, 1j
    elif which == "Z":
        M[0, 0], M[1, 1] = 1.0, -1.0
    else:
        raise ValueError(f"unknown pauli {which!r}; expected 'X', 'Y' or 'Z'")
    return qt.Qobj(M)


class CR_len_sweep(TwoQubitSimulatorBase):
    def __init__(self, qubit_pair = [1,2], len_list = None, **kwargs):
        # 1 ns keeps the calibrated d_X180 arbitrary waveform on its native grid.
        kwargs.setdefault("dt_sample_ns", 1)
        # With 1 ns samples, n_sub=2 keeps the same 0.5 ns substep used by the
        # original 4 ns/8-substep engine while avoiding unnecessary work.
        kwargs.setdefault("n_sub", 2)
        super().__init__(qubit_pair=qubit_pair, **kwargs)
        self.len_list = len_list
        self.parallel = bool(kwargs.get("parallel", True))
        self.max_workers = kwargs.get("max_workers", None)
        self.verbose = bool(kwargs.get("verbose", False))
        os.makedirs(MEDIA_DIR, exist_ok=True)
        self.plot_filename = _media_path(kwargs.get("plot_filename", "cr_len_sweep_fit.png"))
        self.bloch_trace_filename = _media_path(
            kwargs.get("bloch_trace_filename", "cr_len_sweep_bloch_trace.json")
        )
        self.save_bloch_trajectory = bool(kwargs.get("save_bloch_trajectory", False))
        self.bloch_trajectory_gif_filename = _media_path(
            kwargs.get("bloch_trajectory_gif_filename", "cr_len_sweep_bloch_trajectory.gif")
        )
        self.bloch_trajectory_png_filename = _media_path(
            kwargs.get("bloch_trajectory_png_filename", "cr_len_sweep_bloch_trajectory.png")
        )
        self.bloch_gif_fps = int(kwargs.get("bloch_gif_fps", 12))
        self.bloch_view_elev = float(kwargs.get("bloch_view_elev", 22))
        self.bloch_view_azim = float(kwargs.get("bloch_view_azim", -58))
        # How to pick the |R| minimum used for gate-duration extraction:
        #   "global"         – deepest point over the full sweep (default)
        #   "deepest_local"  – lowest among sampled local minima
        #   "leftmost_local" – first sampled local minimum (legacy behaviour)
        self.min_selection = str(kwargs.get("min_selection", "global"))
        # Only search for |R| minima at or before this total pulse duration (ns).
        self.min_max_duration_ns = float(kwargs.get("min_max_duration_ns", 1000.0))
        _default_cr_pulse_params = {
            "amp_mhz": 65.0,
            "t_rise_ns": int(cr_tail_ns),
            "t_flat_ns": None,
            "phase_rad": 0.0,
        }
        self.cr_pulse_params = kwargs.get("cr_pulse_params", _default_cr_pulse_params)
        # CR drive phase (rad). Priority: explicit phase_rad kwarg >
        # cr_pulse_params["phase_rad"] > 0. Stored in cr_pulse_params, which is
        # the single source of truth used by _build_timeline and the JSON dump.
        if "phase_rad" in kwargs:
            self.cr_pulse_params["phase_rad"] = float(kwargs["phase_rad"])

        self.echo_qubit = int(kwargs.get("echo_qubit", self.q_pair[0]))
        if self.echo_qubit == self.q_pair[0]:
            self.echo_channel = "q1_drive"
        elif self.echo_qubit == self.q_pair[1]:
            self.echo_channel = "q2_drive"
        else:
            raise ValueError(f"echo_qubit {self.echo_qubit} is not in pair {self.q_pair}")

        q = str(self.echo_qubit)
        _default_x_pi_pulse_params = {
            "amp_scale_x180": float(amp_scale[q]["X180"]),
            "length_ns": int(pi_len_ns[q]),
            "rise_ns": int(pi_rise_grft_ns),
            "alpha": float(drag_dict[q]["alpha"]),
            "det": float(drag_dict[q]["det"]),
            "anharm_hz": float(anharmonicities[q]) * 1e6,
        }
        self.x_pi_pulse_params = {
            **_default_x_pi_pulse_params,
            **kwargs.get("x_pi_pulse_params", {}),
        }
        override = kwargs.get("f_rabi_per_opx1", None)
        self.f_rabi_overridden = override is not None
        self.f_rabi_per_opx1 = (
            float(override) if self.f_rabi_overridden else self._calibrate_x_pi_amp_to_mhz()
        )

    def _calibrate_x_pi_amp_to_mhz(self):
        """MHz Rabi rate per OPX waveform sample, fixed by the X180 calibration."""
        p = self.x_pi_pulse_params
        return calibrate_f_rabi_per_opx1(
            p["amp_scale_x180"], p["length_ns"], p["rise_ns"]
        )

    def build_x_pi(self):
        """Calibrated complex d_X180 envelope (MHz) for the echo qubit."""
        p = self.x_pi_pulse_params
        return drag_grft_envelope_mhz(
            amplitude=p["amp_scale_x180"],
            length_ns=p["length_ns"],
            rise_ns=p["rise_ns"],
            anharm_hz=p["anharm_hz"],
            alpha=p["alpha"],
            detuning=p["det"],
            f_rabi_per_opx1=self.f_rabi_per_opx1,
        )

    @staticmethod
    def _to_jsonable(value):
        if isinstance(value, dict):
            return {str(k): CR_len_sweep._to_jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [CR_len_sweep._to_jsonable(v) for v in value]
        if isinstance(value, np.ndarray):
            return CR_len_sweep._to_jsonable(value.tolist())
        if isinstance(value, np.generic):
            return value.item()
        return value

    @staticmethod
    def _select_minimum(tlist, r_mag, mode="global", max_duration_ns=None):
        t = np.asarray(tlist, dtype=float)
        r = np.asarray(r_mag, dtype=float)
        if t.size == 0:
            raise ValueError("cannot find |R| minimum from an empty sweep")

        search_idx = np.arange(t.size)
        if max_duration_ns is not None:
            mask = t <= float(max_duration_ns)
            if not np.any(mask):
                raise ValueError(
                    f"no sweep points with total duration <= {max_duration_ns} ns"
                )
            search_idx = np.where(mask)[0]

        ts = t[search_idx]
        rs = r[search_idx]

        mode = str(mode)
        if mode == "global":
            local_idx = int(np.argmin(rs))
            selection = "global_minimum"
        elif mode == "leftmost_local":
            if ts.size < 3:
                local_idx = int(np.argmin(rs))
            else:
                local_minima = np.where((rs[1:-1] <= rs[:-2]) & (rs[1:-1] <= rs[2:]))[0] + 1
                local_idx = int(local_minima[0]) if local_minima.size else int(np.argmin(rs))
            selection = "leftmost_sampled_local_minimum"
        elif mode == "deepest_local":
            if ts.size < 3:
                local_idx = int(np.argmin(rs))
            else:
                local_minima = np.where((rs[1:-1] <= rs[:-2]) & (rs[1:-1] <= rs[2:]))[0] + 1
                local_idx = (
                    int(local_minima[np.argmin(rs[local_minima])])
                    if local_minima.size
                    else int(np.argmin(rs))
                )
            selection = "deepest_sampled_local_minimum"
        else:
            raise ValueError(
                f"unknown min_selection {mode!r}; expected 'global', "
                "'deepest_local', or 'leftmost_local'"
            )

        idx = int(search_idx[local_idx])
        result = {
            "index": idx,
            "duration_ns": float(t[idx]),
            "r_mag": float(r[idx]),
            "selection": selection,
        }
        if max_duration_ns is not None:
            result["max_duration_ns"] = float(max_duration_ns)
        return result

    def _flat_len_at_minimum(self, duration_info, total_duration_ns):
        """Sweep `length` passed to _build_timeline for the |R| minimum point."""
        idx = int(duration_info["index"])
        if self.len_list is not None and 0 <= idx < len(self.len_list):
            return float(self.len_list[idx])
        if self.echoed_cr:
            x_pi_len = self.x_pi_pulse_params["length_ns"]
            return (float(total_duration_ns) - 4 * self.cr_pulse_params["t_rise_ns"] - 2 * x_pi_len) / 2
        return float(total_duration_ns) - 2 * self.cr_pulse_params["t_rise_ns"]

    def _propagator_from_timeline(self, timeline):
        """Assemble the joint Hilbert-space propagator by evolving each basis ket."""
        sim = self.simulator
        run_U = getattr(sim, "run_propagator", None)
        if callable(run_U):
            return run_U(timeline)
        n0, n1 = sim.dims
        dim = n0 * n1
        U = np.zeros((dim, dim), dtype=complex)
        for c in range(n0):
            for t in range(n1):
                col = c * n1 + t
                psi0 = qt.basis(sim.dims, [c, t])
                psi = sim.run_shot(timeline, psi0=psi0)
                U[:, col] = psi.full().flatten()
        return U

    @staticmethod
    def _generators_from_unitary(U_full, T_total_ns, comp_indices=_COMP_INDICES):
        """Matrix-log extraction of (ZX, IX, ZY, IY, ZZ, IZ) in MHz.

        Same convention as HM/Thesis/grape/validate_simulator.py: returns MHz.
        Bloch-fit path uses int_strength * 1e3 for the same MHz scale.

        comp_indices selects the |00>,|01>,|10>,|11> rows/cols out of the full
        Hilbert space; pass the engine's comp_idx so it is correct for any
        n_levels (defaults to the qutrit layout [0,1,3,4]).
        """
        U_comp = U_full[np.ix_(comp_indices, comp_indices)]
        Up, _ = sla.polar(U_comp)
        T_us = float(T_total_ns) * 1e-3
        H_eff_rad_per_us = 1j * sla.logm(Up) / T_us
        H_eff = 0.5 * (H_eff_rad_per_us + H_eff_rad_per_us.conj().T)
        out = {}
        for lab in ("ZX", "IX", "ZY", "IY", "ZZ", "IZ"):
            c_P = np.trace(_PAULI4[lab] @ H_eff) / 4.0
            omega_P_rad_per_us = 2.0 * c_P
            out[lab] = float(np.real(omega_P_rad_per_us / (2 * np.pi)))
        return out

    def extract_generators_matrix_log(self, flat_len_ns, total_duration_ns):
        """Propagate once at the given flat length; return generators in MHz."""
        x_pi = self.build_x_pi() if self.echoed_cr else None
        timeline = self._build_timeline(float(flat_len_ns), x_pi=x_pi)
        U = self._propagator_from_timeline(timeline)
        return self._generators_from_unitary(U, total_duration_ns, self.simulator.comp_idx)

    def _build_timeline(self, length, x_pi=None):
        tl = Timeline(self.channels, dt_ns=self.dt_sample_ns)
        # Relative CR drive phase: rotates the in-plane (ZX, ZY) / (IX, IY)
        # interaction components. The echo X_pi stays at phase 0.
        phase_rad = float(self.cr_pulse_params.get("phase_rad", 0.0))
        cr_amp = self.cr_pulse_params["amp_mhz"] * np.exp(1j * phase_rad)
        if self.echoed_cr:
            if x_pi is None:
                x_pi = self.build_x_pi()
            cr_plus = cr_rise_fall_flat_top(
                amp=cr_amp,
                t_flat_ns=length,
                t_rise_ns=self.cr_pulse_params["t_rise_ns"],
                dt_ns=self.dt_sample_ns,
            )
            cr_minus = cr_rise_fall_flat_top(
                amp=-cr_amp,
                t_flat_ns=length,
                t_rise_ns=self.cr_pulse_params["t_rise_ns"],
                dt_ns=self.dt_sample_ns,
            )
            t = tl.add("cr_drive", start_ns=0.0, waveform=cr_plus)
            t = tl.add(self.echo_channel, start_ns=t, waveform=x_pi)
            t = tl.add("cr_drive", start_ns=t, waveform=cr_minus)
            tl.add(self.echo_channel, start_ns=t, waveform=x_pi)
        else:
            cr = cr_rise_fall_flat_top(
                amp=cr_amp,
                t_flat_ns=length,
                t_rise_ns=self.cr_pulse_params["t_rise_ns"],
                dt_ns=self.dt_sample_ns,
            )
            tl.add("cr_drive", start_ns=0.0, waveform=cr)
        return tl.finalize()

    def _build_timeline_from_cr_half(self, cr_plus, x_pi=None):
        """Echoed CR from one optimized CR-half envelope (+u → Xπ → −u → Xπ)."""
        if not self.echoed_cr:
            raise ValueError("_build_timeline_from_cr_half requires echoed_cr=True")
        cr_plus = np.asarray(cr_plus, dtype=complex)
        cr_minus = -cr_plus
        if x_pi is None:
            x_pi = self.build_x_pi()
        tl = Timeline(self.channels, dt_ns=self.dt_sample_ns)
        t = tl.add("cr_drive", start_ns=0.0, waveform=cr_plus)
        t = tl.add(self.echo_channel, start_ns=t, waveform=x_pi)
        t = tl.add("cr_drive", start_ns=t, waveform=cr_minus)
        tl.add(self.echo_channel, start_ns=t, waveform=x_pi)
        return tl.finalize()

    def run_simulation(self, len_list = None, phase_rad = None):
        if len_list is not None:
            self.len_list = np.asarray(len_list, dtype=float)
        elif self.len_list is not None:
            self.len_list = np.asarray(self.len_list, dtype=float)
        else:
            raise ValueError("len_list must be provided")
        if phase_rad is not None:
            self.cr_pulse_params["phase_rad"] = float(phase_rad)

        #defining operators in the 2 qubit space
        print("J:", self.simulator.J_MHz)
        print("Detuning:", self.simulator.delta_qq_MHz)
        print("Drive lines:", list(self.simulator.drive_lines.keys()))
        print(f"dt_sample_ns: {self.dt_sample_ns:g}, n_sub: {self.simulator.n_sub}")
        print(f"CR phase: {self.cr_pulse_params['phase_rad']:.4f} rad")
        n0, n1 = self.simulator.dims
        I0 = qt.qeye(n0)
        # Target-qubit Pauli X/Y/Z on its {|0>,|1>} subspace (any n_levels).
        X_op = qt.tensor(I0, pauli_on_levels("X", n1))
        Y_op = qt.tensor(I0, pauli_on_levels("Y", n1))
        Z_op = qt.tensor(I0, pauli_on_levels("Z", n1))
        psi00 = qt.basis(self.simulator.dims, [0, 0])
        psi10 = qt.basis(self.simulator.dims, [1, 0])
        x_pi = self.build_x_pi() if self.echoed_cr else None

        self.results = {
                   0: {"X": [], "Y": [], "Z": []},
                   1: {"X": [], "Y": [], "Z": []},
                   "R_mag": []}

        def simulate_length(length):
            timeline = self._build_timeline(float(length), x_pi=x_pi)
            if self.verbose:
                print(f"CR timeline: {np.max(np.abs(timeline['cr_drive']))} MHz peak")
                print(f"CR samples nonzero: {np.sum(np.abs(timeline['cr_drive']) > 0)}")
            point = {}
            for ctrl_state, psi0 in [(0, psi00), (1, psi10)]:
                psi = self.simulator.run_shot(timeline, psi0=psi0)
                point[ctrl_state] = {
                    "X": qt.expect(X_op, psi),
                    "Y": qt.expect(Y_op, psi),
                    "Z": qt.expect(Z_op, psi),
                }
            return point

        max_workers = self.max_workers
        if max_workers is None:
            max_workers = min(len(self.len_list), os.cpu_count() or 1)
        max_workers = max(1, int(max_workers))

        if self.parallel and max_workers > 1:
            print(f"Running length sweep in parallel with {max_workers} workers")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                sweep_points = list(tqdm(
                    executor.map(simulate_length, self.len_list),
                    total=len(self.len_list),
                    desc="Length Sweep",
                ))
        else:
            sweep_points = [
                simulate_length(length)
                for length in tqdm(self.len_list, desc="Length Sweep")
            ]

        for point in sweep_points:
            for ctrl_state in [0, 1]:
                self.results[ctrl_state]["X"].append(point[ctrl_state]["X"])
                self.results[ctrl_state]["Y"].append(point[ctrl_state]["Y"])
                self.results[ctrl_state]["Z"].append(point[ctrl_state]["Z"])

        self.results["R_mag"] = np.sqrt(
            (np.array(self.results[0]["X"]) + np.array(self.results[1]["X"]))**2 +
            (np.array(self.results[0]["Y"]) + np.array(self.results[1]["Y"]))**2 +
            (np.array(self.results[0]["Z"]) + np.array(self.results[1]["Z"]))**2
        )
        if self.echoed_cr:
            x_pi_len = self.x_pi_pulse_params["length_ns"]
            self.results["total_durations"] = (
                2 * (2 * self.cr_pulse_params["t_rise_ns"] + self.len_list) + 2 * x_pi_len
            )
        else:
            self.results["total_durations"] = 2 * self.cr_pulse_params["t_rise_ns"] + self.len_list
        return self.results

    def analyze_and_plot(self, results_input = None):
        # analysis where we try to extract propagators, find the cr gate duration and the error
        #1 starting with bloch model fit (like in sheldons paper)
        results = self.results if results_input is None else results_input

        x_vals = [np.array(results[0]["X"]), np.array(results[1]["X"])]
        y_vals = [np.array(results[0]["Y"]), np.array(results[1]["Y"])]
        z_vals = [np.array(results[0]["Z"]), np.array(results[1]["Z"])]
        exp_vals = [z_vals, y_vals, x_vals]
        tlist = np.asarray(results["total_durations"], dtype=float)
        r_mag = np.asarray(results["R_mag"], dtype=float)
        duration_info = self._select_minimum(
            tlist,
            r_mag,
            mode=self.min_selection,
            max_duration_ns=self.min_max_duration_ns,
        )
        min_duration_ns = duration_info["duration_ns"]
        min_r_mag = duration_info["r_mag"]
        min_label = duration_info["selection"].replace("_", " ")

        int_strengths, [C0, C1] = CR_Hamiltonian_tomography(exp_vals, tlist, bloch_params=True)
        # Same scaling as hardware CR-HT scripts: int_strengths * 1e3 -> MHz
        # (CrossResonance_HT-WithAC_auto_time.py prints these as MHz, not kHz).
        int_strengths_mhz = [s * 1e3 for s in int_strengths]

        # C1_guess = [-C0[0], C0[1], C0[2], C0[3]]
        # int_strengths, [C0, C1] = CR_Hamiltonian_tomography(exp_vals, tlist_us, bloch_params=True, init_vals=[C0, C1_guess])

        ZX, IX, ZY, IY, ZZ, IZ = int_strengths_mhz
        print(f"Bloch-fit generators (full sweep) [MHz]:")
        print(f"  ZX: {ZX:.4f}, IX: {IX:.4f}, ZY: {ZY:.4f}, "
              f"IY: {IY:.4f}, ZZ: {ZZ:.4f}, IZ: {IZ:.4f}")
        print(f"C0: {C0}, C1: {C1}")
        print(f"|R| minimum search window: t <= {self.min_max_duration_ns:.1f} ns")
        print(f"|R| minimum index ({min_label}): {duration_info['index']}")
        print(f"|R| minimum duration ({min_label}): {min_duration_ns:.3f} ns ({min_duration_ns * 1e-3:.6f} us)")
        print(f"|R| minimum value ({min_label}): {min_r_mag:.6f}")
        if self.echoed_cr:
            x_pi_len = self.x_pi_pulse_params["length_ns"]
            cr_flat_ns = (min_duration_ns - 4 * self.cr_pulse_params["t_rise_ns"] - 2 * x_pi_len) / 2
            cr_total_ns = 2 * (2 * self.cr_pulse_params["t_rise_ns"] + cr_flat_ns)
            duration_info["cr_flat_top_each_half_ns"] = float(cr_flat_ns)
            duration_info["cr_total_without_echo_x_pi_ns"] = float(cr_total_ns)
            duration_info["x_pi_total_ns"] = float(2 * x_pi_len)
            print(f"CR flat-top duration at minimum, each half: {cr_flat_ns:.3f} ns")
            print(f"Total CR-only duration at minimum: {cr_total_ns:.3f} ns")
            print(f"Total echoed sequence duration at minimum: {min_duration_ns:.3f} ns")
        else:
            cr_flat_ns = min_duration_ns - 2 * self.cr_pulse_params["t_rise_ns"]
            duration_info["cr_flat_top_ns"] = float(cr_flat_ns)
            print(f"CR flat-top duration at minimum: {cr_flat_ns:.3f} ns")
            print(f"Total CR pulse duration at minimum: {min_duration_ns:.3f} ns")
        self.duration_info = duration_info

        flat_len_min = self._flat_len_at_minimum(duration_info, min_duration_ns)
        matrix_gens_mhz = self.extract_generators_matrix_log(flat_len_min, min_duration_ns)
        self.matrix_generators_mhz = matrix_gens_mhz
        duration_info["flat_len_ns"] = float(flat_len_min)
        duration_info["matrix_log_generators_mhz"] = matrix_gens_mhz
        print(f"\nMatrix-log generators at |R| minimum (T = {min_duration_ns:.1f} ns, "
              f"flat_len = {flat_len_min:.1f} ns) [MHz]:")
        print(f"  ZX: {matrix_gens_mhz['ZX']:.4f}, IX: {matrix_gens_mhz['IX']:.4f}, "
              f"ZY: {matrix_gens_mhz['ZY']:.4f}, IY: {matrix_gens_mhz['IY']:.4f}, "
              f"ZZ: {matrix_gens_mhz['ZZ']:.4f}, IZ: {matrix_gens_mhz['IZ']:.4f}")


        ### Plotting
        # t_dense_us = np.linspace(tlist_us[0], tlist_us[-1], 1000)
        t_dense_ns = np.linspace(tlist[0], tlist[-1], 1000)
        fit_0 = bloch_functions(t_dense_ns, *C0)
        fit_1 = bloch_functions(t_dense_ns, *C1)
        fig, axes = plt.subplots(4,1, figsize =(8,7), sharex=True)
        labels = ["X", "Y", "Z", ]
        fit_indices = [2,1,0]
        for ax, comp, fi, in zip(axes, labels, fit_indices):
            ax.plot(tlist, results[0][comp], "o", label="Control 0 sim", color = "tab:blue")
            ax.plot(tlist, results[1][comp], "s", label="Control 1 sim", color = "tab:red")
            ax.plot(t_dense_ns, fit_0[fi], label="Control 0 fit", color = "tab:blue", linewidth = 2.0, alpha = 0.6)
            ax.plot(t_dense_ns, fit_1[fi], label="Control 1 fit", color = "tab:red", linewidth = 2.0, alpha = 0.6)
            ax.axvline(min_duration_ns, color="tab:purple", ls="--", lw=1.2, alpha=0.85)
            ax.set_ylabel(f"<{comp}> target")
            ax.set_ylim(-1.1, 1.1)
            ax.axhline(0, color="k", lw=0.5, alpha=0.3)
            ax.set_yticks(np.arange(-1.0, 1.01, 0.5))
            ax.yaxis.set_major_formatter(FormatStrFormatter("%.2g"))
            ax.grid(which="major", alpha=0.4)
        axes[-1].plot(tlist, results["R_mag"], "o", label="|R|", color = "tab:green")
        axes[-1].plot(
            min_duration_ns,
            min_r_mag,
            "o",
            color="tab:purple",
            ms=7,
            label=f"min |R| = {min_r_mag:.4f}",
        )
        axes[-1].axvline(
            min_duration_ns,
            color="tab:purple",
            ls="--",
            lw=1.2,
            alpha=0.85,
            label=f"{min_label} at {min_duration_ns:.1f} ns",
        )
        axes[-1].set_xlabel("Total CR pulse duration (ns)")
        axes[-1].set_ylabel("|R|")
        axes[-1].set_ylim(0.0, 2.0)
        axes[-1].set_yticks(np.arange(0.0, 2.01, 0.5))
        axes[-1].yaxis.set_major_formatter(FormatStrFormatter("%.2g"))
        axes[-1].grid(which="major", alpha=0.4)
        axes[-1].legend(loc="upper right", fontsize=8)
        axes[0].set_title(f"CR Rabi on target: Bloch vector fit CR_amp = {self.cr_pulse_params['amp_mhz']} MHz")
        plt.tight_layout()
        plt.savefig(self.plot_filename, dpi=160)
        print(f"Saved {self.plot_filename}")

        bloch_trace = {
            "metadata": {
                "q_pair": self.q_pair,
                "echoed_cr": self.echoed_cr,
                "echo_qubit": self.echo_qubit,
                "echo_channel": self.echo_channel,
                "dt_sample_ns": self.dt_sample_ns,
                "n_sub": self.simulator.n_sub,
                "cr_pulse_params": self.cr_pulse_params,
                "x_pi_pulse_params": self.x_pi_pulse_params,
                "f_rabi_per_opx1": self.f_rabi_per_opx1,
                "duration_info": duration_info,
                "interaction_strengths_mhz": {
                    "ZX": ZX,
                    "IX": IX,
                    "ZY": ZY,
                    "IY": IY,
                    "ZZ": ZZ,
                    "IZ": IZ,
                },
                "interaction_strengths_matrix_log_mhz": matrix_gens_mhz,
                "bloch_fit_params": {
                    "control_0": C0,
                    "control_1": C1,
                },
            },
            "raw": {
                "sweep_lengths_ns": self.len_list,
                "total_durations_ns": tlist,
                "control_0": {
                    "X": results[0]["X"],
                    "Y": results[0]["Y"],
                    "Z": results[0]["Z"],
                },
                "control_1": {
                    "X": results[1]["X"],
                    "Y": results[1]["Y"],
                    "Z": results[1]["Z"],
                },
                "R_mag": results["R_mag"],
            },
            "fit": {
                "total_durations_ns": t_dense_ns,
                "control_0": {
                    "X": fit_0[2],
                    "Y": fit_0[1],
                    "Z": fit_0[0],
                },
                "control_1": {
                    "X": fit_1[2],
                    "Y": fit_1[1],
                    "Z": fit_1[0],
                },
            },
        }
        with open(self.bloch_trace_filename, "w") as f:
            json.dump(self._to_jsonable(bloch_trace), f, indent=2)
        print(f"Saved {self.bloch_trace_filename}")

        if self.save_bloch_trajectory:
            self.save_bloch_trajectory_plots(results, tlist)

        plt.show()

        return int_strengths, [C0, C1]

    def _bloch_trajectory_arrays(self, results):
        """Target-qubit Bloch components (X, Y, Z) for each control state."""
        return bloch_trajectory_arrays(results)

    def save_bloch_trajectory_png(self, results=None, tlist=None, filename=None):
        """Save a 2x1 PNG of the full net Bloch trajectories (ctrl off | ctrl on)."""
        results = self.results if results is None else results
        if tlist is None:
            tlist = np.asarray(results["total_durations"], dtype=float)
        filename = self.bloch_trajectory_png_filename if filename is None else filename
        return plotting.save_bloch_trajectory_png(
            bloch_trajectory_arrays(results),
            tlist,
            filename,
            elev=self.bloch_view_elev,
            azim=self.bloch_view_azim,
        )

    def save_bloch_trajectory_gif(self, results=None, tlist=None, filename=None, fps=None):
        """Save a 2x1 GIF animating the traversed Bloch paths (ctrl off | ctrl on)."""
        results = self.results if results is None else results
        if tlist is None:
            tlist = np.asarray(results["total_durations"], dtype=float)
        filename = self.bloch_trajectory_gif_filename if filename is None else filename
        fps = self.bloch_gif_fps if fps is None else int(fps)
        return plotting.save_bloch_trajectory_gif(
            bloch_trajectory_arrays(results),
            tlist,
            filename,
            fps=fps,
            elev=self.bloch_view_elev,
            azim=self.bloch_view_azim,
        )

    def save_bloch_trajectory_plots(self, results=None, tlist=None):
        """Save both the static PNG and animated GIF of Bloch trajectories."""
        results = self.results if results is None else results
        if tlist is None:
            tlist = np.asarray(results["total_durations"], dtype=float)
        self.save_bloch_trajectory_png(results=results, tlist=tlist)
        self.save_bloch_trajectory_gif(results=results, tlist=tlist)


    def bloch_evolve(self, method="rotation"):
        """
        Evolve the state using the Bloch model.
        
        Args:
            method (str): The method to use for Bloch evolution. 
                Available options: "rotation" and "matrix". Default is "rotation".

        Matrix makes a 3x3 matrix using scipy.linalg.expm (slower)
        Rotation uses the closed form Rodriguez formula (faster)
        
                """
        # TODO: implement evolution according to the given method
        if method == "matrix":
            pass
        elif method == "rotation":
            pass

        #evolve the state using the bloch model
        return None


    def run(self):
        self.run_simulation()
        self.analyze_and_plot()
        return self.results





def perform_cr_len_sweep(q_pair = [1,2], len_list = None, **kwargs):
    exp = CR_len_sweep(qubit_pair=q_pair, len_list=len_list, **kwargs)
    exp.run()
    return exp

if __name__ == "__main__":
    cr_pulse_params = {
        "amp_mhz": 21,
        "t_rise_ns": int(16),
        "t_flat_ns": None,
        # "phase_rad": np.round(np.pi/4, 4),
        "phase_rad": 0
        # "phase_rad": 0
    }
    print(cr_pulse_params)
    n_levels = 3
    file_suffix = f"recreate_amp_{cr_pulse_params['amp_mhz']}_t_rise_{cr_pulse_params['t_rise_ns']}_ph_{cr_pulse_params['phase_rad']}_n_levels_{n_levels}"
    exp = perform_cr_len_sweep( 
                                q_pair = [1,2],
                                len_list = np.arange(100, 130, 1),
                                cr_pulse_params=cr_pulse_params,
                                echoed_cr = True,
                                parallel = True,
                                max_workers=4,
                                n_sub=4,
                                n_levels = n_levels,
                                save_bloch_trajectory=True,
                                bloch_trajectory_gif_filename=f"cr_len_sweep_bloch_trajectory_{file_suffix}.gif",
                                bloch_trajectory_png_filename=f"cr_len_sweep_bloch_trajectory_{file_suffix}.png",
                                plot_filename=f"cr_len_sweep_fit_{file_suffix}.png",
                                bloch_view_elev=22,
                                bloch_view_azim=-10, # rotate around Z (try -80, -30, 0, 30, …)
                                )

