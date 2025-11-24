"""
intro_to_integration.py: Demonstrate usage of the integration in the measure statement
Author: Gal Winer - Quantum Machines
Created: 31/12/2020
Revised by Tomer Feld - Quantum Machines
Revision date: 24/04/2022
"""

from qm import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig, LoopbackInterface
from Configuration_Files.configuration_4qubitsv3 import *
import matplotlib.pyplot as plt
from Helper_Functions.macros import *
import scipy
from Helper_Functions.spectro_helper import *


def norm_proper(sig):
    return (sig - np.mean(sig)) / np.linalg.norm(sig - np.mean(sig))


# Open communication with the server.
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

q_no = 6
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]
pi_len_config = pi_len_ns[f"{q_no}"]

rr_I = dac_mapping[rr][1][0]
rr_Q = dac_mapping[rr][1][0]

avgs = 50

con = f'con{dac_mapping[qe][0]}'

# Sliced demodulation parameters
num_segments = ro_len // 2
seg_length = ro_len // (num_segments)

# Moving window demodulation parameters
samples_per_chunk = 20
chunks_per_window = 3
arr_size = 10

time_factor = 0.25

measure_type = 'accumulated'

config["integration_weights"][f"new_dummy_cos{q_no}"] = {}
config["integration_weights"][f"new_dummy_cos{q_no}_mw"] = {}
config["integration_weights"][f"new_dummy_minusSin{q_no}"] = {}
config["integration_weights"][f"new_dummy_minusSin{q_no}_mw"] = {}

