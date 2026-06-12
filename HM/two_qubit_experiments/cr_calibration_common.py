import logging
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
from qualang_tools.plot import interrupt_on_close
from qualang_tools.results import fetching_tool, progress_counter

from Helper_Functions.CR_fitters import CR_Hamiltonian_tomography, bloch_functions, fit_cos, normalize_data, rabi_fit
from Helper_Functions.helper_functionsv2 import S2N
from Helper_Functions.qua_program_funcs import HT_setPhase_local_phase

logger = logging.getLogger(__name__)

INT_STRENGTH_LABELS = ["ZX", "IX", "ZY", "IY", "ZZ", "IZ"]


def wrap_phase_unit_cycle(phase):
    phase = float(phase)
    while phase > 1:
        phase -= 2
    while phase < -1:
        phase += 2
    return phase


def round_to_multiple(value, step):
    value = float(value)
    step = float(step)
    off = value % step
    if off <= step / 2:
        return value - off
    return value - off + step


def init_cr_live_plot(t_list_ns, job, title, show_plot=True):
    plt.ion()
    plt.rcParams["figure.figsize"] = (15, 10)
    fig, ax = plt.subplots(3, 3, sharex=True, sharey="row")
    interrupt_on_close(fig, job)
    fig.suptitle(title, fontsize=15)
    axbig = fig.add_subplot(111, frameon=False)
    axbig.set_xlabel("Time (us)", labelpad=20, fontsize=15)
    axbig.set_ylabel("Amplitude", labelpad=50, fontsize=15)
    axbig.set_xticks([])
    axbig.set_yticks([])

    lines = []
    control_labels = ["Control 0", "Control 1"]
    target_labels = ["Z", "Y", "X"]
    for i in range(2):
        for j in range(3):
            lines.append(
                ax[i, j].plot(
                    1e-3 * t_list_ns,
                    1e-4 * np.random.rand(len(t_list_ns)),
                    marker=".",
                    label="I",
                )[0]
            )
            lines.append(ax[i, j].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label="Q")[0])
            ax[i, j].set_title(control_labels[i] + " Target: " + target_labels[j])
            ax[i, j].grid()
            ax[i, j].legend(loc="upper right")

    for i in range(2):
        lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label="I")[0])
        lines.append(ax[2, i].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label="Q")[0])
        ax[2, i].set_title(f"Control {i}")
        ax[2, i].grid()
        ax[2, i].legend(loc="upper right")

    lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label="I")[0])
    lines.append(ax[2, 2].plot(1e-3 * t_list_ns, [0] * len(t_list_ns), marker=".", label="Q")[0])
    ax[2, 2].set_title("Target Rabi")
    ax[2, 2].grid()
    ax[2, 2].legend(loc="upper right")
    fig.set_tight_layout(True)
    if show_plot:
        plt.show()
    return {"fig": fig, "ax": ax, "lines": lines}


def update_cr_live_plot(live_plot, t_list_len, I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg):
    if live_plot is None:
        return
    fig = live_plot["fig"]
    ax = live_plot["ax"]
    lines = live_plot["lines"]

    Ic0 = np.average(I_c_avg[:, 0].reshape(t_list_len, 3), axis=1)
    Qc0 = np.average(Q_c_avg[:, 0].reshape(t_list_len, 3), axis=1)
    Ic1 = np.average(I_c_avg[:, 1].reshape(t_list_len, 3), axis=1)
    Qc1 = np.average(Q_c_avg[:, 1].reshape(t_list_len, 3), axis=1)
    lines[12].set_ydata(Ic0)
    lines[13].set_ydata(Qc0)
    lines[14].set_ydata(Ic1)
    lines[15].set_ydata(Qc1)
    lines[16].set_ydata(I_rabi_avg)
    lines[17].set_ydata(Q_rabi_avg)

    for i in range(6):
        lines[2 * i].set_ydata(I_t_avg[:, i])
        lines[2 * i + 1].set_ydata(Q_t_avg[:, i])

    for i in range(3):
        for j in range(3):
            ax[i, j].relim()
            ax[i, j].autoscale_view()
    fig.set_tight_layout(True)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)


