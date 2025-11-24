from qm import SimulationConfig
from qm.qua import *
from qm.QuantumMachinesManager import QuantumMachinesManager
from Aneesh_configuration_octave import *
from qualang_tools.results import progress_counter, fetching_tool
import numpy as np
import matplotlib.pyplot as plt
from macros_drag import *
import seaborn as sns
from scipy.optimize import minimize

# Initialize QM Manager
qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name, octave=octave_config)

simulate = False
save_data = False

# Define qubits
q1_no = 3 #control
q2_no = 2 #target
cz_elem = "cz_c3t2"

control = 3

qe1 = f"q{q1_no}"
qe2 = f"q{q2_no}"
rr1 = f"rr{q1_no}"
rr2 = f"rr{q2_no}"
out1 = adc_mapping[rr1]
out2 = adc_mapping[rr2]

if control == 3:
    qe_c = qe1
    qe_t = qe2
else:
    qe_c = qe2
    qe_t = qe1

raman_IF = 19.7378 * u.MHz - 4.50 * u.MHz  #for amp = 0.80  pair 2-3
# raman_IF = 22.55 * u.MHz - 3.30 * u.MHz #for amp = 0.60

t_fgge = 152//4  #for amp = 0.80
# t_fgge = 188//4

# a_ram = 0.60
a_ram = 0.80

# Repetition rate
if simulate:
    rep_rate_clk = 100
else:
    rep_rate_clk = 125000

wait_rr = 16
wait_t = 4
n_avgs = 5000*4

target_rot1 = "d_Y90"
target_rot2 = "I"

def prepare_pulse_state(qubit, prep_pulse):
    play(prep_pulse, qubit)

def tomo_pulse_state(qubit, tomo_pulse):
    play(tomo_pulse, qubit)

def two_qubit_tomo_pulse(tomo_pulse1,tomo_pulse2):

    #Prepare initial state
    align()
    wait(rep_rate_clk)
    prepare_pulse_state(qe1, target_rot1)
    align(qe1,qe2)
    prepare_pulse_state(qe2, target_rot2)
    wait(wait_t,qe2)
    wait(wait_t,qe1)

    #Play CNOT
    # CZ_CNOT_macro(cz_elem,qe_c,qe_t,a_ram,t_fgge)
    # CZ_SWAP_macro(cz_elem, qe1, qe2, a_ram, t_fgge)
    CZ_Cphase_macro(cz_elem,qe1,qe2,a_ram,t_fgge)
    # CZ_ISWAP_macro(cz_elem, qe1, qe2, a_ram, t_fgge)

    # align()
    # CZ_Cphase_macro(cz_elem,qe1,qe2,a_ram,t_fgge)
    #Play_CY
    # frame_rotation_2pi(0.25, qe_t)
    # CZ_CNOT_macro(cz_elem,qe_c,qe_t,a_ram,t_fgge)
    # frame_rotation_2pi(-0.25, qe_t)

    align()
    wait(wait_t, qe1)
    wait(wait_t, qe2)
    tomo_pulse_state(qe1, tomo_pulse1)
    tomo_pulse_state(qe2, tomo_pulse2)
    align(qe1,qe2,rr1,rr2)
    measure_macro(qe1, rr1, out1, I1, Q1, pi_12 = False)
    measure_macro(qe2, rr2, out2, I2, Q2, pi_12 = False)
    save(I1, I1_st)
    save(Q1, Q1_st)
    save(I2, I2_st)
    save(Q2, Q2_st)