config["integration_weights"][f"new_dummy_cos{q_no}"]["cosine"] = [
    (np.cos(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_cos{q_no}"]["sine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_minusSin{q_no}"]["cosine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_minusSin{q_no}"]["sine"] = [
    (-np.cos(optimal_readout_phase[f"rr{q_no}"]), int(ro_len))]

config["integration_weights"][f"new_dummy_cos{q_no}_mw"]["cosine"] = [
    (np.cos(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk) * 4 * arr_size)]

config["integration_weights"][f"new_dummy_cos{q_no}_mw"]["sine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk) * 4 * arr_size)]

config["integration_weights"][f"new_dummy_minusSin{q_no}_mw"]["cosine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk) * 4 * arr_size)]

config["integration_weights"][f"new_dummy_minusSin{q_no}_mw"]["sine"] = [
    (-np.cos(optimal_readout_phase[f"rr{q_no}"]), int(samples_per_chunk) * 4 * arr_size)]

config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_cos'] = f"new_dummy_cos{q_no}"
config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_minusSin'] = f"new_dummy_minusSin{q_no}"

config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_cos_mw'] = f"new_dummy_cos{q_no}_mw"

with program() as measureProg:
    ind = declare(int)
    I_0 = declare(fixed)
    I_1 = declare(fixed)

    int_stream_0 = declare_stream()
    acc_int_stream_0 = declare_stream()
    mov_int_stream_0 = declare_stream()
    raw_adc_0 = declare_stream(adc_trace=True)

    sliced_demod_res_0 = declare(fixed, size=int(num_segments))
    acc_demod_res_0 = declare(fixed, size=int(num_segments))
    mov_demod_res_0 = declare(fixed, size=arr_size)

    int_stream_1 = declare_stream()
    acc_int_stream_1 = declare_stream()
    mov_int_stream_1 = declare_stream()
    raw_adc_1 = declare_stream(adc_trace=True)

    sliced_demod_res_1 = declare(fixed, size=int(num_segments))
    acc_demod_res_1 = declare(fixed, size=int(num_segments))
    mov_demod_res_1 = declare(fixed, size=arr_size)

    n = declare(int)

    with for_(n, 0, n < avgs, n + 1):
        # wait(2500000)
        cooldown(250000, qe=qe)
        reset_frame(rr)
        reset_frame(qe)

        play("I", qe)
        wait(4, qe)
        align(qe, qe_12)
        # play('X180', qe)
        play('X180', qe_12)
        align('stark_6', qe_12)
        # align(qe_12, rr)
        ramp_to_zero('stark_6')
        wait(4, 'stark_6')
        align('stark_6', qe_12)
        wait(4, rr)

        align(qe_12, rr)
        wait(4, rr)

        if measure_type == 'sliced':
            measure("readout", rr, None, demod.sliced("integW_cos", sliced_demod_res_0, seg_length, out))
            with for_(ind, 0, ind < num_segments, ind + 1):  # save a QUA array
                save(sliced_demod_res_0[ind], int_stream_0)
        elif measure_type == 'accumulated':
            measure("readout", rr, None, demod.accumulated("integW_cos", acc_demod_res_0, seg_length, out))
            with for_(ind, 0, ind < num_segments, ind + 1):  # save a QUA array
                save(acc_demod_res_0[ind], acc_int_stream_0)
        elif measure_type == 'moving_avg':
            measure(
                "readout",
                rr,
                None,
                demod.moving_window("new_dummy_cos_mw", mov_demod_res_0, samples_per_chunk, chunks_per_window,
                                    element_output=out))
        elif measure_type == 'full':
            measure("readout", rr, raw_adc_0, demod.full("integW_cos", I_0, out))
            save(I_0, "full_0")

        # reset_phase(rr)

        # # reset_phase(rr)

        # wait(2500000)
        cooldown(250000, qe=qe)

        play('X180', qe)
        wait(4, qe)
        align(qe, qe_12)
        # play('X180', qe)
        play('X180', qe_12)
        align('stark_6', qe_12)
        # align(qe_12, rr)
        ramp_to_zero('stark_6')
        wait(4, 'stark_6')
        align('stark_6', qe_12)
        wait(4, rr)

        align(qe_12, rr)
        wait(4, rr)

        if measure_type == 'sliced':
            measure("readout", rr, None, demod.sliced("integW_cos", sliced_demod_res_1, seg_length, out))
            with for_(ind, 0, ind < num_segments, ind + 1):  # save a QUA array
                save(sliced_demod_res_1[ind], int_stream_1)
        elif measure_type == 'accumulated':
            measure("readout", rr, None, demod.accumulated("integW_cos", acc_demod_res_1, seg_length, out))
            with for_(ind, 0, ind < num_segments, ind + 1):  # save a QUA array
                save(acc_demod_res_1[ind], acc_int_stream_1)
        elif measure_type == 'moving_avg':
            measure(
                "readout",
                rr,
                None,
                demod.moving_window("new_dummy_cos_mw", mov_demod_res_1, samples_per_chunk, chunks_per_window,
                                    element_output=out))
        elif measure_type == 'full':
            measure("readout", rr, raw_adc_1, demod.full("integW_cos", I_1, out))
            save(I_1, "full_1")

    with stream_processing():
        if measure_type == 'sliced':
            int_stream_0.buffer(num_segments).average().save("demod_sliced_0")
            int_stream_1.buffer(num_segments).average().save("demod_sliced_1")
            int_stream_0.buffer(num_segments).save_all('demod_0_data_all')
            int_stream_1.buffer(num_segments).save_all('demod_1_data_all')
        elif measure_type == 'accumulated':
            acc_int_stream_0.buffer(num_segments).average().save("demod_acc_0")
            acc_int_stream_1.buffer(num_segments).average().save("demod_acc_1")
            acc_int_stream_0.buffer(num_segments).save_all('demo_acc_0_data_all')
            acc_int_stream_1.buffer(num_segments).save_all('demo_acc_1_data_all')
        elif measure_type == 'moving_avg':
            mov_int_stream_0.average().save_all("demod_mov_0")
            mov_int_stream_1.average().save_all("demod_mov_1")
        elif measure_type == 'full':
            raw_adc_0.input1().average().save_all("raw_input_0")
            raw_adc_1.input1().average().save_all("raw_input_1")

qm = qmm.open_qm(config)
job = qm.execute(measureProg)

res = job.result_handles
res.wait_for_all_values()
# full = res.full_0.fetch_all()["value"]
# print(f"Result of full demodulation: {full}")
if measure_type == 'sliced':
    data_0 = res.get('demod_sliced_0').fetch_all()
    data_1 = res.get('demod_sliced_1').fetch_all()
    data_0_shots = res.get('demod_0_data_all').fetch_all()['value']
    data_1_shots = res.get('demod_1_data_all').fetch_all()['value']
elif measure_type == 'accumulated':
    data_0 = res.get('demod_acc_0').fetch_all()
    data_1 = res.get('demod_acc_1').fetch_all()
    data_0_shots = res.get('demo_acc_0_data_all').fetch_all()['value']
    data_1_shots = res.get('demo_acc_1_data_all').fetch_all()['value']
elif measure_type == 'moving_avg':
    data_0 = res.get('demod_mov_0').fetch_all()['value']
    data_1 = res.get('demod_mov_1').fetch_all()['value']
elif measure_type == 'full':
    data_0 = res.get('raw_input_0').fetch_all()['value']
    data_1 = res.get('raw_input_1').fetch_all()['value']
# sliced_0 = res.get('demod_sliced_0').fetch_all()['value']
# sliced_1 = res.get('demod_sliced_1').fetch_all()['value']


# demod_mov = res.get('demod_mov_0').fetch_all()
# print(f"Result of sliced demodulation in {num_segments} segments:{sliced}")

plt.figure()
plt.plot(data_0, label=measure_type + ' data_0')
plt.plot(data_1, label=measure_type + ' data_1')
plt.grid()
plt.legend()
plt.title(measure_type + f' demod on q{q_no}')
plt.show(block=False)
# [f, (ax1, ax2)] = plt.subplots(nrows=1, ncols=2)
# ax1.plot(sliced, "o-")
# ax1.set_title("sliced demod")
# ax1.set_xlabel("slice number")
#
# ax2.plot(res.demod_acc.fetch_all(), "o-")
# ax2.set_title("acc demodulation")
# ax2.set_xlabel("slice number")
# plt.show(block=False)
#
# plt.figure()
# plt.plot(res.raw_input.fetch_all() / 2**12)
# plt.xlabel("t[ns]")
# plt.ylabel("output [V]")
# plt.title("Raw output")
# plt.show(block=False)
#
# plt.figure()
# plt.plot(demod_mov / 2**12, "o-")
# plt.xlabel("sample number")
# plt.title("moving windows")
# plt.show(block=False)


# window_size = int(max(seg_length // 100, 10))  # 10 works for 500 samples
# fil_sig_0 = smooth_filter(data_0, window_size)[window_size - 1:-window_size + 1]
# fil_sig_1 = smooth_filter(data_1, window_size)[window_size - 1:-window_size + 1]

coeff_0 = np.loadtxt(f'{measure_type}_fil_sig_0.csv', delimiter=',')
coeff_1 = np.loadtxt(f'{measure_type}_fil_sig_1.csv', delimiter=',')

filter_sos = scipy.signal.butter(4, (10 / ro_len) * 1e9, 'low', output='sos', fs=1e9)

fil_sig_0 = scipy.signal.sosfilt(filter_sos, data_0)
fil_sig_1 = scipy.signal.sosfilt(filter_sos, data_1)

d_0 = norm_proper(fil_sig_0)
c_0 = norm_proper(coeff_0)
c_1 = norm_proper(coeff_1)
d_1 = norm_proper(fil_sig_1)

corr_00 = scipy.signal.correlate(d_0, c_0)
corr_01 = scipy.signal.correlate(d_0, c_1)
corr_11 = scipy.signal.correlate(d_1, c_1)
corr_10 = scipy.signal.correlate(d_1, c_0)

plt.figure()
plt.plot(corr_00, label='corr_00')
plt.plot(corr_01, label='corr_01')
plt.plot(corr_11, label='corr_11')
plt.plot(corr_10, label='corr_10')
plt.legend()
plt.grid()
plt.title(f'{avgs} averaging')
plt.show(block=False)

plt.figure()
plt.plot(fil_sig_0, label=measure_type + ' data_0')
plt.plot(fil_sig_1, label=measure_type + ' data_1')
plt.grid()
plt.legend()
plt.title(measure_type + f' demod on q{q_no}')
plt.show(block=False)

i = len(fil_sig_0) // 3
e = 2 * len(fil_sig_0) // 3

Y_1 = np.fft.fft(fil_sig_0[i:e]) * (2 / len(fil_sig_0[i:e]))
Y_2 = np.fft.fft(fil_sig_1[i:e]) * (2 / len(fil_sig_1[i:e]))

X = np.fft.fftfreq(n=len(fil_sig_0[i:e]), d=2e-9)

Y_1 = Y_1[1:len(Y_1) // 2]
Y_2 = Y_2[1:len(Y_2) // 2]
X = X[1:len(X) // 2]

a = np.where(np.abs(Y_1) == np.max(np.abs(Y_1)))[0][0]
b = np.where(np.abs(Y_2) == np.max(np.abs(Y_2)))[0][0]

max_amp_1 = np.abs(Y_1)[a]
max_amp_2 = np.abs(Y_2)[b]

plt.figure()
plt.plot(X, np.abs(Y_1), label='data_0')
plt.plot(X, np.abs(Y_2), label='data_1')
plt.grid()
plt.show(block=False)

## End FFT
#
#
# filter_sos = scipy.signal.butter(4, (20 / ro_len) * 1e9, 'low', output='sos', fs=1e9)
#
# iir_data_0 = scipy.signal.sosfilt(filter_sos, data_0)
# iir_data_1 = scipy.signal.sosfilt(filter_sos, data_1)
#
# plt.figure()
# plt.plot(iir_data_1, label='iir_data_1')
# plt.plot(iir_data_0, label='iir_data_0')
# # plt.plot(data_0)
# # plt.plot(data_1)
# plt.grid()
# plt.legend()
# plt.show(block=False)
#
# iir_data_normed_0 = norm_proper(iir_data_0)
# iir_data_normed_1 = norm_proper(iir_data_1)
#

if avgs > 9999:
    np.savetxt(
        f'{measure_type}_fil_sig_0.csv',
        d_0,
        delimiter=',',
    )

    np.savetxt(
        f'{measure_type}_fil_sig_1.csv',
        d_1,
        delimiter=',',
    )

#######################  HMM trial
#
# mean_0 = fil_sig_0
# cov_0 = np.cov(data_0_shots, rowvar=False)
#
# mean_1 = fil_sig_1
# cov_1 = np.cov(data_1_shots, rowvar=False)
#
# eps = 1e-6
# cov_0 += eps * np.eye(cov_0.shape[0])
# cov_1 += eps * np.eye(cov_1.shape[0])
#
# from scipy.stats import multivariate_normal
# from sklearn.metrics import confusion_matrix
#
# mv_0 = multivariate_normal(mean=mean_0, cov=cov_0)
# mv_1 = multivariate_normal(mean=mean_1, cov=cov_1)
#
# log_likelihood_0 = mv_0.logpdf(avgs)
# log_likelihood_1 = mv_1.logpdf(avgs)
#
# predicted_labels = (log_likelihood_1 > log_likelihood_0).astype(int)
#
# template = fil_sig_1 - fil_sig_0
# template /= np.linalg.norm(template)  # Normalize for numerical stability
#
# all_shots = np.concatenate([data_0_shots, data_1_shots], axis=0)
#
# labels = [0]*len(data_0_shots)
# t = [1]*len(data_0_shots)
# labels.extend(t)
#
# # Step 2: Project all shots
# projections = all_shots @ template  # Shape: (n_shots,)
#
# # Step 3: Compute threshold (midpoint between class projections)
# proj_0 = fil_sig_0 @ template
# proj_1 = fil_sig_1 @ template
# threshold = 0.5 * (proj_0 + proj_1)
#
# # Step 4: Classify based on projection
# predicted_labels = (projections > threshold).astype(int)
#
# # Step 5: Compute fidelity
# tn, fp, fn, tp = confusion_matrix(labels, predicted_labels).ravel()
# P_error_0 = fp / (fp + tn)
# P_error_1 = fn / (fn + tp)
# readout_fidelity = 1 - 0.5 * (P_error_0 + P_error_1)

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from hmmlearn import hmm
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import joblib
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

data_0_flt_shots = []
data_1_flt_shots = []

for shot in data_0_shots:
    temp = scipy.signal.sosfilt(filter_sos, shot)
    data_0_flt_shots.append(temp)

for shot in data_1_shots:
    temp = scipy.signal.sosfilt(filter_sos, shot)
    data_1_flt_shots.append(temp)


# Combine test shots and labels
shots = np.vstack([data_0_flt_shots, data_1_flt_shots])
labels = np.array([0] * len(data_0_shots) + [1] * len(data_1_shots))

X = np.vstack([data_0_flt_shots, data_1_flt_shots])
y = np.hstack([np.zeros(len(data_0_shots)), np.ones(len(data_1_shots))])

# pca = PCA(n_components=10)
# shots_pca = pca.fit_transform(X)

X, y = shuffle(X, y, random_state=42)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Apply PCA only on training data
pca = PCA(n_components=30)
X_train_pca = pca.fit_transform(X_train)
X_test_pca = pca.transform(X_test)

# Train classifier on PCA-transformed data
clf1 = RandomForestClassifier(n_estimators=50, max_depth=20, random_state=42, n_jobs=-1)
clf1.fit(X_train_pca, y_train)



# Evaluate on test data
y_pred = clf1.predict(X_test_pca)
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
fidelity = 1 - 0.5 * (fp / (fp + tn) + fn / (fn + tp))
print(f"Fidelity: {fidelity:.2%}")

# Load the trained model and PCA transform
# rf_model = joblib.load(f"./classifier/random_forest_readout_classifier_1_{measure_type}.joblib")
# pca_model = joblib.load(f"./classifier/pca_transform_1_{measure_type}.joblib")

# Apply PCA transform to the same sliced region used during training
# X_test_pca = pca_model.transform(shots)  # use same slice as training

# Predict and evaluate fidelity
# pred = rf_model.predict(shots)
# tn, fp, fn, tp = confusion_matrix(labels, pred).ravel()
# fidelity_rf_loaded = 1 - 0.5 * (fp / (fp + tn) + fn / (fn + tp))
# print(f"TN={tn}, FP={fp}, FN={fn}, TP={tp}")
#
# print(f"Fidelity: {fidelity_rf_loaded:.2%}")
def corr_filter(data, coeff_0, coeff_1):

    d = norm_proper(data)
    c_0 = norm_proper(coeff_0)
    c_1 = norm_proper(coeff_1)

    corr_0 = scipy.signal.correlate(d, c_0)
    corr_1 = scipy.signal.correlate(d, c_1)

    if max(corr_0) > max(corr_1):
        return 0
    else:
        return 1

pred = []
for shot in shots:
    temp = corr_filter(shot, coeff_0, coeff_1)
    pred.append(temp)

hits = [pred[i] == labels[i] for i in range(len(pred))]

