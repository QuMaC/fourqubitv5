from Helper_Functions.helper_functionsv2 import *
AC_AMP_FACTOR = 0.4

def config_add_controller(config, con_no, dc_offsets, adc_offsets, gain_dict):
    if not "controllers" in config: config["controllers"] = {}

    config["controllers"][f"con{con_no}"] = {}
    config["controllers"][f"con{con_no}"]["type"] = "opx1"
    config["controllers"][f"con{con_no}"]["analog_outputs"] = {}

    for i in range(1, 11):
        config["controllers"][f"con{con_no}"]["analog_outputs"][i] = {"offset": dc_offsets[f"con{con_no}"][f"{i}"]}

    config["controllers"][f"con{con_no}"]["digital_outputs"] = {}
    config["controllers"][f"con{con_no}"]["analog_inputs"] = {}

    for i in range(1, 3):
        config["controllers"][f"con{con_no}"]["analog_inputs"][i] = {"offset": adc_offsets[f"con{con_no}"][f"{i}"],
                                                                     'gain_db': gain_dict[f"con{con_no}"][f"{i}"]}

    return config


def config_add_common_elements(config):
    config["pulses"] = {"zero": {"operation": "control",
                                 "length": 100,
                                 "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
                                 },

                        "const_pulse": {
                            "operation": "control",
                            "length": 100,
                            "waveforms": {"I": "const_wf", "Q": "zero_wf"},
                        },
                        }

    config["waveforms"] = {"zero_wf": {"type": "constant", "sample": 0.0},
                           "const_wf": {"type": "constant", "sample": AC_AMP_FACTOR},
                           }

    config["digital_waveforms"] = {"ON": {"samples": [(1, 0)]}}

    return config


