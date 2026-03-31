import time
import json
from HM.single_qubit_experiments.single_qubit_base import SingleQubitExperiment
from Configuration_Files.config_dictionaries import rr_IF, q_IF, rr_LO, q_LO, f, u
from HM.utilities.post_processing_utils import return_elec_delay
from HM.utilities.files_utils import save_json
import numpy as np
from Helper_Functions.macros import update_config_rr
from Helper_Functions.spectro_helper import smooth_filter
from qm.qua import for_each_, program, declare, for_, update_frequency, fixed, declare_stream, wait, measure, save, stream_processing, demod, play, amp, align
from qualang_tools.loops import from_array  
from Configuration_Files.Spectroscopy_Settings.spectro_settings import qubit_spec_settings, resonator_spec_settings
from qm import QuantumMachinesManager, SimulationConfig, LoopbackInterface
import matplotlib.pyplot as plt
import logging
from termcolor import cprint
from Helper_Functions.spectro_helper import get_sweep_array
from Helper_Functions.macros import measure_macro
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class QubitSpectroscopy(SingleQubitExperiment):
    def __init__(self, q_no: int, rr_no: int = None, **kwargs):
        # Default n_avg from settings if not provided (avoid passing n_avg twice to super)
        kwargs.setdefault("n_avg", qubit_spec_settings["qubits"][f"{q_no}"]["n_avg"])
        super().__init__(q_no, rr_no, expt_name="qubit_spec", **kwargs)

        self.prev_q_frequency = float(self.fq)
        self.sweep_span_MHz = kwargs.get("sweep_span_MHz", 200)
        self.sweep_npts = kwargs.get("sweep_npts", 100)
        self.sweep_method = kwargs.get("sweep_method", "linear") #linear or quadratic
        self.saturation_len = kwargs.get("saturation_len", 8) #in microseconds
        self.saturation_amp = kwargs.get("saturation_amp", 0.6 ) #pre-factor to the value defined in the config - restricted to [-2; 2)
        
        self.sweep_array = get_sweep_array(self.sweep_span_MHz, self.sweep_npts, self.sweep_method, custom_spacing=kwargs.get("custom_spacing", None))
        #need to create a final frequency array and an array that has IF frequencies
        self.final_freq_array = self.sweep_array*u.MHz + self.prev_q_frequency*u.GHz
        self.saturation_duration_in_clock_cycles = self.saturation_len*u.us//self.clock_cycle_dur_ns # *u.us converts the duration to ns and then //self.clock_cycle_dur_ns converts it to clock cycles
        print(self.saturation_duration_in_clock_cycles)
        # IF in Hz as integers (QUA update_frequency expects int; floats get fixed-point and overflow)
        self.IF_array = np.round(
            self.final_freq_array - self.q_lo * u.MHz
        ).astype(np.int64)

        #query and set LO's so that we can reach our target freqs?

    
    def run_experiment(self):
        qe = self.q_str
        rr = self.rr_str
        out = self.out
        f_LO = self.q_lo*u.MHz
        # print(self.n_avg)
        # exit()

        with program() as qubit_spec:
            n = declare(int)
            I = declare(fixed)
            I_st = declare_stream()
            Q = declare(fixed)
            Q_st = declare_stream()
            f = declare(int)
            n_st = declare_stream()
            with for_(n, 0, n < self.n_avg, n + 1):
                with for_each_(f, self.IF_array):
                    update_frequency(self.q_str, f)
                    align(self.rr_str, self.q_str)
                    play("const" * amp(self.saturation_amp), self.q_str, duration=self.saturation_duration_in_clock_cycles)
                    measure_macro(qe, rr, out, I, Q, pi_12=False) #macro aligns as well

                    wait(20000, self.q_str)

                    save(I, I_st)
                    save(Q, Q_st)

                save(n, n_st)

            with stream_processing():
                I_st.buffer(len(self.IF_array)).average().save('I')
                Q_st.buffer(len(self.IF_array)).average().save('Q')

        qmm = QuantumMachinesManager(host=self.qm_ip, cluster_name=self.cluster_name)

        qm = qmm.open_qm(self.config)
        job = qm.execute(qubit_spec)
        res_handles = job.result_handles

        # Wait for the first value to be available (job is running)
        res_handles.wait_for_all_values()
        # Or wait until job is fully done: job.halt() not used, so job runs to completion

        # Fetch all data (blocks until job completes and streams are ready)
        I = res_handles.get("I").fetch_all()
        Q = res_handles.get("Q").fetch_all()

        # Plot
        freqs_MHz = self.final_freq_array / 1e6  # Hz -> MHz for axis
        fig, axs = plt.subplots(3, 1, sharex=True)
        axs[0].plot(freqs_MHz, I, marker=".", label="I")
        axs[1].plot(freqs_MHz, Q, marker=".", label="Q")
        axs[2].plot(freqs_MHz, np.abs(I + 1j * Q), marker=".", label="|I + jQ|")
        for ax in axs:
            ax.set_xlabel("Frequency (MHz)")
            ax.set_ylabel("Amplitude (a.u.)")
            ax.legend()
            ax.grid(True)
        
        fig.suptitle(f"Qubit spectroscopy q{self.q_no}")
        plt.tight_layout()
        plt.show()

        return I, Q
















if __name__ == "__main__":
    q_no = 1
    rr_no = 1
    n_avg = 300000
    span_npts = 1000
    qubit_spec = QubitSpectroscopy(q_no, rr_no, n_avg=n_avg, sweep_npts=span_npts)
    qubit_spec.run_experiment()
    