with program() as two_qubit_tomo:
    I1, Q1, I2, Q2 = declare(fixed), declare(fixed), declare(fixed), declare(fixed)
    I1_st, Q1_st, I2_st, Q2_st = declare_stream(), declare_stream(), declare_stream(), declare_stream()
    n = declare(int)
    n_st = declare_stream()

    Ig1 = declare(fixed)  # I quadrature from the measurement for state 0
    Qg1 = declare(fixed)  # Q quadrature from the measurement
    Ie1 = declare(fixed)  # I quadrature from the measurement for state 1
    Qe1 = declare(fixed)  # Q quadrature from the measurement

    Ig2 = declare(fixed)  # I quadrature from the measurement for state 0
    Qg2 = declare(fixed)  # Q quadrature from the measurement
    Ie2 = declare(fixed)  # I quadrature from the measurement for state 1
    Qe2 = declare(fixed)  # Q quadrature from the measurement

    Ig1_st = declare_stream()
    Qg1_st = declare_stream()
    Ie1_st = declare_stream()
    Qe1_st = declare_stream()
    Ig2_st = declare_stream()
    Qg2_st = declare_stream()
    Ie2_st = declare_stream()
    Qe2_st = declare_stream()

    with for_(n, 0, n < n_avgs, n + 1):

        #Prepare the 0 state for q1,q2
        wait(rep_rate_clk)
        align(qe1, rr1, qe2, rr2)
        measure_macro(qe1, rr1, out1, Ig1, Qg1, pi_12 = False)
        save(Ig1, Ig1_st)
        save(Qg1, Qg1_st)
        measure_macro(qe2, rr2, out2, Ig2, Qg2, pi_12= False)
        save(Ig2, Ig2_st)
        save(Qg2, Qg2_st)

        #State 1 for both Qubits
        wait(rep_rate_clk)
        align(qe1, rr1, qe2, rr2)
        play("d_Y180", qe1)
        play("d_Y180", qe2)
        measure_macro(qe1, rr1,out1, Ie1, Qe1, pi_12 = False)
        save(Ie1, Ie1_st)
        save(Qe1, Qe1_st)
        measure_macro(qe2, rr2, out2, Ie2, Qe2, pi_12 = False)
        save(Ie2, Ie2_st)
        save(Qe2, Qe2_st)

        align(qe1,rr1,qe2,rr2)
        #Starting_tomography
        two_qubit_tomo_pulse("I", "I")
        two_qubit_tomo_pulse("d_X90", "d_X90")
        two_qubit_tomo_pulse("d_mY90", "d_mY90")

        save(n,n_st)

    with stream_processing():

        Ig1_st.average().save("Ig1")
        Qg1_st.average().save("Qg1")

        Ie1_st.average().save("Ie1")
        Qe1_st.average().save("Qe1")

        Ig2_st.average().save("Ig2")
        Qg2_st.average().save("Qg2")

        Ie2_st.average().save("Ie2")
        Qe2_st.average().save("Qe2")

        I1_st.buffer(3).average().save("I1")
        Q1_st.buffer(3).average().save("Q1")

        I2_st.buffer(3).average().save("I2")
        Q2_st.buffer(3).average().save("Q2")

        n_st.save("iteration")

# Execute the program
if simulate:
    job = qmm.simulate(config, two_qubit_tomo, SimulationConfig(int(10000)))
    samples = job.get_simulated_samples()
    samples.con1.plot()
    raise Halted()

qm = qmm.open_qm(config)
job = qm.execute(two_qubit_tomo)
results = fetching_tool(job, data_list=["Ig1", "Qg1", "Ig2", "Qg2", "Ie1", "Qe1", "Ie2", "Qe2", "I1", "Q1", "I2", "Q2", "iteration"], mode="live")


while results.is_processing():

    Ig1, Qg1, Ig2, Qg2, Ie1, Qe1, Ie2, Qe2, I1, Q1, I2, Q2, iteration = results.fetch_all()
    progress_counter(iteration, n_avgs, start_time= results.get_start_time())

    Y1 = [Ig1, Ie1]
    Y2 = [Ig2, Ie2]

    for i in range(3):
        Y1.append(I1[i])
        Y2.append(I2[i])

    # Y1 = np.array(Y1) ; Y2 = np.array(Y2)

    Y1, Y2 = np.array(Y1), np.array(Y2)
    Y1_norm, Y2_norm = [], []

    for i in range(len(Y1)):
        Y1_norm.append(1-2*(Y1[i]-min(Y1))/(max(Y1)-min(Y1)))

    for i in range(len(Y2)):
        Y2_norm.append(1-2*(Y2[i]-min(Y2))/(max(Y2)-min(Y2)))