def config_add_elements_q_rr(config, q_no, rr_no, dac_mapping, q_LO, q_IF, rr_LO, rr_IF, pi_len_ns, piby2_len_ns,
                             pi_rise_grft_ns, amp_scale,
                             mixers, mixer_corrections, ro_amp, ro_len_clk, tof, integ_len_clk, optimal_readout_phase,
                             opt_weights=None, smearing=0):
    '''
    Given parameters, this function adds the qubit, readout resonator, and all the standard pulses and waveforms to the config.
    '''

    ################ ADD ELEMENTS ################
    # Add qubit
    if not "elements" in config: config["elements"] = {}
    config['elements'][f"q{q_no}"] = {
        "mixInputs": {
            "I": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][0]),
            "Q": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][1]),
            "lo_frequency": q_LO[f"{q_no}"],
            "mixer": mixers[f"q{q_no}"],
        },
        "intermediate_frequency": q_IF[f"{q_no}"],
        "operations": {
            "const": "const_pulse",
            "grft": f"q{q_no}_grft",
            "X180": f"q{q_no}_X180",
            "X360": f"q{q_no}_X360",
            "Y360": f"q{q_no}_Y360",
            "X90": f"q{q_no}_X90",
            "mX90": f"q{q_no}_mX90",
            "Y180": f"q{q_no}_Y180",
            "Y90": f"q{q_no}_Y90",
            "mY90": f"q{q_no}_mY90",
            "I": "zero",
        },
    }

    # add corresponding rr
    config['elements'][f"rr{rr_no}"] = {
        "mixInputs": {
            "I": (f"con{dac_mapping[f'rr{rr_no}'][0]}", dac_mapping[f'rr{rr_no}'][1][0]),
            "Q": (f"con{dac_mapping[f'rr{rr_no}'][0]}", dac_mapping[f'rr{rr_no}'][1][1]),
            "lo_frequency": rr_LO[f"{rr_no}"],
            "mixer": mixers[f"rr{rr_no}"],
        },
        "intermediate_frequency": rr_IF[f"{rr_no}"],
        "outputs": {
            "out1": (f"con{dac_mapping[f'rr{rr_no}'][0]}", 1),
            "out2": (f"con{dac_mapping[f'rr{rr_no}'][0]}", 2),
        },
        "time_of_flight": tof[f"{rr_no}"],
        "smearing": smearing,
        "operations": {
            "const": f"const_pulse",
            "readout": f"q{rr_no}_ro_pulse",
        }
    }

    ####### ADD CORRESPONDING PULSES #########
    if not "pulses" in config: config["pulses"] = {}
    if not "waveforms" in config: config["waveforms"] = {}
    # add all control pulses
    for key in config["elements"][f"q{q_no}"]["operations"]:
        pul = config["elements"][f"q{q_no}"]["operations"][key]
        # print(pul)
        if pul == "const_pulse" or pul == "zero":
            continue

        pul_name = pul.split('_')[1]
        if "m" in pul: pul_name = pul.split('_')[1][1:]

        config["pulses"][pul] = {
            "operation": "control",
            "length": pi_len_ns[f"{q_no}"],
            "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
        }

        if 'grft' in pul:
            config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
            config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                  "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}

        if "X" in pul:
            config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
            # add waveform
            if "m" in pul:
                config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                              [-amp_scale[f"{q_no}"][pul_name]])}
            else:
                config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                              [amp_scale[f"{q_no}"][pul_name]])}

        if "Y" in pul:
            config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
            # add waveform
            if "m" in pul:
                config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                              [-amp_scale[f"{q_no}"][pul_name]])}
            else:
                config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                              [amp_scale[f"{q_no}"][pul_name]])}

        if "90" in pul:
            config["pulses"][pul]["length"] = piby2_len_ns[f"{q_no}"]

    # add readout pulse
    config["pulses"][f"q{q_no}_ro_pulse"] = {
        "operation": "measurement",
        "length": ro_len_clk[f"{q_no}"] * 4,
        "waveforms": {"I": f"q{q_no}_ro_wf", "Q": "zero_wf"},
        "integration_weights": {
            "integW_cos": f"integW_cos_rr{q_no}",
            "integW_sin": f"integW_sin_rr{q_no}",
            "integW_minus_sin": f"integW_minus_sin_rr{q_no}",
            # 'acc_cos': f"acc_cos_rr{q_no}",
            # 'acc_minus_sin': f"acc_minus_sin{q_no}",
        },
        "digital_marker": "ON",
    }

    ro_pulse_square = False
    if ro_pulse_square:
        config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "constant",
                                                  "sample": AC_AMP_FACTOR * ro_amp[str(rr_no)]}


    else:
        config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "arbitrary",
                                                  "samples": grft_arr_gen((ro_len_clk[str(rr_no)] * 4, 200),
                                                                          [ro_amp[str(rr_no)]])}
    # config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "ramp",
    #                                           "sample": 0.4 * ro_amp[str(rr_no)]}
    # add integration weights
    if not "integration_weights" in config: config["integration_weights"] = {}

    config["integration_weights"][f"integW_cos_rr{rr_no}"] = {}
    config["integration_weights"][f"integW_sin_rr{rr_no}"] = {}
    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"] = {}
    # config["integration_weights"][f"acc_cos_rr{q_no}_mw"] = {}
    # config["integration_weights"][f"acc_minus_sin{q_no}"] = {}



    config["integration_weights"][f"integW_cos_rr{rr_no}"]["cosine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_cos_rr{rr_no}"]["sine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    config["integration_weights"][f"integW_sin_rr{rr_no}"]["cosine"] = [
        (np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_sin_rr{rr_no}"]["sine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["cosine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["sine"] = [
        (-np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    if opt_weights is not None and f"rr{rr_no}" in opt_weights:
        config["integration_weights"][f"optW_cos_rr{rr_no}"] = {
            "cosine": [tuple(k) for k in opt_weights[f"rr{rr_no}"]["optW_cos"]],
            "sine": [tuple(k) for k in opt_weights[f"rr{rr_no}"]["optW_minus_sin"]],
        }
        config["integration_weights"][f"optW_minus_sin_rr{rr_no}"] = {
            "cosine": [tuple(k) for k in opt_weights[f"rr{rr_no}"]["optW_minus_sin"]],
            "sine": [(-1*k[0], k[1]) for k in opt_weights[f"rr{rr_no}"]["optW_cos"]],
        }

        ro_pulse_name = config["elements"][f"rr{rr_no}"]["operations"]["readout"]
        config["pulses"][ro_pulse_name]["integration_weights"]["optW_cos"] = f"optW_cos_rr{rr_no}"
        config["pulses"][ro_pulse_name]["integration_weights"]["optW_minus_sin"] = f"optW_minus_sin_rr{rr_no}"

    # add mixers
    if not "mixers" in config: config["mixers"] = {}
    config["mixers"][f"mixer_q{q_no}"] = [{"intermediate_frequency": q_IF[f"{q_no}"], "lo_frequency": q_LO[f"{q_no}"],
                                           "correction": mixer_corrections[f"q{q_no}"]}]
    config["mixers"][f"mixer_rr{q_no}"] = [
        {"intermediate_frequency": rr_IF[f"{rr_no}"], "lo_frequency": rr_LO[f"{rr_no}"],
         "correction": mixer_corrections[f"rr{rr_no}"]}]

    return config


def config_add_drag_grft(config, q_no, q_anh, pi_len_ns, piby2_len_ns, pi_rise_grft_ns, amp_scale, drag_dict):
    '''
    Given parameters, this function adds the drag-corrected control pulses to the config gate-set.
    '''
    ################ ADD ELEMENTS ####################
    # Add DRAG pulses to qubit
    config['elements'][f"q{q_no}"]["operations"].update({"d_X180": f"q{q_no}_d_X180",
                                                         "d_X90": f"q{q_no}_d_X90",
                                                         "d_mX90": f"q{q_no}_d_mX90",
                                                         "d_Y180": f"q{q_no}_d_Y180",
                                                         "d_Y90": f"q{q_no}_d_Y90",
                                                         "d_Y360": f"q{q_no}_d_Y360",
                                                         "d_X360": f"q{q_no}_d_X360",
                                                         "d_mY90": f"q{q_no}_d_mY90"})

    for key in config["elements"][f"q{q_no}"]["operations"]:
        pul = config["elements"][f"q{q_no}"]["operations"][key]

        if "d" in pul:
            if "m" in pul:
                pul_name = pul.split("_")[2][1:]
            else:
                pul_name = pul.split("_")[2]

            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"],
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }

            if "X" in pul:
                config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
                config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"

                # Add waveform
                if "m" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

                else:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

            if "Y" in pul:
                config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
                config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"

                # Add waveform
                if "m" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}

                else:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}
            if "90" in pul:
                config["pulses"][pul]["length"] = piby2_len_ns[f"{q_no}"]

    return config

def config_add_rise_fall(config, cr_tail_ns):
    config["pulses"]["rise_pulse"] = {
        "operation": "control",
        "length": cr_tail_ns,
        "waveforms": {"I": "rise_wf", "Q": "zero_wf"},
    }

    config["pulses"]["fall_pulse"] = {
        "operation": "control",
        "length": cr_tail_ns,
        "waveforms": {"I": "fall_wf", "Q": "zero_wf"},
    }

    config["waveforms"]["rise_wf"] = {"type": "arbitrary", "samples": rise_arr(cr_tail_ns)}
    config["waveforms"]["fall_wf"] = {"type": "arbitrary", "samples": fall_arr(cr_tail_ns)}

    return config


def config_add_crgate(config, control, target, dac_mapping, q_LO, q_IF, mixers, mixer_corrections):
    qe = f"cr_c{control}t{target}"
    qe_ac = f"cr_ac_c{control}t{target}"

    config['elements'][qe] = {
        "mixInputs": {
            "I": (f"con{dac_mapping[f'q{control}'][0]}", dac_mapping[qe][1][0]),
            "Q": (f"con{dac_mapping[f'q{control}'][0]}", dac_mapping[qe][1][1]),
            "lo_frequency": q_LO[f"{control}"],
            "mixer": mixers[qe],
        },
        "intermediate_frequency": q_IF[f"{target}"],
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    config['elements'][qe_ac] = {
        "mixInputs": {
            "I": (f"con{dac_mapping[f'q{target}'][0]}", dac_mapping[f'q{target}'][1][0]),
            "Q": (f"con{dac_mapping[f'q{target}'][0]}", dac_mapping[f'q{target}'][1][1]),
            "lo_frequency": q_LO[f"{target}"],
            "mixer": mixers[qe_ac],
        },
        "intermediate_frequency": q_IF[f"{target}"],
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    config["mixers"][mixers[qe]] = [{"intermediate_frequency": q_IF[f"{target}"], "lo_frequency": q_LO[f"{control}"],
                                     "correction": mixer_corrections[qe]}]

    return config


def config_add_q12(config, q_no, dac_mapping, q_LO, q12_IF,
                   pi_12_len_ns, piby2_12_len_ns, pi_rise_grft_ns, amp_12_scale, mixers, mixer_corrections):
    config['elements'][f"q12_{q_no}"] = {
        "mixInputs": {
            "I": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][0]),
            "Q": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][1]),
            "lo_frequency": q_LO[f"{q_no}"],
            "mixer": mixers[f"q12_{q_no}"],
        },
        "intermediate_frequency": q12_IF[f"{q_no}"],
        "operations": {
            "const": "const_pulse",
            "grft": f"q12_{q_no}_grft",
            "X180": f"q12_{q_no}_X180",
            "X360": f"q12_{q_no}_X360",
            "X90": f"q12_{q_no}_X90",
            "mX90": f"q12_{q_no}_mX90",
            "Y180": f"q12_{q_no}_Y180",
            "Y90": f"q12_{q_no}_Y90",
            "mY90": f"q12_{q_no}_mY90",
            "I": "zero",
        },
    }

    for key in config["elements"][f"q12_{q_no}"]["operations"]:
        pul = config["elements"][f"q12_{q_no}"]["operations"][key]
        # print(pul)
        if pul == "const_pulse" or pul == "zero":
            continue

        pul_name = pul.split('_')[2]
        if "m" in pul: pul_name = pul.split('_')[2][1:]

        config["pulses"][pul] = {
            "operation": "control",
            "length": pi_12_len_ns[f"{q_no}"],
            "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
        }

        if 'grft' in pul:
            config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
            config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                  "samples": grft_arr_gen((pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                          1)}

        if "X" in pul:
            config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
            # add waveform
            if "m" in pul:
                config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen(
                                                          (pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                          [-amp_12_scale[f"{q_no}"][pul_name]])}
            else:
                config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen(
                                                          (pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                          [amp_12_scale[f"{q_no}"][pul_name]])}

        if "Y" in pul:
            config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
            # add waveform
            if "m" in pul:
                config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen(
                                                          (pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                          [-amp_12_scale[f"{q_no}"][pul_name]])}
            else:
                config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen(
                                                          (pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                          [amp_12_scale[f"{q_no}"][pul_name]])}

        if "90" in pul:
            config["pulses"][pul]["length"] = piby2_12_len_ns[f"{q_no}"]

        config["mixers"][f"mixer_q12_{q_no}"] = [
            {"intermediate_frequency": q12_IF[f"{q_no}"], "lo_frequency": q_LO[f"{q_no}"],
             "correction": mixer_corrections[f"q12_{q_no}"]}]

    return config