def collect_cr_tomography(
    exp,
    qmm,
    phase,
    amplitude,
    echo_p,
    title,
    plot_suffix=None,
):
    job = HT_setPhase_local_phase(
        qmm,
        exp.cr_elem,
        phase,
        exp.t_min,
        exp.t_max,
        exp.dt,
        exp.n_avg,
        exp.wait_init,
        exp.wait_t,
        exp.wait_rr,
        exp.q_control_str,
        exp.q_target_str,
        exp.pi_12,
        exp.simulate,
        echo_p,
        amplitude,
    )

    results = fetching_tool(
        job,
        data_list=["I_t_avg", "Q_t_avg", "I_c_avg", "Q_c_avg", "I_rabi_avg", "Q_rabi_avg", "iteration"],
        mode="live",
    )
    live_plot = None
    if exp.plot_live:
        live_plot = init_cr_live_plot(exp.t_list_ns, job, title, show_plot=exp.show_plot)

    while results.is_processing():
        I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg, iteration = results.fetch_all()
        progress_counter(iteration, exp.n_avg, start_time=results.get_start_time())
        update_cr_live_plot(live_plot, len(exp.t_list), I_t_avg, Q_t_avg, I_c_avg, Q_c_avg, I_rabi_avg, Q_rabi_avg)
        snr_i, _ = S2N(I_rabi_avg)
        if snr_i > exp.snr_halt_threshold:
            job.halt()

    fetched = results.fetch_all()[:6]
    if live_plot is not None:
        update_cr_live_plot(live_plot, len(exp.t_list), *fetched)
        if exp.save_plot and getattr(exp, "save_live_plot", False):
            plot_formats = getattr(exp, "plot_formats", ("png",))
            if isinstance(plot_formats, str):
                plot_formats = (plot_formats,)
            suffix = plot_suffix or "live_tomography"
            for fmt in plot_formats:
                fig_path = str(exp.path_to_save) + f"_{suffix}.{str(fmt).lstrip('.')}"
                live_plot["fig"].savefig(fig_path, bbox_inches="tight")
                exp.results["artifacts"].append(fig_path)
                logger.info("Saved plot: %s", fig_path)
    if live_plot is not None and not exp.show_plot:
        plt.close(live_plot["fig"])
    return fetched


def split_control_traces(control_avg, t_list_len):
    c0 = np.average(control_avg[:, 0].reshape(t_list_len, 3), axis=1)
    c1 = np.average(control_avg[:, 1].reshape(t_list_len, 3), axis=1)
    return c0, c1


def _bloch_fit_values(params, time_ns, affine_output):
    z_fit, y_fit, x_fit = bloch_functions(time_ns, *params[:4])
    if affine_output:
        x_scale, x_offset, y_scale, y_offset, z_scale, z_offset = params[4:]
        x_fit = x_scale * x_fit + x_offset
        y_fit = y_scale * y_fit + y_offset
        z_fit = z_scale * z_fit + z_offset
    return z_fit, y_fit, x_fit


def _robust_affine_guess(*traces):
    guesses = []
    for trace in traces:
        trace = np.asarray(trace, dtype=float)
        lo, hi = np.nanpercentile(trace, [10, 90])
        scale = max(0.5 * abs(float(hi - lo)), 0.1)
        offset = float(np.nanmedian(trace))
        guesses.extend([scale, offset])
    return np.array(guesses, dtype=float)


def _bloch_residual(params, x_vals, y_vals, z_vals, time_ns, initial_state_weight, affine_output):
    z_fit, y_fit, x_fit = _bloch_fit_values(params, time_ns, affine_output)
    residual = [x_fit - x_vals, y_fit - y_vals, z_fit - z_vals]
    if initial_state_weight > 0:
        z0, y0, x0 = bloch_functions(np.array([0.0]), *params[:4])
        residual.append(initial_state_weight * np.array([x0[0], y0[0], z0[0] - 1.0]))
    return np.concatenate(residual)