#-----------------------
#Plot expectation values in a bar-plot
# plt.figure()
# x = ["0","1", "Z", "Y", "X"]
# plt.bar(x, Y1_norm)
#
# plt.figure()
# plt.bar(x, Y2_norm)
#-----------------------------

Ig1, Qg1, Ig2, Qg2, Ie1, Qe1, Ie2, Qe2, I1, Q1, I2, Q2, iteration = results.fetch_all()

Y1 = [Ig1, Ie1]
Y2 = [Ig2, Ie2]

for i in range(3):
    Y1.append(I1[i])
    Y2.append(I2[i])

Y1, Y2 = np.array(Y1), np.array(Y2)
Y1_norm, Y2_norm = [], []

for i in range(len(Y1)):
    Y1_norm.append(1-2*(Y1[i]-min(Y1))/(max(Y1)-min(Y1)))

for i in range(len(Y2)):
    Y2_norm.append(1-2*(Y2[i]-min(Y2))/(max(Y2)-min(Y2)))

expectations = {
    'II': 1.0, 'IX': Y2_norm[4], 'IY': Y2_norm[3], 'IZ': Y2_norm[2],
    'XI': Y1_norm[4], 'XX': Y1_norm[4] * Y2_norm[4], 'XY': Y1_norm[4] * Y2_norm[3], 'XZ': Y1_norm[4] * Y2_norm[2],
    'YI': Y1_norm[3], 'YX': Y1_norm[3] * Y2_norm[4], 'YY': Y1_norm[3] * Y2_norm[3], 'YZ': Y1_norm[3] * Y2_norm[2],
    'ZI': Y1_norm[2], 'ZX': Y1_norm[2] * Y2_norm[4], 'ZY': Y1_norm[2] * Y2_norm[3], 'ZZ': Y1_norm[2] * Y2_norm[2]
}

# Reconstruct the density matrix using these expectation values
def reconstruct_density_matrix(expectations):
    # Define Pauli matrices
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    # Pauli basis for two qubits
    pauli_basis = [I, X, Y, Z]
    labels = ['I', 'X', 'Y', 'Z']

    # Start with an empty density matrix
    rho = np.zeros((4, 4), dtype=complex)

    # Construct the density matrix
    for i, li in enumerate(labels):
        for j, lj in enumerate(labels):
            label = li + lj
            rho += expectations[label] * np.kron(pauli_basis[i], pauli_basis[j])

    # Normalize the density matrix to ensure trace is 1
    rho = rho / 4
    # rho = rho / np.trace(rho)
    return rho

# Calculate the density matrix
rho = reconstruct_density_matrix(expectations)

# Print the density matrix
print("Reconstructed Density Matrix:")
print(rho)

xlabel = ["00","01","10","11"]
ylabel = ["00","01","10","11"]

# Optionally, visualize the density matrix
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
sns.heatmap(np.real(rho), xticklabels= xlabel, yticklabels= ylabel, vmin=-1,vmax=1, annot=True, cmap='BrBG', ax=ax[0]) #coolworm
ax[0].set_title('Real Part of the Density Matrix')
sns.heatmap(np.imag(rho), xticklabels= xlabel, yticklabels= ylabel, vmin=-1,vmax=1, annot=True, cmap='BrBG', ax=ax[1])
ax[1].set_title('Imaginary Part of the Density Matrix')
plt.show()

#Perform Maximum Likelihood Esimation

