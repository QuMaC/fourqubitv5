"""
        RABI CHEVRON (DURATION VS FREQUENCY)
This sequence involves executing the qubit pulse (be it x180, square_pi, or another type) and measuring the state of
the resonator across various qubit intermediate frequencies and pulse durations.
Analyzing the results allows for determining the qubit and estimating the x180 pulse duration for a specific amplitude.

Prerequisites:
    - Determination of the resonator's resonance frequency when coupled to the qubit of interest (referred to as "resonator_spectroscopy").
    - Calibration of the IQ mixer connected to the qubit drive line (whether external mixer or an Octave port).
    - Identification of the approximate qubit frequency ("qubit_spectroscopy").
    - Configuration of the qubit frequency and the desired pi pulse amplitude (labeled as "x180_amp").

Before proceeding to the next node:
    - Adjust the qubit frequency setting, labeled as "qubit_IF", in the configuration.
    - Modify the qubit pulse duration setting, labeled as "x180_len", in the configuration.
"""
import numpy as np
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm import SimulationConfig
from configuration_4qubitsv3 import *
from qualang_tools.results import progress_counter, fetching_tool
from qualang_tools.plot import interrupt_on_close
from qualang_tools.loops import from_array
import matplotlib.pyplot as plt

q_no = 1
qe = f"q{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
q_IF_val = q_IF[f"{q_no}"]
out = adc_mapping[rr]


simulate = False
save_data = False


if simulate:
    rep_rate_clk = 300
else:
    rep_rate_clk = 250000

###################
# The QUA program #
###################
n_avg = 200  # The number of averages
# The frequency sweep parameters
# span = 30 * u.MHz
# df = 200 * u.kHz
# dfs = np.arange(-span, span + 0.1, df)

f_min = -20 * u.MHz
f_max = 20 * u.MHz
df = 0.50 * u.MHz

freq= np.arange(f_min, f_max, df)

# Pulse duration sweep (in clock cycles = 4ns) - must be larger than 4 clock cycles

# t_min = 4
# t_max = 1000
# dt = 10
# durations = np.arange(t_min, t_max, dt)

t_min_ns = 16
t_max_ns = 1000
dt_ns = 4 #minimum 4ns

t_min = int(t_min_ns/4)
t_max = int(t_max_ns/4)
dt = int(dt_ns/4)
t_list = np.arange(t_min, t_max, dt)


# ===================================
with program() as rabi_amp_freq:
    n = declare(int)  # QUA variable for the averaging loop
    f = declare(int)  # QUA variable for the qubit frequency
    t = declare(int)  # QUA variable for the qubit pulse duration
    I = declare(fixed)  # QUA variable for the measured 'I' quadrature
    Q = declare(fixed)  # QUA variable for the measured 'Q' quadrature
    I_st = declare_stream()  # Stream for the 'I' quadrature
    Q_st = declare_stream()  # Stream for the 'Q' quadrature
    n_st = declare_stream()  # Stream for the averaging iteration 'n'

    with for_(n, 0, n < n_avg, n + 1):  # QUA for_ loop for averaging
        with for_(t, t_min, t < t_max + dt/2, t + dt):  # QUA for_ loop for sweeping the pulse duration
            with for_(*from_array(f,freq)):  # QUA for_ loop for sweeping the frequency
                # Update the frequency of the digital oscillator linked to the qubit element
                update_frequency(qe, f+q_IF_val)
                # Play the qubit pulse with a variable duration (in clock cycles = 4ns)
                play("const"*amp(0.5), qe, duration=t)
                # play("const"*amp(0.3),qe,duration=t)
                # Align the two elements to measure after playing the qubit pulse.
                align(qe, rr)
                # Measure the state of the resonator.
                # The integration weights have changed to maximize the SNR after having calibrated the IQ blobs.
                measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))
                # Wait for the qubit to decay to the ground state
                wait(rep_rate_clk)
                # Save the 'I' & 'Q' quadratures to their respective streams
                save(I, I_st)
                save(Q, Q_st)
        # Save the averaging iteration to get the progress bar
        save(n, n_st)

    with stream_processing():
        # Cast the data into a 2D matrix, average the 2D matrices together and store the results on the OPX processor
        I_st.buffer(len(freq)).buffer(len(t_list)).average().save("I")
        Q_st.buffer(len(freq)).buffer(len(t_list)).average().save("Q")
        n_st.save("iteration")


#####################################
#  Open Communication with the QOP  #
#####################################
qmm = QuantumMachinesManager()
# qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name,octave=octave_config)
###########################
# Run or Simulate Program #
###########################


if simulate:
    # Simulates the QUA program for the specified duration
    simulation_config = SimulationConfig(duration=10_000)  # In clock cycles = 4ns
    job = qmm.simulate(config, rabi_amp_freq, simulation_config)
    job.get_simulated_samples().con1.plot()
else:
    # Open the quantum machine
    qm = qmm.open_qm(config)
    # Send the QUA program to the OPX, which compiles and executes it
    job = qm.execute(rabi_amp_freq)
    # Get results from QUA program
    results = fetching_tool(job, data_list=["I", "Q", "iteration"], mode="live")
    # Live plotting
    fig = plt.figure()
    interrupt_on_close(fig, job)  #  Interrupts the job when closing the figure
    while results.is_processing():
        # Fetch results
        I, Q, iteration = results.fetch_all()
        # # Convert results into Volts
        # S = u.demod2volts(I + 1j * Q, readout_len)
        # R = np.abs(S)  # Amplitude
        # phase = np.angle(S)  # Phase
        # Progress bar
        progress_counter(iteration, n_avg, start_time=results.get_start_time())
        # Plot results
        # plt.subplot(211)
        # plt.suptitle(f"Rabi chevron with LO={qubit_LO / u.GHz}GHz and IF={qubit_IF / u.MHz}MHz")
        plt.title(f"Rabi chevron")
        plt.cla()
        # plt.title(r"$R=\sqrt{I^2 + Q^2}$")
        plt.pcolor(t_list * 4,freq / u.MHz, np.transpose(I))
        plt.ylabel("Frequency detuning [MHz]")
        plt.xlabel("Pulse duration [ns]")
        # plt.title("Phase")
        # plt.pcolor(dfs / u.MHz, durations * 4, np.unwrap(phase))

        plt.tight_layout()
        plt.pause(0.1)

    I, Q, iteration = results.fetch_all()
    plt.title(f"Rabi chevron")
    plt.cla()
    # plt.title(r"$R=\sqrt{I^2 + Q^2}$")
    plt.pcolor(t_list * 4,freq / u.MHz, np.transpose(I))
    plt.ylabel("Frequency detuning [MHz]")
    plt.xlabel("Pulse duration [ns]")


    if save_data is True:
        file_saver_(t_list*4, file_name=__file__,
                    master_folder=ExpName, header_string="time (ns)",suffix="time ",time_stamp=True)

        file_saver_(np.transpose(I), file_name=__file__,
                        master_folder=ExpName, header_string="Ivalues",suffix="Ivalues",time_stamp=True)

        file_saver_(np.transpose(Q), file_name=__file__,
                        master_folder=ExpName, header_string="Qvalues",suffix="Qvalues",time_stamp=True)

        file_saver_(freq/u.MHz, file_name=__file__,
                        master_folder=ExpName, header_string="Detuning (MHz)",suffix="Detunings",time_stamp=True)