def _bounded_bloch_fit(
    x_vals,
    y_vals,
    z_vals,
    time_ns,
    init_vals=None,
    max_fit_cycles=None,
    initial_state_weight=0.0,
    affine_output=False,
):
    time_ns = np.asarray(time_ns, dtype=float)
    span_ns = max(float(time_ns[-1] - time_ns[0]), 1.0)
    if max_fit_cycles is None:
        omega_bound = np.inf
        component_bound = np.inf
    else:
        omega_bound = 2 * np.pi * float(max_fit_cycles) / span_ns
        component_bound = omega_bound / np.sqrt(3)

    if init_vals is None:
        # Start with a slow partial-cycle trajectory. Low-amplitude CR traces often
        # contain less than one visible period, so an FFT seed is too aggressive.
        guess_omega = (0.35 * omega_bound) if np.isfinite(omega_bound) else (2 * np.pi / span_ns)
        component_guess = guess_omega / np.sqrt(3)
        init_vals = np.array([component_guess, component_guess, component_guess, 5 * span_ns], dtype=float)
    else:
        init_vals = np.array(init_vals, dtype=float)

    lower = np.array([-component_bound, -component_bound, -component_bound, span_ns / 10], dtype=float)
    upper = np.array([component_bound, component_bound, component_bound, 100 * span_ns], dtype=float)
    if np.isfinite(component_bound):
        init_vals[:3] = np.clip(init_vals[:3], lower[:3] * 0.95, upper[:3] * 0.95)
    init_vals[3] = np.clip(init_vals[3], lower[3] * 1.05, upper[3] * 0.95)

    if affine_output:
        if len(init_vals) == 4:
            init_vals = np.concatenate((init_vals, _robust_affine_guess(x_vals, y_vals, z_vals)))
        data_bound = max(
            float(np.nanmax(np.abs(np.concatenate((x_vals, y_vals, z_vals))))),
            1.0,
        )
        affine_lower = np.array([-5 * data_bound, -5 * data_bound] * 3, dtype=float)
        affine_upper = np.array([5 * data_bound, 5 * data_bound] * 3, dtype=float)
        lower = np.concatenate((lower, affine_lower))
        upper = np.concatenate((upper, affine_upper))
        init_vals[4:] = np.clip(init_vals[4:], lower[4:] * 0.95, upper[4:] * 0.95)

    result = least_squares(
        _bloch_residual,
        init_vals,
        args=(x_vals, y_vals, z_vals, time_ns, initial_state_weight, affine_output),
        bounds=(lower, upper),
        loss="soft_l1",
        f_scale=0.2,
        max_nfev=5000,
    )
    if not result.success:
        logger.warning("Bounded CR Bloch fit did not converge: %s", result.message)
    return result.x


def _bounded_cr_hamiltonian_tomography(
    cdata,
    time_ns,
    init_vals=None,
    max_fit_cycles=None,
    initial_state_weight=0.0,
    affine_output=False,
):
    z_vals, y_vals, x_vals = cdata[0], cdata[1], cdata[2]
    init0 = None if init_vals is None else init_vals[0]
    init1 = None if init_vals is None else init_vals[1]
    fit0 = _bounded_bloch_fit(
        x_vals[0],
        y_vals[0],
        z_vals[0],
        time_ns,
        init0,
        max_fit_cycles,
        initial_state_weight,
        affine_output,
    )
    fit1 = _bounded_bloch_fit(
        x_vals[1],
        y_vals[1],
        z_vals[1],
        time_ns,
        init1,
        max_fit_cycles,
        initial_state_weight,
        affine_output,
    )
    c0 = fit0[:4]
    c1 = fit1[:4]

    int_strengths = []
    for i in range(3):
        int_strengths.append((c0[i] - c1[i]) / (4 * np.pi))
        int_strengths.append((c0[i] + c1[i]) / (4 * np.pi))
    fit_vals0 = _bloch_fit_values(fit0, time_ns, affine_output)
    fit_vals1 = _bloch_fit_values(fit1, time_ns, affine_output)
    return np.array(int_strengths, dtype=float), [c0, c1], [fit_vals0, fit_vals1], [fit0[4:], fit1[4:]]