def config_add_tonestark(config, q_no, dac_mapping, stark_LO, q_IF, stark_IF, stark_amp, mixers, mixer_corrections):

    qe = f"stark_{q_no}"
    freq_IF = stark_IF[f"{q_no}"]

    if q_no != 6:
        config['elements'][qe] = {
            "mixInputs": {
                "I": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][0]),
                "Q": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][1]),
                "lo_frequency": stark_LO[f"{q_no}"],
                "mixer": mixers[f"stark_{q_no}"],
            },

        "intermediate_frequency": freq_IF,
        # "sticky": {"analog": True, "duration": 4},
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
            # "stark": "stark_pulse"
        }, }
    else:
        config['elements'][qe] = {
            "mixInputs": {
                "I": (f"con{dac_mapping[f'q{q_no}'][0]}", 5),
                "Q": (f"con{dac_mapping[f'q{q_no}'][0]}", 6),
                "lo_frequency": stark_LO[f"{q_no}"],
                "mixer": mixers[f"stark_{q_no}"],
            },

        "intermediate_frequency": freq_IF,
        "sticky": {"analog": True, "duration": 320},
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
            # "stark": "stark_pulse"
        }, }


    # config["pulses"]["stark_pulse"] = {"operation": "control",
    #                                    "length": 112,
    #                                    "waveforms": {"I": "stark_wf", "Q": "zero_wf"},
    #                                    }

    # config["waveforms"]["stark_wf"] = {"type": "constant", "sample": 0.4 * stark_amp[f"{q_no}"]}
    # config["waveforms"]["stark_wf"] = {"type": "arbitrary",
    #                                                   "samples": grft_arr_gen(
    #                                                       (pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
    #                                                       [-amp_12_scale[f"{q_no}"][pul_name]])}

    config["mixers"][mixers[qe]] = [{"intermediate_frequency": freq_IF, "lo_frequency": stark_LO[f"{q_no}"],
                                     "correction": mixer_corrections[qe]}]

    return config