# def compute_rho(T):
#     T_dagger = np.conjugate(T.T)
#     return np.dot(T_dagger, T) / np.trace(rho)
#
# def frobenius_norm(A, B):
#     return np.linalg.norm(A - B, 'fro')
#
# # Initialize T
# T = np.zeros((4, 4), dtype=complex)
# T[0, 0], T[1, 1], T[2, 2], T[3, 3] = 1, 2, 3, 4
# T[1, 0], T[2, 1], T[3, 2] = 0.5 + 0.1j, 0.2 + 0.3j, 0.4 + 0.5j
# T[2, 0], T[3, 1], T[3, 0] = 0.6 + 0.7j, 0.8 + 0.9j, 1.0 + 1.1j
#
# # Gradient descent parameters
# learning_rate = 0.01
# iterations = 1000
#
# # Optimization loop
# for _ in range(iterations):
#     rho = compute_rho(T)
#     grad = T.conj().T @ (rho - rho)  # Simplified gradient calculation
#     T -= learning_rate * grad  # Update T
#
#     if _ % 100 == 0:  # Print loss every 100 iterations
#         loss = frobenius_norm(compute_rho(T), rho)
#         print(f"Iteration {_}: Loss {loss}")
#
# rho_opt = compute_rho(T)
#----------------------
#Nelder-mead
# def compute_rho1_from_T_vector(T_vector):
#     """Compute rho1 from a flattened T vector."""
#     T = T_vector.reshape((4, 4))  # Reshape T_vector to matrix
#     T_dagger = np.conjugate(T.T)
#     rho1 = np.dot(T_dagger, T) / np.trace(rho)
#     return rho1
# def objective_function(T_vector, noisy_rho):
#     """Objective function to be minimized."""
#     rho1 = compute_rho1_from_T_vector(T_vector)
#     return np.linalg.norm(rho1 - noisy_rho, 'fro')
# # Initial T matrix setup
# T_initial = np.zeros((4, 4), dtype=complex)
# T_initial[0, 0], T_initial[1, 1], T_initial[2, 2], T_initial[3, 3] = 1, 2, 3, 4
# T_initial[1, 0], T_initial[2, 1], T_initial[3, 2] = 0.5 + 0.1j, 0.2 + 0.3j, 0.4 + 0.5j
# T_initial[2, 0], T_initial[3, 1], T_initial[3, 0] = 0.6 + 0.7j, 0.8 + 0.9j, 1.0 + 1.1j
# # Flatten T_initial to use it as an initial guess
# T_initial_vector = T_initial.flatten()
# # Optimization using Nelder-Mead
# result = minimize(
#     objective_function,
#     T_initial_vector,
#     args=(rho,),
#     method='Nelder-Mead',
#     options={'xatol': 1e-6, 'disp': True, 'maxiter': 5000}
# )
# # Get the optimized T from the result
# T_optimized = result.x.reshape((4, 4))
# rho_opt = compute_rho1_from_T_vector(T_optimized)
# # # Print results
# # # print("Optimized T Matrix:")
# # # print(T_optimized)
#
# fig, ax = plt.subplots(1, 2, figsize=(12, 5))
# sns.heatmap(np.real(rho_opt), xticklabels= xlabel, yticklabels= ylabel, vmin=-1,vmax=1, annot=True, cmap='BrBG', ax=ax[0]) #coolworm
# ax[0].set_title('Real Part of the Density Matrix')
# sns.heatmap(np.imag(rho_opt), xticklabels= xlabel, yticklabels= ylabel, vmin=-1,vmax=1, annot=True, cmap='BrBG', ax=ax[1])
# ax[1].set_title('Imaginary Part of the Density Matrix')
# plt.show()


if save_data:
    file_saver_([Ig1, Qg1, Ig2, Qg2, Ie1, Qe1, Ie2, Qe2, I1[0], Q1[0], I1[1], Q1[1],I1[2], Q1[2], I2[0], Q2[0], I2[1], Q2[1],I2[2], Q2[2]], suffix= f"data_q{q1_no}_{target_rot1}_q{q2_no}_{target_rot2}", file_name=__file__,
                master_folder=ExpName, header_string="Ig1, Qg1, Ig2, Qg2, Ie1, Qe1, Ie2, Qe2, Z1_I, Z1_Q, Y1_I, Y1_Q,X1_I, X1_Q, Z2_I, Z2_Q, Y2_I, Y2_Q,X2_I, X2_Q")

    file_saver_(np.real(rho), suffix= f"rho_real_{target_rot1}_{target_rot2}", file_name=__file__,
                master_folder=ExpName)

    file_saver_(np.imag(rho), suffix= f"rho_imag_{target_rot1}_{target_rot2}", file_name=__file__,
                master_folder=ExpName)