def analyze_cr_tomography(
    time_ns,
    I_t_avg,
    I_rabi_avg,
    norm_off_pair: Tuple[Optional[float], Optional[float]] = (None, None),
    fit_init_vals=None,
    max_fit_cycles=None,
    initial_state_weight=0.0,
    affine_output=False,
):
    time_ns = np.asarray(time_ns)
    rabi_i = 1e3 * np.asarray(I_rabi_avg)
    norm, off = norm_off_pair
    rabi_fit_params = None
    if norm is None or off is None:
        res_i = fit_cos(time_ns, rabi_i)
        rabi_fit_params = [res_i["amp"], res_i["freq"], 0, res_i["phase"], res_i["offset"]]
        norm, off = rabi_fit_params[0], rabi_fit_params[4]

    target_data = np.asarray(I_t_avg).transpose()
    c0_data = 1e3 * target_data[0:3]
    c1_data = 1e3 * target_data[3:6]
    cdata = normalize_data([[c0_data[i], c1_data[i]] for i in range(3)], off, norm)
    if max_fit_cycles is None:
        int_strengths, ivals = CR_Hamiltonian_tomography(cdata, time_ns, bloch_params=True, init_vals=fit_init_vals)
        bounded_fit = False
    else:
        int_strengths, ivals, bounded_fit_vals, affine_params = _bounded_cr_hamiltonian_tomography(
            cdata,
            time_ns,
            fit_init_vals,
            max_fit_cycles,
            initial_state_weight,
            affine_output,
        )
        bounded_fit = True
    int_strengths = np.array(int_strengths, dtype=float)

    if bounded_fit and affine_output:
        vals0 = np.array(bounded_fit_vals[0], dtype=float)
        vals1 = np.array(bounded_fit_vals[1], dtype=float)
    else:
        vals0 = bloch_functions(time_ns, *ivals[0])
        vals1 = bloch_functions(time_ns, *ivals[1])
    str_phase = wrap_phase_unit_cycle(np.arctan2(int_strengths[2], int_strengths[0]) / (2 * np.pi))
    str_ac_phase = wrap_phase_unit_cycle(np.arctan2(int_strengths[3], int_strengths[1]) / (2 * np.pi))

    return {
        "time_ns": time_ns,
        "rabi_i": rabi_i,
        "rabi_fit_params": rabi_fit_params,
        "norm": float(norm),
        "offset": float(off),
        "cdata": cdata,
        "int_strengths_hz": int_strengths,
        "int_strengths_mhz": 1e3 * int_strengths,
        "str_phase_correction": float(str_phase),
        "str_ac_phase_correction": float(str_ac_phase),
        "fit_vals_control0": vals0,
        "fit_vals_control1": vals1,
        "fit_params_control0": np.array(ivals[0], dtype=float),
        "fit_params_control1": np.array(ivals[1], dtype=float),
        "affine_fit_params_control0": None if not (bounded_fit and affine_output) else np.array(affine_params[0], dtype=float),
        "affine_fit_params_control1": None if not (bounded_fit and affine_output) else np.array(affine_params[1], dtype=float),
        "max_fit_cycles": None if max_fit_cycles is None else float(max_fit_cycles),
        "initial_state_weight": float(initial_state_weight),
        "affine_output": bool(affine_output),
        "bounded_fit": bounded_fit,
    }


def save_rabi_fit_plot(exp, analysis, suffix):
    if not exp.plot_rabi:
        return
    pars = analysis.get("rabi_fit_params")
    if pars is None:
        return
    fig = plt.figure()
    plt.plot(analysis["time_ns"], analysis["rabi_i"], ".", label="data")
    plt.plot(analysis["time_ns"], rabi_fit(analysis["time_ns"], *pars), label="fit")
    plt.grid()
    plt.legend()
    plt.xlabel("Time (ns)")
    plt.ylabel("Target Rabi I (mV)")
    plt.title(f"Target Rabi normalization {suffix}")
    if exp.save_plot:
        plot_formats = getattr(exp, "plot_formats", ("png",))
        if isinstance(plot_formats, str):
            plot_formats = (plot_formats,)
        for fmt in plot_formats:
            fig_path = str(exp.path_to_save) + f"_{suffix}_rabi_fit.{str(fmt).lstrip('.')}"
            fig.savefig(fig_path, bbox_inches="tight")
            exp.results["artifacts"].append(fig_path)
            logger.info("Saved plot: %s", fig_path)
    if exp.show_plot:
        plt.show(block=False)
    else:
        plt.close(fig)

