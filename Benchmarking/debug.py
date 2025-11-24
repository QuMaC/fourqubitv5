
# Single QUA script generated at 2025-03-20 20:52:54.793660
# QUA library version: 1.2.1

from qm import CompilerOptionArguments
from qm.qua import *

with program() as prog:
    v1 = declare(int, )
    v2 = declare(fixed, )
    v3 = declare(fixed, )
    v4 = declare(fixed, )
    v5 = declare(fixed, )
    v6 = declare(fixed, )
    v7 = declare(fixed, )
    v8 = declare(fixed, )
    v9 = declare(fixed, )
    v10 = declare(fixed, )
    v11 = declare(fixed, )
    v12 = declare(fixed, )
    v13 = declare(fixed, )
    v14 = declare(fixed, )
    v15 = declare(fixed, )
    v16 = declare(fixed, )
    v17 = declare(fixed, )
    v18 = declare(fixed, )
    v19 = declare(fixed, )
    v20 = declare(fixed, )
    v21 = declare(fixed, )
    v22 = declare(fixed, )
    v23 = declare(fixed, )
    v24 = declare(fixed, )
    v25 = declare(fixed, )
    v26 = declare(fixed, )
    v27 = declare(fixed, )
    v28 = declare(fixed, )
    v29 = declare(fixed, )
    v30 = declare(fixed, )
    v31 = declare(fixed, )
    v32 = declare(fixed, )
    v33 = declare(fixed, )
    v34 = declare(fixed, )
    v35 = declare(fixed, )
    v36 = declare(fixed, )
    v37 = declare(fixed, )
    v38 = declare(fixed, )
    v39 = declare(fixed, )
    v40 = declare(fixed, )
    v41 = declare(fixed, )
    v42 = declare(fixed, )
    v43 = declare(fixed, )
    v44 = declare(fixed, )
    v45 = declare(fixed, )
    v46 = declare(fixed, )
    v47 = declare(fixed, )
    v48 = declare(fixed, )
    v49 = declare(fixed, )
    v50 = declare(fixed, )
    v51 = declare(fixed, )
    v52 = declare(fixed, )
    v53 = declare(fixed, )
    v54 = declare(fixed, )
    v55 = declare(fixed, )
    v56 = declare(fixed, )
    v57 = declare(fixed, )
    v58 = declare(fixed, )
    v59 = declare(fixed, )
    v60 = declare(fixed, )
    v61 = declare(fixed, )
    v62 = declare(fixed, )
    v63 = declare(fixed, )
    v64 = declare(fixed, )
    v65 = declare(fixed, )
    v66 = declare(fixed, )
    v67 = declare(fixed, )
    v68 = declare(fixed, )
    v69 = declare(fixed, )
    v70 = declare(fixed, )
    v71 = declare(fixed, )
    v72 = declare(fixed, )
    v73 = declare(fixed, )
    v74 = declare(fixed, )
    v75 = declare(fixed, )
    v76 = declare(fixed, )
    v77 = declare(fixed, )
    v78 = declare(fixed, )
    v79 = declare(fixed, )
    update_frequency("q5", -45252279.0, "Hz", False)
    with for_(v1,0,(v1<10000.0),(v1+1)):
        wait(250000, "q5")
        wait(20, "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v2, "out1"), demod.full("integW_minus_sin", v3, "out1"))
        r1 = declare_stream()
        save(v2, r1)
        r22 = declare_stream()
        save(v3, r22)
        wait(250000, "q5")
        play("d_X180", "q5")
        wait(20, "q5")
        play("d_X180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v4, "out1"), demod.full("integW_minus_sin", v5, "out1"))
        r2 = declare_stream()
        save(v4, r2)
        r23 = declare_stream()
        save(v5, r23)
        wait(250000, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v8, 0.9166666666666666)
        assign(v9, -0.75)
        assign(v10, 1.6666666666666667)
        assign(v11, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v8, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v9, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v10, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v11, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        wait(20, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v12, 0.9166666666666666)
        assign(v13, -0.75)
        assign(v14, 1.6666666666666667)
        assign(v15, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v12, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v13, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v14, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v15, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v6, "out1"), demod.full("integW_minus_sin", v7, "out1"))
        r3 = declare_stream()
        save(v6, r3)
        r24 = declare_stream()
        save(v7, r24)
        wait(250000, "q5")
        play("d_X180", "q5")
        wait(20, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v18, 0.9166666666666666)
        assign(v19, -0.75)
        assign(v20, 1.6666666666666667)
        assign(v21, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v18, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v19, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v20, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v21, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v16, "out1"), demod.full("integW_minus_sin", v17, "out1"))
        r4 = declare_stream()
        save(v16, r4)
        r25 = declare_stream()
        save(v17, r25)
        wait(250000, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v24, 0.9166666666666666)
        assign(v25, -0.75)
        assign(v26, 1.6666666666666667)
        assign(v27, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v24, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v25, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v26, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v27, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        wait(20, "q5")
        play("d_X180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v22, "out1"), demod.full("integW_minus_sin", v23, "out1"))
        r5 = declare_stream()
        save(v22, r5)
        r26 = declare_stream()
        save(v23, r26)
        wait(250000, "q5")
        play("d_X90", "q5")
        wait(20, "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v28, "out1"), demod.full("integW_minus_sin", v29, "out1"))
        r6 = declare_stream()
        save(v28, r6)
        r27 = declare_stream()
        save(v29, r27)
        wait(250000, "q5")
        play("d_Y90", "q5")
        wait(20, "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v30, "out1"), demod.full("integW_minus_sin", v31, "out1"))
        r7 = declare_stream()
        save(v30, r7)
        r28 = declare_stream()
        save(v31, r28)
        wait(250000, "q5")
        play("d_X90", "q5")
        wait(20, "q5")
        play("d_Y90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v32, "out1"), demod.full("integW_minus_sin", v33, "out1"))
        r8 = declare_stream()
        save(v32, r8)
        r29 = declare_stream()
        save(v33, r29)
        wait(250000, "q5")
        play("d_Y90", "q5")
        wait(20, "q5")
        play("d_X90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v34, "out1"), demod.full("integW_minus_sin", v35, "out1"))
        r9 = declare_stream()
        save(v34, r9)
        r30 = declare_stream()
        save(v35, r30)
        wait(250000, "q5")
        play("d_X90", "q5")
        wait(20, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v38, 0.9166666666666666)
        assign(v39, -0.75)
        assign(v40, 1.6666666666666667)
        assign(v41, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v38, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v39, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v40, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v41, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v36, "out1"), demod.full("integW_minus_sin", v37, "out1"))
        r10 = declare_stream()
        save(v36, r10)
        r31 = declare_stream()
        save(v37, r31)
        wait(250000, "q5")
        play("d_Y90", "q5")
        wait(20, "q5")
        play("d_X180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v42, "out1"), demod.full("integW_minus_sin", v43, "out1"))
        r11 = declare_stream()
        save(v42, r11)
        r32 = declare_stream()
        save(v43, r32)
        wait(250000, "q5")
        play("d_X180", "q5")
        wait(20, "q5")
        play("d_Y90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v44, "out1"), demod.full("integW_minus_sin", v45, "out1"))
        r12 = declare_stream()
        save(v44, r12)
        r33 = declare_stream()
        save(v45, r33)
        wait(250000, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v48, 0.9166666666666666)
        assign(v49, -0.75)
        assign(v50, 1.6666666666666667)
        assign(v51, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v48, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v49, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v50, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v51, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        wait(20, "q5")
        play("d_X90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v46, "out1"), demod.full("integW_minus_sin", v47, "out1"))
        r13 = declare_stream()
        save(v46, r13)
        r34 = declare_stream()
        save(v47, r34)
        wait(250000, "q5")
        play("d_X90", "q5")
        wait(20, "q5")
        play("d_X180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v52, "out1"), demod.full("integW_minus_sin", v53, "out1"))
        r14 = declare_stream()
        save(v52, r14)
        r35 = declare_stream()
        save(v53, r35)
        wait(250000, "q5")
        play("d_X180", "q5")
        wait(20, "q5")
        play("d_X90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v54, "out1"), demod.full("integW_minus_sin", v55, "out1"))
        r15 = declare_stream()
        save(v54, r15)
        r36 = declare_stream()
        save(v55, r36)
        wait(250000, "q5")
        play("d_Y90", "q5")
        wait(20, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v58, 0.9166666666666666)
        assign(v59, -0.75)
        assign(v60, 1.6666666666666667)
        assign(v61, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v58, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v59, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v60, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v61, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v56, "out1"), demod.full("integW_minus_sin", v57, "out1"))
        r16 = declare_stream()
        save(v56, r16)
        r37 = declare_stream()
        save(v57, r37)
        wait(250000, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v64, 0.9166666666666666)
        assign(v65, -0.75)
        assign(v66, 1.6666666666666667)
        assign(v67, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v64, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v65, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v66, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v67, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        wait(20, "q5")
        play("d_Y90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v62, "out1"), demod.full("integW_minus_sin", v63, "out1"))
        r17 = declare_stream()
        save(v62, r17)
        r38 = declare_stream()
        save(v63, r38)
        wait(250000, "q5")
        play("d_X180", "q5")
        wait(20, "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v68, "out1"), demod.full("integW_minus_sin", v69, "out1"))
        r18 = declare_stream()
        save(v68, r18)
        r39 = declare_stream()
        save(v69, r39)
        wait(250000, "q5")
        frame_rotation_2pi(-0.25, "q5")
        assign(v72, 0.9166666666666666)
        assign(v73, -0.75)
        assign(v74, 1.6666666666666667)
        assign(v75, -1.6666666666666667)
        play("d_X180", "q5")
        frame_rotation_2pi(v72, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v73, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v74, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(v75, "q5")
        play("d_X180", "q5")
        frame_rotation_2pi(0.25, "q5")
        play("d_Y180", "q5")
        wait(20, "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v70, "out1"), demod.full("integW_minus_sin", v71, "out1"))
        r19 = declare_stream()
        save(v70, r19)
        r40 = declare_stream()
        save(v71, r40)
        wait(250000, "q5")
        play("d_X90", "q5")
        wait(20, "q5")
        play("d_X90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v76, "out1"), demod.full("integW_minus_sin", v77, "out1"))
        r20 = declare_stream()
        save(v76, r20)
        r41 = declare_stream()
        save(v77, r41)
        wait(250000, "q5")
        play("d_Y90", "q5")
        wait(20, "q5")
        play("d_Y90", "q5")
        align("q5", "rr5")
        wait(16, "rr5")
        measure("readout", "rr5", None, demod.full("integW_cos", v78, "out1"), demod.full("integW_minus_sin", v79, "out1"))
        r21 = declare_stream()
        save(v78, r21)
        r42 = declare_stream()
        save(v79, r42)
    with stream_processing():
        r1.average().save("Ixy_0")
        r22.average().save("Qxy_0")
        r2.average().save("Ixy_1")
        r23.average().save("Qxy_1")
        r3.average().save("Ixy_2")
        r24.average().save("Qxy_2")
        r4.average().save("Ixy_3")
        r25.average().save("Qxy_3")
        r5.average().save("Ixy_4")
        r26.average().save("Qxy_4")
        r6.average().save("Ixy_5")
        r27.average().save("Qxy_5")
        r7.average().save("Ixy_6")
        r28.average().save("Qxy_6")
        r8.average().save("Ixy_7")
        r29.average().save("Qxy_7")
        r9.average().save("Ixy_8")
        r30.average().save("Qxy_8")
        r10.average().save("Ixy_9")
        r31.average().save("Qxy_9")
        r11.average().save("Ixy_10")
        r32.average().save("Qxy_10")
        r12.average().save("Ixy_11")
        r33.average().save("Qxy_11")
        r13.average().save("Ixy_12")
        r34.average().save("Qxy_12")
        r14.average().save("Ixy_13")
        r35.average().save("Qxy_13")
        r15.average().save("Ixy_14")
        r36.average().save("Qxy_14")
        r16.average().save("Ixy_15")
        r37.average().save("Qxy_15")
        r17.average().save("Ixy_16")
        r38.average().save("Qxy_16")
        r18.average().save("Ixy_17")
        r39.average().save("Qxy_17")
        r19.average().save("Ixy_18")
        r40.average().save("Qxy_18")
        r20.average().save("Ixy_19")
        r41.average().save("Qxy_19")
        r21.average().save("Ixy_20")
        r42.average().save("Qxy_20")


config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.03439100687984689,
                },
                "2": {
                    "offset": -0.00456807440883176,
                },
                "3": {
                    "offset": -0.027224942669403993,
                },
                "4": {
                    "offset": -0.00746944472185292,
                },
                "5": {
                    "offset": 0.007251527048272247,
                },
                "6": {
                    "offset": 0.004582863340542396,
                },
                "7": {
                    "offset": -0.01004958944627166,
                },
                "8": {
                    "offset": 0.004911278856552271,
                },
                "9": {
                    "offset": 0.011454769566979228,
                },
                "10": {
                    "offset": 0.001733100950205538,
                },
            },
            "digital_outputs": {},
            "analog_inputs": {
                "1": {
                    "offset": 0.2629143867543879,
                    "gain_db": 20,
                },
                "2": {
                    "offset": 0.2840686339716801,
                    "gain_db": 20,
                },
            },
        },
        "con2": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.023109068899027727,
                },
                "2": {
                    "offset": -0.030702739253611902,
                },
                "3": {
                    "offset": -0.00977638920851303,
                },
                "4": {
                    "offset": -0.027215368254123427,
                },
                "5": {
                    "offset": 0.0,
                },
                "6": {
                    "offset": 0.0,
                },
                "7": {
                    "offset": 0.011644772330749321,
                },
                "8": {
                    "offset": 0.001698276611435881,
                },
                "9": {
                    "offset": -0.00027563385255682457,
                },
                "10": {
                    "offset": -0.0022497087424338796,
                },
            },
            "digital_outputs": {},
            "analog_inputs": {
                "1": {
                    "offset": 0.23809878542844415,
                    "gain_db": 20,
                },
                "2": {
                    "offset": 0.23036690812516145,
                    "gain_db": 20,
                },
            },
        },
        "con3": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": 0.003256753126844797,
                },
                "2": {
                    "offset": -0.0005252833477161794,
                },
                "3": {
                    "offset": -0.0015988851853745718,
                },
                "4": {
                    "offset": 0.0026215662243260036,
                },
                "5": {
                    "offset": 0.0,
                },
                "6": {
                    "offset": 0.0,
                },
                "7": {
                    "offset": -0.008435945429116389,
                },
                "8": {
                    "offset": -0.0022479689331722026,
                },
                "9": {
                    "offset": -0.011279786195934931,
                },
                "10": {
                    "offset": -0.007801638796693005,
                },
            },
            "digital_outputs": {},
            "analog_inputs": {
                "1": {
                    "offset": 0.15253875033329783,
                    "gain_db": 20,
                },
                "2": {
                    "offset": 0.2151648584392131,
                    "gain_db": 20,
                },
            },
        },
    },
    "pulses": {
        "zero": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "zero_wf",
            },
        },
        "const_pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
        },
        "q1_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y360_Q_wf",
            },
        },
        "q1_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y180_Q_wf",
            },
        },
        "q1_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y90_Q_wf",
            },
        },
        "q1_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_mY90_Q_wf",
            },
        },
        "q1_ro_pulse": {
            "operation": "measurement",
            "length": 3040,
            "waveforms": {
                "I": "q1_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr1",
                "integW_sin": "integW_sin_rr1",
                "integW_minus_sin": "integW_minus_sin_rr1",
            },
            "digital_marker": "ON",
        },
        "q1_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_X180_I_wf",
                "Q": "q1_d_X180_Q_wf",
            },
        },
        "q1_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_X90_I_wf",
                "Q": "q1_d_X90_Q_wf",
            },
        },
        "q1_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_mX90_I_wf",
                "Q": "q1_d_mX90_Q_wf",
            },
        },
        "q1_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y180_I_wf",
                "Q": "q1_d_Y180_Q_wf",
            },
        },
        "q1_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y90_I_wf",
                "Q": "q1_d_Y90_Q_wf",
            },
        },
        "q1_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y360_I_wf",
                "Q": "q1_d_Y360_Q_wf",
            },
        },
        "q1_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_X360_I_wf",
                "Q": "q1_d_X360_Q_wf",
            },
        },
        "q1_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_mY90_I_wf",
                "Q": "q1_d_mY90_Q_wf",
            },
        },
        "q2_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y360_Q_wf",
            },
        },
        "q2_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y180_Q_wf",
            },
        },
        "q2_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y90_Q_wf",
            },
        },
        "q2_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_mY90_Q_wf",
            },
        },
        "q2_ro_pulse": {
            "operation": "measurement",
            "length": 10000,
            "waveforms": {
                "I": "q2_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr2",
                "integW_sin": "integW_sin_rr2",
                "integW_minus_sin": "integW_minus_sin_rr2",
            },
            "digital_marker": "ON",
        },
        "q2_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_X180_I_wf",
                "Q": "q2_d_X180_Q_wf",
            },
        },
        "q2_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_X90_I_wf",
                "Q": "q2_d_X90_Q_wf",
            },
        },
        "q2_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_mX90_I_wf",
                "Q": "q2_d_mX90_Q_wf",
            },
        },
        "q2_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y180_I_wf",
                "Q": "q2_d_Y180_Q_wf",
            },
        },
        "q2_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y90_I_wf",
                "Q": "q2_d_Y90_Q_wf",
            },
        },
        "q2_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y360_I_wf",
                "Q": "q2_d_Y360_Q_wf",
            },
        },
        "q2_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_X360_I_wf",
                "Q": "q2_d_X360_Q_wf",
            },
        },
        "q2_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_mY90_I_wf",
                "Q": "q2_d_mY90_Q_wf",
            },
        },
        "q3_grft": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_X180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_X360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_Y360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y360_Q_wf",
            },
        },
        "q3_X90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_mX90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_Y180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y180_Q_wf",
            },
        },
        "q3_Y90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y90_Q_wf",
            },
        },
        "q3_mY90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_mY90_Q_wf",
            },
        },
        "q3_ro_pulse": {
            "operation": "measurement",
            "length": 4000,
            "waveforms": {
                "I": "q3_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr3",
                "integW_sin": "integW_sin_rr3",
                "integW_minus_sin": "integW_minus_sin_rr3",
            },
            "digital_marker": "ON",
        },
        "q3_d_X180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_X180_I_wf",
                "Q": "q3_d_X180_Q_wf",
            },
        },
        "q3_d_X90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_X90_I_wf",
                "Q": "q3_d_X90_Q_wf",
            },
        },
        "q3_d_mX90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_mX90_I_wf",
                "Q": "q3_d_mX90_Q_wf",
            },
        },
        "q3_d_Y180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_Y180_I_wf",
                "Q": "q3_d_Y180_Q_wf",
            },
        },
        "q3_d_Y90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_Y90_I_wf",
                "Q": "q3_d_Y90_Q_wf",
            },
        },
        "q3_d_Y360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_Y360_I_wf",
                "Q": "q3_d_Y360_Q_wf",
            },
        },
        "q3_d_X360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_X360_I_wf",
                "Q": "q3_d_X360_Q_wf",
            },
        },
        "q3_d_mY90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q3_d_mY90_I_wf",
                "Q": "q3_d_mY90_Q_wf",
            },
        },
        "q4_grft": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_X180": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_X360": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_Y360": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y360_Q_wf",
            },
        },
        "q4_X90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_mX90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_Y180": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y180_Q_wf",
            },
        },
        "q4_Y90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y90_Q_wf",
            },
        },
        "q4_mY90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_mY90_Q_wf",
            },
        },
        "q4_ro_pulse": {
            "operation": "measurement",
            "length": 3200,
            "waveforms": {
                "I": "q4_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr4",
                "integW_sin": "integW_sin_rr4",
                "integW_minus_sin": "integW_minus_sin_rr4",
            },
            "digital_marker": "ON",
        },
        "q4_d_X180": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_X180_I_wf",
                "Q": "q4_d_X180_Q_wf",
            },
        },
        "q4_d_X90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_X90_I_wf",
                "Q": "q4_d_X90_Q_wf",
            },
        },
        "q4_d_mX90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_mX90_I_wf",
                "Q": "q4_d_mX90_Q_wf",
            },
        },
        "q4_d_Y180": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_Y180_I_wf",
                "Q": "q4_d_Y180_Q_wf",
            },
        },
        "q4_d_Y90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_Y90_I_wf",
                "Q": "q4_d_Y90_Q_wf",
            },
        },
        "q4_d_Y360": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_Y360_I_wf",
                "Q": "q4_d_Y360_Q_wf",
            },
        },
        "q4_d_X360": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_X360_I_wf",
                "Q": "q4_d_X360_Q_wf",
            },
        },
        "q4_d_mY90": {
            "operation": "control",
            "length": 72,
            "waveforms": {
                "I": "q4_d_mY90_I_wf",
                "Q": "q4_d_mY90_Q_wf",
            },
        },
        "q5_grft": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_X180": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_X360": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_Y360": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y360_Q_wf",
            },
        },
        "q5_X90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_mX90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_Y180": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y180_Q_wf",
            },
        },
        "q5_Y90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y90_Q_wf",
            },
        },
        "q5_mY90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_mY90_Q_wf",
            },
        },
        "q5_ro_pulse": {
            "operation": "measurement",
            "length": 1760,
            "waveforms": {
                "I": "q5_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr5",
                "integW_sin": "integW_sin_rr5",
                "integW_minus_sin": "integW_minus_sin_rr5",
            },
            "digital_marker": "ON",
        },
        "q5_d_X180": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_X180_I_wf",
                "Q": "q5_d_X180_Q_wf",
            },
        },
        "q5_d_X90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_X90_I_wf",
                "Q": "q5_d_X90_Q_wf",
            },
        },
        "q5_d_mX90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_mX90_I_wf",
                "Q": "q5_d_mX90_Q_wf",
            },
        },
        "q5_d_Y180": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_Y180_I_wf",
                "Q": "q5_d_Y180_Q_wf",
            },
        },
        "q5_d_Y90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_Y90_I_wf",
                "Q": "q5_d_Y90_Q_wf",
            },
        },
        "q5_d_Y360": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_Y360_I_wf",
                "Q": "q5_d_Y360_Q_wf",
            },
        },
        "q5_d_X360": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_X360_I_wf",
                "Q": "q5_d_X360_Q_wf",
            },
        },
        "q5_d_mY90": {
            "operation": "control",
            "length": 36,
            "waveforms": {
                "I": "q5_d_mY90_I_wf",
                "Q": "q5_d_mY90_Q_wf",
            },
        },
        "q6_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y360_Q_wf",
            },
        },
        "q6_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y180_Q_wf",
            },
        },
        "q6_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y90_Q_wf",
            },
        },
        "q6_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_mY90_Q_wf",
            },
        },
        "q6_ro_pulse": {
            "operation": "measurement",
            "length": 1040,
            "waveforms": {
                "I": "q6_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr6",
                "integW_sin": "integW_sin_rr6",
                "integW_minus_sin": "integW_minus_sin_rr6",
            },
            "digital_marker": "ON",
        },
        "q6_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_X180_I_wf",
                "Q": "q6_d_X180_Q_wf",
            },
        },
        "q6_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_X90_I_wf",
                "Q": "q6_d_X90_Q_wf",
            },
        },
        "q6_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_mX90_I_wf",
                "Q": "q6_d_mX90_Q_wf",
            },
        },
        "q6_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_Y180_I_wf",
                "Q": "q6_d_Y180_Q_wf",
            },
        },
        "q6_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_Y90_I_wf",
                "Q": "q6_d_Y90_Q_wf",
            },
        },
        "q6_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_Y360_I_wf",
                "Q": "q6_d_Y360_Q_wf",
            },
        },
        "q6_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_X360_I_wf",
                "Q": "q6_d_X360_Q_wf",
            },
        },
        "q6_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q6_d_mY90_I_wf",
                "Q": "q6_d_mY90_Q_wf",
            },
        },
        "q7_grft": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_X180": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_X360": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_Y360": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y360_Q_wf",
            },
        },
        "q7_X90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_mX90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_Y180": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y180_Q_wf",
            },
        },
        "q7_Y90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y90_Q_wf",
            },
        },
        "q7_mY90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_mY90_Q_wf",
            },
        },
        "q7_ro_pulse": {
            "operation": "measurement",
            "length": 4000,
            "waveforms": {
                "I": "q7_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr7",
                "integW_sin": "integW_sin_rr7",
                "integW_minus_sin": "integW_minus_sin_rr7",
            },
            "digital_marker": "ON",
        },
        "q7_d_X180": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_X180_I_wf",
                "Q": "q7_d_X180_Q_wf",
            },
        },
        "q7_d_X90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_X90_I_wf",
                "Q": "q7_d_X90_Q_wf",
            },
        },
        "q7_d_mX90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_mX90_I_wf",
                "Q": "q7_d_mX90_Q_wf",
            },
        },
        "q7_d_Y180": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_Y180_I_wf",
                "Q": "q7_d_Y180_Q_wf",
            },
        },
        "q7_d_Y90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_Y90_I_wf",
                "Q": "q7_d_Y90_Q_wf",
            },
        },
        "q7_d_Y360": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_Y360_I_wf",
                "Q": "q7_d_Y360_Q_wf",
            },
        },
        "q7_d_X360": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_X360_I_wf",
                "Q": "q7_d_X360_Q_wf",
            },
        },
        "q7_d_mY90": {
            "operation": "control",
            "length": 500,
            "waveforms": {
                "I": "q7_d_mY90_I_wf",
                "Q": "q7_d_mY90_Q_wf",
            },
        },
        "q8_grft": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_X180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_X360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_Y360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y360_Q_wf",
            },
        },
        "q8_X90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_mX90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_Y180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y180_Q_wf",
            },
        },
        "q8_Y90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y90_Q_wf",
            },
        },
        "q8_mY90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_mY90_Q_wf",
            },
        },
        "q8_ro_pulse": {
            "operation": "measurement",
            "length": 2000,
            "waveforms": {
                "I": "q8_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr8",
                "integW_sin": "integW_sin_rr8",
                "integW_minus_sin": "integW_minus_sin_rr8",
            },
            "digital_marker": "ON",
        },
        "q8_d_X180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_X180_I_wf",
                "Q": "q8_d_X180_Q_wf",
            },
        },
        "q8_d_X90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_X90_I_wf",
                "Q": "q8_d_X90_Q_wf",
            },
        },
        "q8_d_mX90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_mX90_I_wf",
                "Q": "q8_d_mX90_Q_wf",
            },
        },
        "q8_d_Y180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y180_I_wf",
                "Q": "q8_d_Y180_Q_wf",
            },
        },
        "q8_d_Y90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y90_I_wf",
                "Q": "q8_d_Y90_Q_wf",
            },
        },
        "q8_d_Y360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y360_I_wf",
                "Q": "q8_d_Y360_Q_wf",
            },
        },
        "q8_d_X360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_X360_I_wf",
                "Q": "q8_d_X360_Q_wf",
            },
        },
        "q8_d_mY90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_mY90_I_wf",
                "Q": "q8_d_mY90_Q_wf",
            },
        },
        "rise_pulse": {
            "operation": "control",
            "length": 16,
            "waveforms": {
                "I": "rise_wf",
                "Q": "zero_wf",
            },
        },
        "fall_pulse": {
            "operation": "control",
            "length": 16,
            "waveforms": {
                "I": "fall_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y180_Q_wf",
            },
        },
        "q12_1_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y90_Q_wf",
            },
        },
        "q12_1_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_mY90_Q_wf",
            },
        },
        "q12_2_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y180_Q_wf",
            },
        },
        "q12_2_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y90_Q_wf",
            },
        },
        "q12_2_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_mY90_Q_wf",
            },
        },
        "q12_3_grft": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_3_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_X180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_3_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_X360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_3_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_X90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_3_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_mX90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_3_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_Y180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y180_Q_wf",
            },
        },
        "q12_3_Y90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y90_Q_wf",
            },
        },
        "q12_3_mY90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_mY90_Q_wf",
            },
        },
        "q12_4_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y180_Q_wf",
            },
        },
        "q12_4_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y90_Q_wf",
            },
        },
        "q12_4_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_mY90_Q_wf",
            },
        },
        "q12_5_grft": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_5_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_X180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_5_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_X360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_5_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_X90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_5_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_mX90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_5_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_Y180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y180_Q_wf",
            },
        },
        "q12_5_Y90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y90_Q_wf",
            },
        },
        "q12_5_mY90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_mY90_Q_wf",
            },
        },
        "q12_6_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_6_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_6_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_6_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_6_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_6_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y180_Q_wf",
            },
        },
        "q12_6_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y90_Q_wf",
            },
        },
        "q12_6_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_mY90_Q_wf",
            },
        },
        "q12_7_grft": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_X180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_X360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_X90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_mX90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_Y180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y180_Q_wf",
            },
        },
        "q12_7_Y90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y90_Q_wf",
            },
        },
        "q12_7_mY90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_mY90_Q_wf",
            },
        },
        "q12_8_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y180_Q_wf",
            },
        },
        "q12_8_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y90_Q_wf",
            },
        },
        "q12_8_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_mY90_Q_wf",
            },
        },
        "stark_pulse": {
            "operation": "control",
            "length": 1000,
            "waveforms": {
                "I": "stark_wf",
                "Q": "zero_wf",
            },
        },
    },
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant",
            "sample": 0.4,
        },
        "q1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.001754498242547914+0j), (0.004769220690781325+0j), (0.01160077380536972+0j), (0.025250591495837534+0j), (0.04918143661320847+0j), (0.08571876843888207+0j), (0.13368900544319495+0j), (0.18657803709392473+0j), (0.23300777060530184+0j), (0.2603906268164547+0j)] + [(0.2640323948139477+0j)] * 32 + [(0.2603906268164547+0j), (0.23300777060530184+0j), (0.18657803709392473+0j), (0.13368900544319495+0j), (0.08571876843888207+0j), (0.04918143661320847+0j), (0.025250591495837534+0j), (0.01160077380536972+0j), (0.004769220690781325+0j), (0.001754498242547914+0j)],
        },
        "q1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q1_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0008360056467367242+0j), (0.0022724989580135894+0j), (0.0055276843103134144+0j), (0.01203172312290646+0j), (0.023434596699029586+0j), (0.04084436946608459+0j), (0.06370183836423844+0j), (0.08890307712195691+0j), (0.11102650731452524+0j), (0.12407423905978995+0j)] + [(0.12580951501286694+0j)] * 32 + [(0.12407423905978995+0j), (0.11102650731452524+0j), (0.08890307712195691+0j), (0.06370183836423844+0j), (0.04084436946608459+0j), (0.023434596699029586+0j), (0.01203172312290646+0j), (0.0055276843103134144+0j), (0.0022724989580135894+0j), (0.0008360056467367242+0j)],
        },
        "q1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0008360056467367242+0j), (-0.0022724989580135894+0j), (-0.0055276843103134144+0j), (-0.01203172312290646+0j), (-0.023434596699029586+0j), (-0.04084436946608459+0j), (-0.06370183836423844+0j), (-0.08890307712195691+0j), (-0.11102650731452524+0j), (-0.12407423905978995+0j)] + [(-0.12580951501286694+0j)] * 32 + [(-0.12407423905978995+0j), (-0.11102650731452524+0j), (-0.08890307712195691+0j), (-0.06370183836423844+0j), (-0.04084436946608459+0j), (-0.023434596699029586+0j), (-0.01203172312290646+0j), (-0.0055276843103134144+0j), (-0.0022724989580135894+0j), (-0.0008360056467367242+0j)],
        },
        "q1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.001754498242547914+0j), (0.004769220690781325+0j), (0.01160077380536972+0j), (0.025250591495837534+0j), (0.04918143661320847+0j), (0.08571876843888207+0j), (0.13368900544319495+0j), (0.18657803709392473+0j), (0.23300777060530184+0j), (0.2603906268164547+0j)] + [(0.2640323948139477+0j)] * 32 + [(0.2603906268164547+0j), (0.23300777060530184+0j), (0.18657803709392473+0j), (0.13368900544319495+0j), (0.08571876843888207+0j), (0.04918143661320847+0j), (0.025250591495837534+0j), (0.01160077380536972+0j), (0.004769220690781325+0j), (0.001754498242547914+0j)],
        },
        "q1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0008360056467367242+0j), (0.0022724989580135894+0j), (0.0055276843103134144+0j), (0.01203172312290646+0j), (0.023434596699029586+0j), (0.04084436946608459+0j), (0.06370183836423844+0j), (0.08890307712195691+0j), (0.11102650731452524+0j), (0.12407423905978995+0j)] + [(0.12580951501286694+0j)] * 32 + [(0.12407423905978995+0j), (0.11102650731452524+0j), (0.08890307712195691+0j), (0.06370183836423844+0j), (0.04084436946608459+0j), (0.023434596699029586+0j), (0.01203172312290646+0j), (0.0055276843103134144+0j), (0.0022724989580135894+0j), (0.0008360056467367242+0j)],
        },
        "q1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0008360056467367242+0j), (-0.0022724989580135894+0j), (-0.0055276843103134144+0j), (-0.01203172312290646+0j), (-0.023434596699029586+0j), (-0.04084436946608459+0j), (-0.06370183836423844+0j), (-0.08890307712195691+0j), (-0.11102650731452524+0j), (-0.12407423905978995+0j)] + [(-0.12580951501286694+0j)] * 32 + [(-0.12407423905978995+0j), (-0.11102650731452524+0j), (-0.08890307712195691+0j), (-0.06370183836423844+0j), (-0.04084436946608459+0j), (-0.023434596699029586+0j), (-0.01203172312290646+0j), (-0.0055276843103134144+0j), (-0.0022724989580135894+0j), (-0.0008360056467367242+0j)],
        },
        "q1_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.00040251623963611874+0j), (0.0004213313407659066+0j), (0.00044092469546678196+0j), (0.00046132329105599503+0j), (0.00048255479927748914+0j), (0.0005046475819741386+0j), (0.0005276306962116111+0j), (0.000551533898821395+0j), (0.000576387650330002+0j), (0.0006022231182408695+0j), (0.0006290721796350132+0j), (0.0006569674230560738+0j), (0.0006859421496450338+0j), (0.0007160303734895581+0j), (0.0007472668211526478+0j), (0.0007796869303450725+0j), (0.0008133268477059036+0j), (0.0008482234256553598+0j), (0.000884414218284159+0j), (0.0009219374762435797+0j), (0.0009608321406005604+0j), (0.001001137835622318+0j), (0.0010428948604552203+0j), (0.0010861441796629664+0j), (0.0011309274125895375+0j), (0.0011772868215128417+0j), (0.0012252652985555777+0j), (0.0012749063513204572+0j), (0.0013262540872176981+0j), (0.0013793531964535074+0j), (0.0014342489336492182+0j), (0.0014909870980617508+0j), (0.001549614012377179+0j), (0.0016101765000504122+0j), (0.001672721861165288+0j), (0.0017372978467908137+0j), (0.0018039526318107697+0j), (0.001872734786205532+0j), (0.0019436932447666644+0j), (0.002016877275226666+0j), (0.002092336444788167+0j), (0.0021701205850388917+0j), (0.002250279755240846+0j), (0.002332864203984379+0j), (0.0024179243292001594+0j), (0.0025055106365244446+0j), (0.0025956736960156485+0j), (0.002688464097222737+0j), (0.0027839324026087842+0j), (0.002882129099335756+0j), (0.0029831045494195445+0j), (0.0030869089382672345+0j), (0.0031935922216116395+0j), (0.0033032040708613304+0j), (0.0034157938168875796+0j), (0.003531410392272925+0j), (0.0036501022720494903+0j), (0.003771917412958515+0j), (0.00389690319126617+0j), (0.004025106339174149+0j), (0.004156572879867184+0j), (0.0042913480612432504+0j), (0.0044294762883758535+0j), (0.0045710010547615485+0j), (0.0047159648724094515+0j), (0.0048644092008333474+0j), (0.005016374375010626+0j), (0.005171899532376079+0j), (0.005331022538922282+0j), (0.0054937799144820065+0j), (0.005660206757271772+0j), (0.0058303366677793156+0j), (0.006004201672081349+0j), (0.006181832144681555+0j), (0.006363256730962206+0j), (0.006548502269346309+0j), (0.006737593713270448+0j), (0.006930554053071794+0j), (0.007127404237895912+0j), (0.007328163097735043+0j), (0.007532847265709499+0j), (0.007741471100707588+0j), (0.00795404661050222+0j), (0.008170583375464821+0j), (0.008391088472999627+0j), (0.00861556640282358+0j), (0.008844019013219176+0j), (0.009076445428389394+0j), (0.009312841977045601+0j), (0.00955320212236071+0j), (0.009797516393421237+0j), (0.010045772318312865+0j), (0.010297954358975046+0j), (0.01055404384796068+0j), (0.010814018927237367+0j), (0.01107785448916678+0j), (0.011345522119798598+0j), (0.011616990044615057+0j), (0.011892223076861535+0j), (0.012171182568597654+0j), (0.012453826364602145+0j), (0.012740108759263402+0j), (0.013029980456585726+0j), (0.013323388533439338+0j), (0.013620276406179943+0j), (0.013920583800760935+0j), (0.014224246726458544+0j), (0.014531197453326976+0j), (0.014841364493497175+0j), (0.015154672586429097+0j), (0.015471042688223293+0j), (0.01579039196509332+0j), (0.01611263379109591+0j), (0.016437677750210905+0j), (0.01676542964285788+0j), (0.017095791496930846+0j), (0.0174286615834269+0j), (0.017763934436738633+0j), (0.018101500879673965+0j), (0.018441248053260664+0j), (0.018783059451386155+0j), (0.01912681496031632+0j), (0.019472390903129907+0j), (0.019819660089097985+0j), (0.020168491868030162+0j), (0.020518752189601946+0j), (0.020870303667669513+0j), (0.02122300564957043+0j), (0.021576714290400496+0j), (0.02193128263224901+0j), (0.022286560688365965+0j), (0.022642395532226727+0j), (0.022998631391450846+0j), (0.02335510974652332+0j), (0.023711669434257975+0j), (0.02406814675593389+0j), (0.024424375590027303+0j), (0.02478018750945269+0j), (0.025135411903218143+0j), (0.025489876102391618+0j), (0.025843405510266128+0j), (0.026195823736603504+0j), (0.02654695273582813+0j), (0.026896612949033748+0j), (0.02724462344965848+0j), (0.02759080209267526+0j), (0.027934965667137254+0j), (0.028276930051910093+0j), (0.02861651037441575+0j), (0.02895352117220561+0j), (0.029287776557173486+0j), (0.029619090382212766+0j), (0.029947276410115728+0j), (0.030272148484506885+0j), (0.030593520702596688+0j), (0.03091120758953652+0j), (0.031225024274151008+0j), (0.031534786665818944+0j), (0.031840311632269885+0j), (0.032141417178059746+0j), (0.03243792262348501+0j), (0.0327296487836923+0j), (0.03301641814773737+0j), (0.03329805505734528+0j), (0.033574385885121835+0j), (0.033845239211964966+0j), (0.03411044600342398+0j), (0.034369839784753865+0j), (0.03462325681441241+0j), (0.034870536255747764+0j), (0.03511152034662558+0j), (0.035346054566745985+0j), (0.03557398780240272+0j), (0.03579517250843906+0j), (0.036009464867158024+0j), (0.03621672494394776+0j), (0.03641681683938664+0j), (0.03660960883759693+0j), (0.03679497355062062+0j), (0.03697278805859595+0j), (0.037142934045519+0j), (0.0373052979303805+0j), (0.03745977099347446+0j), (0.037606249497682154+0j), (0.03774463480454201+0j), (0.03787483348492375+0j), (0.03799675742413297+0j), (0.03811032392128052+0j), (0.03821545578276005+0j), (0.03831208140968567+0j), (0.038400134879151185+0j), (0.03847955601918161+0j), (0.03855029047725805+0j), (0.038612289782306276+0j), (0.03866551140005032+0j), (0.038709918781642524+0j), (0.038745481405492124+0j), (0.0387721748122255+0j), (0.03878998063272192+0j), (0.038798886609179815+0j)] + [(0.0388+0j)] * 2640 + [(0.038798886609179815+0j), (0.03878998063272192+0j), (0.0387721748122255+0j), (0.038745481405492124+0j), (0.038709918781642524+0j), (0.03866551140005032+0j), (0.038612289782306276+0j), (0.03855029047725805+0j), (0.03847955601918161+0j), (0.038400134879151185+0j), (0.03831208140968567+0j), (0.03821545578276005+0j), (0.03811032392128052+0j), (0.03799675742413297+0j), (0.03787483348492375+0j), (0.03774463480454201+0j), (0.037606249497682154+0j), (0.03745977099347446+0j), (0.0373052979303805+0j), (0.037142934045519+0j), (0.03697278805859595+0j), (0.03679497355062062+0j), (0.03660960883759693+0j), (0.03641681683938664+0j), (0.03621672494394776+0j), (0.036009464867158024+0j), (0.03579517250843906+0j), (0.03557398780240272+0j), (0.035346054566745985+0j), (0.03511152034662558+0j), (0.034870536255747764+0j), (0.03462325681441241+0j), (0.034369839784753865+0j), (0.03411044600342398+0j), (0.033845239211964966+0j), (0.033574385885121835+0j), (0.03329805505734528+0j), (0.03301641814773737+0j), (0.0327296487836923+0j), (0.03243792262348501+0j), (0.032141417178059746+0j), (0.031840311632269885+0j), (0.031534786665818944+0j), (0.031225024274151008+0j), (0.03091120758953652+0j), (0.030593520702596688+0j), (0.030272148484506885+0j), (0.029947276410115728+0j), (0.029619090382212766+0j), (0.029287776557173486+0j), (0.02895352117220561+0j), (0.02861651037441575+0j), (0.028276930051910093+0j), (0.027934965667137254+0j), (0.02759080209267526+0j), (0.02724462344965848+0j), (0.026896612949033748+0j), (0.02654695273582813+0j), (0.026195823736603504+0j), (0.025843405510266128+0j), (0.025489876102391618+0j), (0.025135411903218143+0j), (0.02478018750945269+0j), (0.024424375590027303+0j), (0.02406814675593389+0j), (0.023711669434257975+0j), (0.02335510974652332+0j), (0.022998631391450846+0j), (0.022642395532226727+0j), (0.022286560688365965+0j), (0.02193128263224901+0j), (0.021576714290400496+0j), (0.02122300564957043+0j), (0.020870303667669513+0j), (0.020518752189601946+0j), (0.020168491868030162+0j), (0.019819660089097985+0j), (0.019472390903129907+0j), (0.01912681496031632+0j), (0.018783059451386155+0j), (0.018441248053260664+0j), (0.018101500879673965+0j), (0.017763934436738633+0j), (0.0174286615834269+0j), (0.017095791496930846+0j), (0.01676542964285788+0j), (0.016437677750210905+0j), (0.01611263379109591+0j), (0.01579039196509332+0j), (0.015471042688223293+0j), (0.015154672586429097+0j), (0.014841364493497175+0j), (0.014531197453326976+0j), (0.014224246726458544+0j), (0.013920583800760935+0j), (0.013620276406179943+0j), (0.013323388533439338+0j), (0.013029980456585726+0j), (0.012740108759263402+0j), (0.012453826364602145+0j), (0.012171182568597654+0j), (0.011892223076861535+0j), (0.011616990044615057+0j), (0.011345522119798598+0j), (0.01107785448916678+0j), (0.010814018927237367+0j), (0.01055404384796068+0j), (0.010297954358975046+0j), (0.010045772318312865+0j), (0.009797516393421237+0j), (0.00955320212236071+0j), (0.009312841977045601+0j), (0.009076445428389394+0j), (0.008844019013219176+0j), (0.00861556640282358+0j), (0.008391088472999627+0j), (0.008170583375464821+0j), (0.00795404661050222+0j), (0.007741471100707588+0j), (0.007532847265709499+0j), (0.007328163097735043+0j), (0.007127404237895912+0j), (0.006930554053071794+0j), (0.006737593713270448+0j), (0.006548502269346309+0j), (0.006363256730962206+0j), (0.006181832144681555+0j), (0.006004201672081349+0j), (0.0058303366677793156+0j), (0.005660206757271772+0j), (0.0054937799144820065+0j), (0.005331022538922282+0j), (0.005171899532376079+0j), (0.005016374375010626+0j), (0.0048644092008333474+0j), (0.0047159648724094515+0j), (0.0045710010547615485+0j), (0.0044294762883758535+0j), (0.0042913480612432504+0j), (0.004156572879867184+0j), (0.004025106339174149+0j), (0.00389690319126617+0j), (0.003771917412958515+0j), (0.0036501022720494903+0j), (0.003531410392272925+0j), (0.0034157938168875796+0j), (0.0033032040708613304+0j), (0.0031935922216116395+0j), (0.0030869089382672345+0j), (0.0029831045494195445+0j), (0.002882129099335756+0j), (0.0027839324026087842+0j), (0.002688464097222737+0j), (0.0025956736960156485+0j), (0.0025055106365244446+0j), (0.0024179243292001594+0j), (0.002332864203984379+0j), (0.002250279755240846+0j), (0.0021701205850388917+0j), (0.002092336444788167+0j), (0.002016877275226666+0j), (0.0019436932447666644+0j), (0.001872734786205532+0j), (0.0018039526318107697+0j), (0.0017372978467908137+0j), (0.001672721861165288+0j), (0.0016101765000504122+0j), (0.001549614012377179+0j), (0.0014909870980617508+0j), (0.0014342489336492182+0j), (0.0013793531964535074+0j), (0.0013262540872176981+0j), (0.0012749063513204572+0j), (0.0012252652985555777+0j), (0.0011772868215128417+0j), (0.0011309274125895375+0j), (0.0010861441796629664+0j), (0.0010428948604552203+0j), (0.001001137835622318+0j), (0.0009608321406005604+0j), (0.0009219374762435797+0j), (0.000884414218284159+0j), (0.0008482234256553598+0j), (0.0008133268477059036+0j), (0.0007796869303450725+0j), (0.0007472668211526478+0j), (0.0007160303734895581+0j), (0.0006859421496450338+0j), (0.0006569674230560738+0j), (0.0006290721796350132+0j), (0.0006022231182408695+0j), (0.000576387650330002+0j), (0.000551533898821395+0j), (0.0005276306962116111+0j), (0.0005046475819741386+0j), (0.00048255479927748914+0j), (0.00046132329105599503+0j), (0.00044092469546678196+0j), (0.0004213313407659066+0j), (0.00040251623963611874+0j)],
        },
        "q1_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001754498242547914, 0.004769220690781325, 0.01160077380536972, 0.025250591495837534, 0.04918143661320847, 0.08571876843888207, 0.13368900544319495, 0.18657803709392473, 0.23300777060530184, 0.2603906268164547] + [0.2640323948139477] * 32 + [0.2603906268164547, 0.23300777060530184, 0.18657803709392473, 0.13368900544319495, 0.08571876843888207, 0.04918143661320847, 0.025250591495837534, 0.01160077380536972, 0.004769220690781325, 0.001754498242547914],
        },
        "q1_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008006671084744846, -0.001947340025125666, -0.004179493628177615, -0.00788424947310757, -0.01299389476587147, -0.018529507730236556, -0.02247704328734932, -0.022406600636444715, -0.016789474717797813, -0.006254186050432826] + [0.0] * 32 + [0.006254186050432826, 0.016789474717797813, 0.022406600636444715, 0.02247704328734932, 0.018529507730236556, 0.01299389476587147, 0.00788424947310757, 0.004179493628177615, 0.001947340025125666, 0.0008006671084744846],
        },
        "q1_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008360056467367242, 0.0022724989580135894, 0.0055276843103134144, 0.01203172312290646, 0.023434596699029586, 0.04084436946608459, 0.06370183836423844, 0.08890307712195691, 0.11102650731452524, 0.12407423905978995] + [0.12580951501286694] * 32 + [0.12407423905978995, 0.11102650731452524, 0.08890307712195691, 0.06370183836423844, 0.04084436946608459, 0.023434596699029586, 0.01203172312290646, 0.0055276843103134144, 0.0022724989580135894, 0.0008360056467367242],
        },
        "q1_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000381512051484859, -0.0009278933530063265, -0.001991498303573379, -0.00375678750765062, -0.006191496311558518, -0.00882917561161735, -0.01071014758206955, -0.010676582171458575, -0.008000062541777738, -0.002980074147188042] + [0.0] * 32 + [0.002980074147188042, 0.008000062541777738, 0.010676582171458575, 0.01071014758206955, 0.00882917561161735, 0.006191496311558518, 0.00375678750765062, 0.001991498303573379, 0.0009278933530063265, 0.000381512051484859],
        },
        "q1_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008360056467367242, -0.0022724989580135894, -0.0055276843103134144, -0.01203172312290646, -0.023434596699029586, -0.04084436946608459, -0.06370183836423844, -0.08890307712195691, -0.11102650731452524, -0.12407423905978995] + [-0.12580951501286694] * 32 + [-0.12407423905978995, -0.11102650731452524, -0.08890307712195691, -0.06370183836423844, -0.04084436946608459, -0.023434596699029586, -0.01203172312290646, -0.0055276843103134144, -0.0022724989580135894, -0.0008360056467367242],
        },
        "q1_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000381512051484859, 0.0009278933530063265, 0.001991498303573379, 0.00375678750765062, 0.006191496311558518, 0.00882917561161735, 0.01071014758206955, 0.010676582171458575, 0.008000062541777738, 0.002980074147188042] + [0.0] * 32 + [-0.002980074147188042, -0.008000062541777738, -0.010676582171458575, -0.01071014758206955, -0.00882917561161735, -0.006191496311558518, -0.00375678750765062, -0.001991498303573379, -0.0009278933530063265, -0.000381512051484859],
        },
        "q1_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008006671084744846, 0.001947340025125666, 0.004179493628177615, 0.00788424947310757, 0.01299389476587147, 0.018529507730236556, 0.02247704328734932, 0.022406600636444715, 0.016789474717797813, 0.006254186050432826] + [0.0] * 32 + [-0.006254186050432826, -0.016789474717797813, -0.022406600636444715, -0.02247704328734932, -0.018529507730236556, -0.01299389476587147, -0.00788424947310757, -0.004179493628177615, -0.001947340025125666, -0.0008006671084744846],
        },
        "q1_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001754498242547914, 0.004769220690781325, 0.01160077380536972, 0.025250591495837534, 0.04918143661320847, 0.08571876843888207, 0.13368900544319495, 0.18657803709392473, 0.23300777060530184, 0.2603906268164547] + [0.2640323948139477] * 32 + [0.2603906268164547, 0.23300777060530184, 0.18657803709392473, 0.13368900544319495, 0.08571876843888207, 0.04918143661320847, 0.025250591495837534, 0.01160077380536972, 0.004769220690781325, 0.001754498242547914],
        },
        "q1_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.000381512051484859, 0.0009278933530063265, 0.001991498303573379, 0.00375678750765062, 0.006191496311558518, 0.00882917561161735, 0.01071014758206955, 0.010676582171458575, 0.008000062541777738, 0.002980074147188042] + [0.0] * 32 + [-0.002980074147188042, -0.008000062541777738, -0.010676582171458575, -0.01071014758206955, -0.00882917561161735, -0.006191496311558518, -0.00375678750765062, -0.001991498303573379, -0.0009278933530063265, -0.000381512051484859],
        },
        "q1_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008360056467367242, 0.0022724989580135894, 0.0055276843103134144, 0.01203172312290646, 0.023434596699029586, 0.04084436946608459, 0.06370183836423844, 0.08890307712195691, 0.11102650731452524, 0.12407423905978995] + [0.12580951501286694] * 32 + [0.12407423905978995, 0.11102650731452524, 0.08890307712195691, 0.06370183836423844, 0.04084436946608459, 0.023434596699029586, 0.01203172312290646, 0.0055276843103134144, 0.0022724989580135894, 0.0008360056467367242],
        },
        "q1_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 32 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
        },
        "q1_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q1_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q1_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 32 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
        },
        "q1_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.000381512051484859, -0.0009278933530063265, -0.001991498303573379, -0.00375678750765062, -0.006191496311558518, -0.00882917561161735, -0.01071014758206955, -0.010676582171458575, -0.008000062541777738, -0.002980074147188042] + [0.0] * 32 + [0.002980074147188042, 0.008000062541777738, 0.010676582171458575, 0.01071014758206955, 0.00882917561161735, 0.006191496311558518, 0.00375678750765062, 0.001991498303573379, 0.0009278933530063265, 0.000381512051484859],
        },
        "q1_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008360056467367242, -0.0022724989580135894, -0.0055276843103134144, -0.01203172312290646, -0.023434596699029586, -0.04084436946608459, -0.06370183836423844, -0.08890307712195691, -0.11102650731452524, -0.12407423905978995] + [-0.12580951501286694] * 32 + [-0.12407423905978995, -0.11102650731452524, -0.08890307712195691, -0.06370183836423844, -0.04084436946608459, -0.023434596699029586, -0.01203172312290646, -0.0055276843103134144, -0.0022724989580135894, -0.0008360056467367242],
        },
        "q2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0011425919097940382+0j), (0.0031058868257374506+0j), (0.007554838173059075+0j), (0.016444086896752877+0j), (0.03202870782286673+0j), (0.055823123079076255+0j), (0.08706305446392269+0j), (0.12150628057579745+0j), (0.15174298107368572+0j), (0.16957567489757952+0j)] + [(0.17194732426739567+0j)] * 32 + [(0.16957567489757952+0j), (0.15174298107368572+0j), (0.12150628057579745+0j), (0.08706305446392269+0j), (0.055823123079076255+0j), (0.03202870782286673+0j), (0.016444086896752877+0j), (0.007554838173059075+0j), (0.0031058868257374506+0j), (0.0011425919097940382+0j)],
        },
        "q2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q2_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005687802792877164+0j), (0.00154610509757366+0j), (0.00376078539434138+0j), (0.00818583805608474+0j), (0.01594383543639708+0j), (0.02778865425482748+0j), (0.04333983814269958+0j), (0.06048561661317156+0j), (0.07553739389822868+0j), (0.08441447808433584+0j)] + [(0.08559508104447734+0j)] * 32 + [(0.08441447808433584+0j), (0.07553739389822868+0j), (0.06048561661317156+0j), (0.04333983814269958+0j), (0.02778865425482748+0j), (0.01594383543639708+0j), (0.00818583805608474+0j), (0.00376078539434138+0j), (0.00154610509757366+0j), (0.0005687802792877164+0j)],
        },
        "q2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005687802792877164+0j), (-0.00154610509757366+0j), (-0.00376078539434138+0j), (-0.00818583805608474+0j), (-0.01594383543639708+0j), (-0.02778865425482748+0j), (-0.04333983814269958+0j), (-0.06048561661317156+0j), (-0.07553739389822868+0j), (-0.08441447808433584+0j)] + [(-0.08559508104447734+0j)] * 32 + [(-0.08441447808433584+0j), (-0.07553739389822868+0j), (-0.06048561661317156+0j), (-0.04333983814269958+0j), (-0.02778865425482748+0j), (-0.01594383543639708+0j), (-0.00818583805608474+0j), (-0.00376078539434138+0j), (-0.00154610509757366+0j), (-0.0005687802792877164+0j)],
        },
        "q2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.001142759621501325+0j), (0.0031063427134237877+0j), (0.007555947085871618+0j), (0.016446500589572324+0j), (0.03203340905453581+0j), (0.055831316898056954+0j), (0.08707583373654014+0j), (0.1215241154874459+0j), (0.15176525418292666+0j), (0.1696005655218764+0j)] + [(0.17197256300667702+0j)] * 32 + [(0.1696005655218764+0j), (0.15176525418292666+0j), (0.1215241154874459+0j), (0.08707583373654014+0j), (0.055831316898056954+0j), (0.03203340905453581+0j), (0.016446500589572324+0j), (0.007555947085871618+0j), (0.0031063427134237877+0j), (0.001142759621501325+0j)],
        },
        "q2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005691157027022902+0j), (0.0015470168729463355+0j), (0.003763003219966468+0j), (0.008190665441723633+0j), (0.015953237899735254+0j), (0.0278050418927889+0j), (0.04336539668793448+0j), (0.06052128643646852+0j), (0.07558194011671057+0j), (0.0844642593329297+0j)] + [(0.08564555852304008+0j)] * 32 + [(0.0844642593329297+0j), (0.07558194011671057+0j), (0.06052128643646852+0j), (0.04336539668793448+0j), (0.0278050418927889+0j), (0.015953237899735254+0j), (0.008190665441723633+0j), (0.003763003219966468+0j), (0.0015470168729463355+0j), (0.0005691157027022902+0j)],
        },
        "q2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005691157027022902+0j), (-0.0015470168729463355+0j), (-0.003763003219966468+0j), (-0.008190665441723633+0j), (-0.015953237899735254+0j), (-0.0278050418927889+0j), (-0.04336539668793448+0j), (-0.06052128643646852+0j), (-0.07558194011671057+0j), (-0.0844642593329297+0j)] + [(-0.08564555852304008+0j)] * 32 + [(-0.0844642593329297+0j), (-0.07558194011671057+0j), (-0.06052128643646852+0j), (-0.04336539668793448+0j), (-0.0278050418927889+0j), (-0.015953237899735254+0j), (-0.008190665441723633+0j), (-0.003763003219966468+0j), (-0.0015470168729463355+0j), (-0.0005691157027022902+0j)],
        },
        "q2_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0029047563685080727+0j), (0.0030405354488261295+0j), (0.003181930792028323+0j), (0.0033291371519504794+0j), (0.0034823542215901273+0j), (0.0036417866740401745+0j), (0.0038076441994652345+0j), (0.003980141537886355+0j), (0.004159498507536096+0j), (0.004345940028542356+0j), (0.004539696141695971+0j), (0.004741002022054141+0j), (0.004950097987129109+0j), (0.005167229499409181+0j), (0.005392647162957252+0j), (0.005626606713830419+0j), (0.00586936900406322+0j), (0.006121199978956203+0j), (0.006382370647411455+0j), (0.006653157045056759+0j), (0.00693384018990095+0j), (0.007224706030264148+0j), (0.007526045384728393+0j), (0.007838153873856458+0j), (0.008161331843429652+0j), (0.00849588427895865+0j), (0.008842120711225818+0j), (0.009200355112621855+0j), (0.009570905784045243+0j), (0.00995409523213871+0j), (0.01035025003664384+0j), (0.010759700707662117+0j), (0.011182781532618816+0j), (0.011619830412734932+0j), (0.012071188688821665+0j), (0.012537200956222365+0j), (0.013018214868737511+0j), (0.013514580931380126+0j), (0.014026652281821287+0j), (0.014554784460398616+0j), (0.015099335168574398+0j), (0.015660664015744577+0j), (0.01623913225431538+0j), (0.01683510250298005+0j), (0.017448938458145477+0j), (0.01808100459347537+0j), (0.018731665847535606+0j), (0.019401287299545524+0j), (0.020090233833259263+0j), (0.020798869789020916+0j), (0.021527558604058566+0j), (0.02227666244110375+0j), (0.02304654180544482+0j), (0.02383755515054568+0j), (0.024650058472384592+0j), (0.02548440489269121+0j), (0.026340944231284975+0j), (0.027220022567741857+0j), (0.028121981792642463+0j), (0.029047159148679422+0j), (0.02999588676192813+0j), (0.03096849116361108+0j), (0.03196529280271234+0j), (0.032986605549825604+0j), (0.03403273619264552+0j), (0.03510398392353962+0j), (0.03620063981966431+0j), (0.037322986316116025+0j), (0.038471296672635026+0j), (0.039645834434406224+0j), (0.04084685288752825+0j), (0.04207459450974763+0j), (0.043329290417081896+0j), (0.044611159806980286+0j), (0.04592040939869633+0j), (0.04725723287157129+0j), (0.04862181030195168+0j), (0.05001430759948717+0j), (0.051434875943578734+0j), (0.05288365122076834+0j), (0.05436075346388297+0j), (0.05586628629376609+0j), (0.057400336364448995+0j), (0.05896297281263273+0j), (0.06055424671236844+0j), (0.06217419053584025+0j), (0.0638228176211693+0j), (0.06550012164817087+0j), (0.06720607612300948+0j), (0.06894063387270614+0j), (0.07070372655046253+0j), (0.07249526415277324+0j), (0.07431513454930445+0j), (0.07616320302652035+0j), (0.07803931184604285+0j), (0.07994327981872933+0j), (0.0818749018954538+0j), (0.08383394877557256+0j), (0.0858201665340523+0j), (0.08783327626823048+0j), (0.0898729737651701+0j), (0.09193892919056063+0j), (0.09403078680010317+0j), (0.0961481646743045+0j), (0.0982906544775872+0j), (0.10045782124260468+0j), (0.10264920318062866+0j), (0.10486431151885445+0j), (0.10710263036544351+0j), (0.10936361660309657+0j), (0.11164669981192066+0j), (0.1139512822223229+0j), (0.11627673869863024+0j), (0.11862241675409929+0j), (0.12098763659794344+0j), (0.12337169121496486+0j), (0.12577384647833845+0j), (0.12819334129605198+0j), (0.13062938779146158+0j), (0.13308117151837592+0j), (0.1355478517110341+0j), (0.138028561569293+0j), (0.14052240857928797+0j), (0.14302847486977924+0j), (0.14554581760434135+0j), (0.14807346940949856+0j), (0.15061043883885214+0j), (0.15315571087318863+0j), (0.15570824745649842+0j), (0.15826698806777634+0j), (0.16083085032841415+0j), (0.16339873064493513+0j), (0.16596950488675866+0j), (0.16854202909862187+0j), (0.1711151402472225+0j), (0.17368765700158476+0j), (0.17625838054658877+0j), (0.17882609542904002+0j), (0.1813895704355948+0j), (0.18394755950179517+0j), (0.186498802651405+0j), (0.18904202696517988+0j), (0.19157594757814111+0j), (0.19409926870436722+0j), (0.19661068468825704+0j), (0.19910888108116165+0j), (0.2015925357422276+0j), (0.20406031996223775+0j), (0.20651089960918578+0j), (0.20894293629426727+0j), (0.21135508855692203+0j), (0.21374601306751478+0j), (0.21611436584619595+0j), (0.21845880349644142+0j), (0.22077798445172866+0j), (0.22307057023376867+0j), (0.22533522672067735+0j), (0.22757062542343565+0j), (0.2297754447689579+0j), (0.23194837138806+0j), (0.2340881014065928+0j), (0.23619334173798565+0j), (0.2382628113754243+0j), (0.24029524268187313+0j), (0.24228938267613692+0j), (0.24424399431314922+0j), (0.24615785775666785+0j), (0.24802977164255363+0j), (0.24985855433081117+0j), (0.2516430451445715+0j), (0.2533821055942052+0j), (0.2550746205847648+0j), (0.2567194996049681+0j), (0.25831567789595195+0j), (0.25986211759804756+0j), (0.26135780887384974+0j), (0.2628017710058829+0j), (0.2641930534671943+0j), (0.2655307369632416+0j), (0.2668139344434759+0j), (0.2680417920810649+0j), (0.2692134902192407+0j), (0.27032824428280533+0j), (0.2713853056533763+0j), (0.27238396250700414+0j), (0.2733235406128518+0j), (0.2742034040916812+0j), (0.27502295613295213+0j), (0.27578163966940233+0j), (0.2764789380080409+0j), (0.27711437541655487+0j), (0.2776875176641972+0j), (0.2781979725162952+0j), (0.2786453901815916+0j), (0.27902946371170334+0j), (0.27934992935205943+0j), (0.27960656684375756+0j), (0.27979919967585415+0j), (0.2799276952876839+0j), (0.2799919652208852+0j)] + [(0.27999999999999997+0j)] * 9600 + [(0.2799919652208852+0j), (0.2799276952876839+0j), (0.27979919967585415+0j), (0.27960656684375756+0j), (0.27934992935205943+0j), (0.27902946371170334+0j), (0.2786453901815916+0j), (0.2781979725162952+0j), (0.2776875176641972+0j), (0.27711437541655487+0j), (0.2764789380080409+0j), (0.27578163966940233+0j), (0.27502295613295213+0j), (0.2742034040916812+0j), (0.2733235406128518+0j), (0.27238396250700414+0j), (0.2713853056533763+0j), (0.27032824428280533+0j), (0.2692134902192407+0j), (0.2680417920810649+0j), (0.2668139344434759+0j), (0.2655307369632416+0j), (0.2641930534671943+0j), (0.2628017710058829+0j), (0.26135780887384974+0j), (0.25986211759804756+0j), (0.25831567789595195+0j), (0.2567194996049681+0j), (0.2550746205847648+0j), (0.2533821055942052+0j), (0.2516430451445715+0j), (0.24985855433081117+0j), (0.24802977164255363+0j), (0.24615785775666785+0j), (0.24424399431314922+0j), (0.24228938267613692+0j), (0.24029524268187313+0j), (0.2382628113754243+0j), (0.23619334173798565+0j), (0.2340881014065928+0j), (0.23194837138806+0j), (0.2297754447689579+0j), (0.22757062542343565+0j), (0.22533522672067735+0j), (0.22307057023376867+0j), (0.22077798445172866+0j), (0.21845880349644142+0j), (0.21611436584619595+0j), (0.21374601306751478+0j), (0.21135508855692203+0j), (0.20894293629426727+0j), (0.20651089960918578+0j), (0.20406031996223775+0j), (0.2015925357422276+0j), (0.19910888108116165+0j), (0.19661068468825704+0j), (0.19409926870436722+0j), (0.19157594757814111+0j), (0.18904202696517988+0j), (0.186498802651405+0j), (0.18394755950179517+0j), (0.1813895704355948+0j), (0.17882609542904002+0j), (0.17625838054658877+0j), (0.17368765700158476+0j), (0.1711151402472225+0j), (0.16854202909862187+0j), (0.16596950488675866+0j), (0.16339873064493513+0j), (0.16083085032841415+0j), (0.15826698806777634+0j), (0.15570824745649842+0j), (0.15315571087318863+0j), (0.15061043883885214+0j), (0.14807346940949856+0j), (0.14554581760434135+0j), (0.14302847486977924+0j), (0.14052240857928797+0j), (0.138028561569293+0j), (0.1355478517110341+0j), (0.13308117151837592+0j), (0.13062938779146158+0j), (0.12819334129605198+0j), (0.12577384647833845+0j), (0.12337169121496486+0j), (0.12098763659794344+0j), (0.11862241675409929+0j), (0.11627673869863024+0j), (0.1139512822223229+0j), (0.11164669981192066+0j), (0.10936361660309657+0j), (0.10710263036544351+0j), (0.10486431151885445+0j), (0.10264920318062866+0j), (0.10045782124260468+0j), (0.0982906544775872+0j), (0.0961481646743045+0j), (0.09403078680010317+0j), (0.09193892919056063+0j), (0.0898729737651701+0j), (0.08783327626823048+0j), (0.0858201665340523+0j), (0.08383394877557256+0j), (0.0818749018954538+0j), (0.07994327981872933+0j), (0.07803931184604285+0j), (0.07616320302652035+0j), (0.07431513454930445+0j), (0.07249526415277324+0j), (0.07070372655046253+0j), (0.06894063387270614+0j), (0.06720607612300948+0j), (0.06550012164817087+0j), (0.0638228176211693+0j), (0.06217419053584025+0j), (0.06055424671236844+0j), (0.05896297281263273+0j), (0.057400336364448995+0j), (0.05586628629376609+0j), (0.05436075346388297+0j), (0.05288365122076834+0j), (0.051434875943578734+0j), (0.05001430759948717+0j), (0.04862181030195168+0j), (0.04725723287157129+0j), (0.04592040939869633+0j), (0.044611159806980286+0j), (0.043329290417081896+0j), (0.04207459450974763+0j), (0.04084685288752825+0j), (0.039645834434406224+0j), (0.038471296672635026+0j), (0.037322986316116025+0j), (0.03620063981966431+0j), (0.03510398392353962+0j), (0.03403273619264552+0j), (0.032986605549825604+0j), (0.03196529280271234+0j), (0.03096849116361108+0j), (0.02999588676192813+0j), (0.029047159148679422+0j), (0.028121981792642463+0j), (0.027220022567741857+0j), (0.026340944231284975+0j), (0.02548440489269121+0j), (0.024650058472384592+0j), (0.02383755515054568+0j), (0.02304654180544482+0j), (0.02227666244110375+0j), (0.021527558604058566+0j), (0.020798869789020916+0j), (0.020090233833259263+0j), (0.019401287299545524+0j), (0.018731665847535606+0j), (0.01808100459347537+0j), (0.017448938458145477+0j), (0.01683510250298005+0j), (0.01623913225431538+0j), (0.015660664015744577+0j), (0.015099335168574398+0j), (0.014554784460398616+0j), (0.014026652281821287+0j), (0.013514580931380126+0j), (0.013018214868737511+0j), (0.012537200956222365+0j), (0.012071188688821665+0j), (0.011619830412734932+0j), (0.011182781532618816+0j), (0.010759700707662117+0j), (0.01035025003664384+0j), (0.00995409523213871+0j), (0.009570905784045243+0j), (0.009200355112621855+0j), (0.008842120711225818+0j), (0.00849588427895865+0j), (0.008161331843429652+0j), (0.007838153873856458+0j), (0.007526045384728393+0j), (0.007224706030264148+0j), (0.00693384018990095+0j), (0.006653157045056759+0j), (0.006382370647411455+0j), (0.006121199978956203+0j), (0.00586936900406322+0j), (0.005626606713830419+0j), (0.005392647162957252+0j), (0.005167229499409181+0j), (0.004950097987129109+0j), (0.004741002022054141+0j), (0.004539696141695971+0j), (0.004345940028542356+0j), (0.004159498507536096+0j), (0.003980141537886355+0j), (0.0038076441994652345+0j), (0.0036417866740401745+0j), (0.0034823542215901273+0j), (0.0033291371519504794+0j), (0.003181930792028323+0j), (0.0030405354488261295+0j), (0.0029047563685080727+0j)],
        },
        "q2_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0011425919097940382, 0.0031058868257374506, 0.007554838173059075, 0.016444086896752877, 0.03202870782286673, 0.055823123079076255, 0.08706305446392269, 0.12150628057579745, 0.15174298107368572, 0.16957567489757952] + [0.17194732426739567] * 32 + [0.16957567489757952, 0.15174298107368572, 0.12150628057579745, 0.08706305446392269, 0.055823123079076255, 0.03202870782286673, 0.016444086896752877, 0.007554838173059075, 0.0031058868257374506, 0.0011425919097940382],
        },
        "q2_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0006442181330182332, -0.0015668331345949302, -0.0033628277640082283, -0.006343680690833834, -0.010454910084484717, -0.01490887379957899, -0.018085067700526924, -0.01802838942241321, -0.013508840244061574, -0.005032128856442101] + [0.0] * 32 + [0.005032128856442101, 0.013508840244061574, 0.01802838942241321, 0.018085067700526924, 0.01490887379957899, 0.010454910084484717, 0.006343680690833834, 0.0033628277640082283, 0.0015668331345949302, 0.0006442181330182332],
        },
        "q2_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005687802792877164, 0.00154610509757366, 0.00376078539434138, 0.00818583805608474, 0.01594383543639708, 0.02778865425482748, 0.04333983814269958, 0.06048561661317156, 0.07553739389822868, 0.08441447808433584] + [0.08559508104447734] * 32 + [0.08441447808433584, 0.07553739389822868, 0.06048561661317156, 0.04333983814269958, 0.02778865425482748, 0.01594383543639708, 0.00818583805608474, 0.00376078539434138, 0.00154610509757366, 0.0005687802792877164],
        },
        "q2_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00032069067396632616, -0.0007799668282727434, -0.0016740098528737779, -0.0031578732915192465, -0.005204436183040273, -0.007421611627828192, -0.009002715466011987, -0.008974501117057884, -0.006724677341935242, -0.0025049850535829947] + [0.0] * 32 + [0.0025049850535829947, 0.006724677341935242, 0.008974501117057884, 0.009002715466011987, 0.007421611627828192, 0.005204436183040273, 0.0031578732915192465, 0.0016740098528737779, 0.0007799668282727434, 0.00032069067396632616],
        },
        "q2_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005687802792877164, -0.00154610509757366, -0.00376078539434138, -0.00818583805608474, -0.01594383543639708, -0.02778865425482748, -0.04333983814269958, -0.06048561661317156, -0.07553739389822868, -0.08441447808433584] + [-0.08559508104447734] * 32 + [-0.08441447808433584, -0.07553739389822868, -0.06048561661317156, -0.04333983814269958, -0.02778865425482748, -0.01594383543639708, -0.00818583805608474, -0.00376078539434138, -0.00154610509757366, -0.0005687802792877164],
        },
        "q2_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00032069067396632616, 0.0007799668282727434, 0.0016740098528737779, 0.0031578732915192465, 0.005204436183040273, 0.007421611627828192, 0.009002715466011987, 0.008974501117057884, 0.006724677341935242, 0.0025049850535829947] + [0.0] * 32 + [-0.0025049850535829947, -0.006724677341935242, -0.008974501117057884, -0.009002715466011987, -0.007421611627828192, -0.005204436183040273, -0.0031578732915192465, -0.0016740098528737779, -0.0007799668282727434, -0.00032069067396632616],
        },
        "q2_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006443126925210857, 0.001567063117196578, 0.00336332136595025, 0.006344611827760344, 0.010456444675098188, 0.014911062151043075, 0.018087722259477017, 0.01803103566202312, 0.013510823096067943, 0.0050328674814179705] + [0.0] * 32 + [-0.0050328674814179705, -0.013510823096067943, -0.01803103566202312, -0.018087722259477017, -0.014911062151043075, -0.010456444675098188, -0.006344611827760344, -0.00336332136595025, -0.001567063117196578, -0.0006443126925210857],
        },
        "q2_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001142759621501325, 0.0031063427134237877, 0.007555947085871618, 0.016446500589572324, 0.03203340905453581, 0.055831316898056954, 0.08707583373654014, 0.1215241154874459, 0.15176525418292666, 0.1696005655218764] + [0.17197256300667702] * 32 + [0.1696005655218764, 0.15176525418292666, 0.1215241154874459, 0.08707583373654014, 0.055831316898056954, 0.03203340905453581, 0.016446500589572324, 0.007555947085871618, 0.0031063427134237877, 0.001142759621501325],
        },
        "q2_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00032087979297203156, 0.0007804267934760396, 0.001674997056757823, 0.0031597355653722697, 0.005207505364267218, 0.007425988330756366, 0.009008024583912186, 0.008979793596277713, 0.006728643045947982, 0.002506462303534735] + [0.0] * 32 + [-0.002506462303534735, -0.006728643045947982, -0.008979793596277713, -0.009008024583912186, -0.007425988330756366, -0.005207505364267218, -0.0031597355653722697, -0.001674997056757823, -0.0007804267934760396, -0.00032087979297203156],
        },
        "q2_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005691157027022902, 0.0015470168729463355, 0.003763003219966468, 0.008190665441723633, 0.015953237899735254, 0.0278050418927889, 0.04336539668793448, 0.06052128643646852, 0.07558194011671057, 0.0844642593329297] + [0.08564555852304008] * 32 + [0.0844642593329297, 0.07558194011671057, 0.06052128643646852, 0.04336539668793448, 0.0278050418927889, 0.015953237899735254, 0.008190665441723633, 0.003763003219966468, 0.0015470168729463355, 0.0005691157027022902],
        },
        "q2_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00034956037273596835, 0.0008501821766146529, 0.001824710088687164, 0.0034421561163089443, 0.0056729577743041834, 0.008089731125756503, 0.009813171474595064, 0.009782417171032325, 0.0073300563720878125, 0.002730492590253645] + [0.0] * 32 + [-0.002730492590253645, -0.0073300563720878125, -0.009782417171032325, -0.009813171474595064, -0.008089731125756503, -0.0056729577743041834, -0.0034421561163089443, -0.001824710088687164, -0.0008501821766146529, -0.00034956037273596835],
        },
        "q2_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q2_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q2_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00034956037273596835, -0.0008501821766146529, -0.001824710088687164, -0.0034421561163089443, -0.0056729577743041834, -0.008089731125756503, -0.009813171474595064, -0.009782417171032325, -0.0073300563720878125, -0.002730492590253645] + [0.0] * 32 + [0.002730492590253645, 0.0073300563720878125, 0.009782417171032325, 0.009813171474595064, 0.008089731125756503, 0.0056729577743041834, 0.0034421561163089443, 0.001824710088687164, 0.0008501821766146529, 0.00034956037273596835],
        },
        "q2_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00032087979297203156, -0.0007804267934760396, -0.001674997056757823, -0.0031597355653722697, -0.005207505364267218, -0.007425988330756366, -0.009008024583912186, -0.008979793596277713, -0.006728643045947982, -0.002506462303534735] + [0.0] * 32 + [0.002506462303534735, 0.006728643045947982, 0.008979793596277713, 0.009008024583912186, 0.007425988330756366, 0.005207505364267218, 0.0031597355653722697, 0.001674997056757823, 0.0007804267934760396, 0.00032087979297203156],
        },
        "q2_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005691157027022902, -0.0015470168729463355, -0.003763003219966468, -0.008190665441723633, -0.015953237899735254, -0.0278050418927889, -0.04336539668793448, -0.06052128643646852, -0.07558194011671057, -0.0844642593329297] + [-0.08564555852304008] * 32 + [-0.0844642593329297, -0.07558194011671057, -0.06052128643646852, -0.04336539668793448, -0.0278050418927889, -0.015953237899735254, -0.008190665441723633, -0.003763003219966468, -0.0015470168729463355, -0.0005691157027022902],
        },
        "q3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 84 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005297769779599651+0j), (0.0014400831323245211+0j), (0.0035028948673558203+0j), (0.007624505815941894+0j), (0.014850509523929386+0j), (0.025883086683548395+0j), (0.04036787018225523+0j), (0.05633790120061767+0j), (0.0703575241963199+0j), (0.07862587491885455+0j)] + [(0.07972551970467169+0j)] * 84 + [(0.07862587491885455+0j), (0.0703575241963199+0j), (0.05633790120061767+0j), (0.04036787018225523+0j), (0.025883086683548395+0j), (0.014850509523929386+0j), (0.007624505815941894+0j), (0.0035028948673558203+0j), (0.0014400831323245211+0j), (0.0005297769779599651+0j)],
        },
        "q3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 84 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q3_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 84 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0002658773462345805+0j), (0.000722729558868374+0j), (0.0017579857755571989+0j), (0.0038264844586092008+0j), (0.007452974037599812+0j), (0.012989855516714248+0j), (0.020259283894384607+0j), (0.028274108326349662+0j), (0.035310088205392824+0j), (0.03945969688848365+0j)] + [(0.040011571827594065+0j)] * 84 + [(0.03945969688848365+0j), (0.035310088205392824+0j), (0.028274108326349662+0j), (0.020259283894384607+0j), (0.012989855516714248+0j), (0.007452974037599812+0j), (0.0038264844586092008+0j), (0.0017579857755571989+0j), (0.000722729558868374+0j), (0.0002658773462345805+0j)],
        },
        "q3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002658773462345805+0j), (-0.000722729558868374+0j), (-0.0017579857755571989+0j), (-0.0038264844586092008+0j), (-0.007452974037599812+0j), (-0.012989855516714248+0j), (-0.020259283894384607+0j), (-0.028274108326349662+0j), (-0.035310088205392824+0j), (-0.03945969688848365+0j)] + [(-0.040011571827594065+0j)] * 84 + [(-0.03945969688848365+0j), (-0.035310088205392824+0j), (-0.028274108326349662+0j), (-0.020259283894384607+0j), (-0.012989855516714248+0j), (-0.007452974037599812+0j), (-0.0038264844586092008+0j), (-0.0017579857755571989+0j), (-0.000722729558868374+0j), (-0.0002658773462345805+0j)],
        },
        "q3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005304889551832756+0j), (0.0014420184870729228+0j), (0.003507602473508908+0j), (0.007634752532401437+0j), (0.014870467402386671+0j), (0.02591787144950523+0j), (0.04042212132060027+0j), (0.056413614763367065+0j), (0.07045207899352757+0j), (0.07873154170777515+0j)] + [(0.07983266432685761+0j)] * 84 + [(0.07873154170777515+0j), (0.07045207899352757+0j), (0.056413614763367065+0j), (0.04042212132060027+0j), (0.02591787144950523+0j), (0.014870467402386671+0j), (0.007634752532401437+0j), (0.003507602473508908+0j), (0.0014420184870729228+0j), (0.0005304889551832756+0j)],
        },
        "q3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0002658773462345805+0j), (0.000722729558868374+0j), (0.0017579857755571989+0j), (0.0038264844586092008+0j), (0.007452974037599812+0j), (0.012989855516714248+0j), (0.020259283894384607+0j), (0.028274108326349662+0j), (0.035310088205392824+0j), (0.03945969688848365+0j)] + [(0.040011571827594065+0j)] * 84 + [(0.03945969688848365+0j), (0.035310088205392824+0j), (0.028274108326349662+0j), (0.020259283894384607+0j), (0.012989855516714248+0j), (0.007452974037599812+0j), (0.0038264844586092008+0j), (0.0017579857755571989+0j), (0.000722729558868374+0j), (0.0002658773462345805+0j)],
        },
        "q3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002658773462345805+0j), (-0.000722729558868374+0j), (-0.0017579857755571989+0j), (-0.0038264844586092008+0j), (-0.007452974037599812+0j), (-0.012989855516714248+0j), (-0.020259283894384607+0j), (-0.028274108326349662+0j), (-0.035310088205392824+0j), (-0.03945969688848365+0j)] + [(-0.040011571827594065+0j)] * 84 + [(-0.03945969688848365+0j), (-0.035310088205392824+0j), (-0.028274108326349662+0j), (-0.020259283894384607+0j), (-0.012989855516714248+0j), (-0.007452974037599812+0j), (-0.0038264844586092008+0j), (-0.0017579857755571989+0j), (-0.000722729558868374+0j), (-0.0002658773462345805+0j)],
        },
        "q3_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.00038176797986106103+0j), (0.00039961323041714847+0j), (0.00041819661838086536+0j), (0.00043754373997063444+0j), (0.0004576808405518453+0j), (0.0004786348200167087+0j), (0.0005004332376440023+0j), (0.0005231043164079211+0j), (0.0005466769467047441+0j), (0.0005711806894655669+0j), (0.000596645778622899+0j), (0.0006231031228985443+0j), (0.0006505843068798259+0j), (0.000679121591350921+0j), (0.0007087479128458104+0j), (0.0007394968823891409+0j), (0.0007714027833911662+0j), (0.0008045005686628154+0j), (0.0008388258565169343+0j), (0.0008744149259217456+0j), (0.0009113047106726964+0j), (0.0009495327925490024+0j), (0.000989137393421446+0j), (0.0010301573662782775+0j), (0.0010726321851364685+0j), (0.0011166019338059942+0j), (0.0011621072934753932+0j), (0.0012091895290874438+0j), (0.0012578904744745178+0j), (0.001308252516223945+0j), (0.0013603185762446192+0j), (0.0014141320930070214+0j), (0.0014697370014299018+0j), (0.0015271777113880197+0j), (0.0015864990848165619+0j), (0.0016477464113892253+0j), (0.0017109653827483589+0j), (0.0017762020652671022+0j), (0.0018435028713250836+0j), (0.0019129145290809613+0j), (0.001984484050726921+0j), (0.0020582586992121447+0j), (0.0021342859534243075+0j), (0.0022126134718202357+0j), (0.00229328905449912+0j), (0.0023763606037139062+0j), (0.0024618760828189652+0j), (0.0025498834736545546+0j), (0.002640430732371218+0j), (0.002733565743699892+0j), (0.0028293362736762687+0j), (0.002927789920830779+0j), (0.003028974065858462+0j), (0.003132935819786004+0j), (0.0032397219706562608+0j), (0.003349378928753702+0j), (0.0034619526703974545+0j), (0.003577488680331787+0j), (0.0036960318927472956+0j), (0.0038176266309692957+0j), (0.003942316545853412+0j), (0.004070144552931742+0j), (0.00420115276835648+0j), (0.004335382443691365+0j), (0.004472873899604841+0j), (0.00461366645852235+0j), (0.004757798376298738+0j), (0.00490530677297525+0j), (0.005056227562689175+0j), (0.005210595382807676+0j), (0.0053684435223608565+0j), (0.005529803849852547+0j), (0.005694706740530764+0j), (0.005863181003203124+0j), (0.006035253806685803+0j), (0.006210950605977941+0j), (0.006390295068256507+0j), (0.006573308998789743+0j), (0.006760012266870349+0j), (0.006950422731872411+0j), (0.007144556169538905+0j), (0.007342426198609258+0j), (0.007544044207899011+0j), (0.0077494192839460165+0j), (0.007958558139339853+0j), (0.008171465041853291+0j), (0.008388141744496537+0j), (0.008608587416616745+0j), (0.008832798576166962+0j), (0.009060769023269952+0j), (0.009292489775203647+0j), (0.009527949002935913+0j), (0.009767131969337157+0j), (0.010010020969199819+0j), (0.010256595271194203+0j), (0.010506831061890142+0j), (0.010760701391973928+0j), (0.011018176124789537+0j), (0.01127922188733259+0j), (0.011543802023824578+0j), (0.011811876551993786+0j), (0.012083402122187968+0j), (0.012358331979442132+0j), (0.012636615928622877+0j), (0.012918200302768605+0j), (0.01320302793474233+0j), (0.013491038132311195+0j), (0.013782166656763729+0j), (0.014076345705172577+0j), (0.01437350389640698+0j), (0.014673566260995289+0j), (0.014976454234933868+0j), (0.015282085657534262+0j), (0.015590374773395907+0j), (0.015901232238586853+0j), (0.01621456513110967+0j), (0.016530276965724483+0j), (0.016848267713195406+0j), (0.017168433824020665+0j), (0.017490668256700835+0j), (0.017814860510593052+0j), (0.018140896663392796+0j), (0.01846865941327785+0j), (0.018798028125742418+0j), (0.019128878885142007+0j), (0.01946108455096267+0j), (0.01979451481882057+0j), (0.020129036286190508+0j), (0.020464512522854077+0j), (0.020800804146050605+0j), (0.021137768900305862+0j), (0.02147526174190576+0j), (0.021813134927973998+0j), (0.022151238110104592+0j), (0.0224894184324921+0j), (0.022827520634494+0j), (0.02316538715755167+0j), (0.023502858256388117+0j), (0.023839772114392463+0j), (0.02417596496309308+0j), (0.024511271205613232+0j), (0.024845523543995073+0j), (0.025178553110269977+0j), (0.025510189601145407+0j), (0.025840261416170927+0j), (0.02616859579923839+0j), (0.0264950189832642+0j), (0.026819356337894108+0j), (0.02714143252006442+0j), (0.027461071627246557+0j), (0.02777809735319547+0j), (0.02809233314601623+0j), (0.028403602368357185+0j), (0.028711728459532303+0j), (0.029016535099370053+0j), (0.02931784637358103+0j), (0.02961548694043188+0j), (0.029909282198508687+0j), (0.030199058455348756+0j), (0.03048464309671646+0j), (0.030765864756295058+0j), (0.03104255348556383+0j), (0.0313145409236272+0j), (0.031581660466760475+0j), (0.03184374743743514+0j), (0.03210063925258533+0j), (0.032352175590876345+0j), (0.03259819855873562+0j), (0.03283855285490662+0j), (0.03307308593328654+0j), (0.03330164816380983+0j), (0.03352409299114052+0j), (0.033740277090938665+0j), (0.033950060523467974+0j), (0.034153306884314824+0j), (0.034349883451991685+0j), (0.03453966133220176+0j), (0.03472251559854554+0j), (0.034898325429454605+0j), (0.03506697424114255+0j), (0.035228349816368534+0j), (0.035382344428814494+0j), (0.035528854962882994+0j), (0.035667783028729465+0j), (0.03579903507234912+0j), (0.03592252248054624+0j), (0.03603816168062096+0j), (0.03614587423461657+0j), (0.0362455869279786+0j), (0.03633723185248538+0j), (0.036420746483318646+0j), (0.03649607375015163+0j), (0.03656316210214166+0j), (0.03662196556672347+0j), (0.03667244380210958+0j), (0.03671456214341352+0j), (0.03674829164232243+0j), (0.036773609100255115+0j), (0.036790497094952745+0j), (0.0367989440004592+0j)] + [(0.0368+0j)] * 3600 + [(0.0367989440004592+0j), (0.036790497094952745+0j), (0.036773609100255115+0j), (0.03674829164232243+0j), (0.03671456214341352+0j), (0.03667244380210958+0j), (0.03662196556672347+0j), (0.03656316210214166+0j), (0.03649607375015163+0j), (0.036420746483318646+0j), (0.03633723185248538+0j), (0.0362455869279786+0j), (0.03614587423461657+0j), (0.03603816168062096+0j), (0.03592252248054624+0j), (0.03579903507234912+0j), (0.035667783028729465+0j), (0.035528854962882994+0j), (0.035382344428814494+0j), (0.035228349816368534+0j), (0.03506697424114255+0j), (0.034898325429454605+0j), (0.03472251559854554+0j), (0.03453966133220176+0j), (0.034349883451991685+0j), (0.034153306884314824+0j), (0.033950060523467974+0j), (0.033740277090938665+0j), (0.03352409299114052+0j), (0.03330164816380983+0j), (0.03307308593328654+0j), (0.03283855285490662+0j), (0.03259819855873562+0j), (0.032352175590876345+0j), (0.03210063925258533+0j), (0.03184374743743514+0j), (0.031581660466760475+0j), (0.0313145409236272+0j), (0.03104255348556383+0j), (0.030765864756295058+0j), (0.03048464309671646+0j), (0.030199058455348756+0j), (0.029909282198508687+0j), (0.02961548694043188+0j), (0.02931784637358103+0j), (0.029016535099370053+0j), (0.028711728459532303+0j), (0.028403602368357185+0j), (0.02809233314601623+0j), (0.02777809735319547+0j), (0.027461071627246557+0j), (0.02714143252006442+0j), (0.026819356337894108+0j), (0.0264950189832642+0j), (0.02616859579923839+0j), (0.025840261416170927+0j), (0.025510189601145407+0j), (0.025178553110269977+0j), (0.024845523543995073+0j), (0.024511271205613232+0j), (0.02417596496309308+0j), (0.023839772114392463+0j), (0.023502858256388117+0j), (0.02316538715755167+0j), (0.022827520634494+0j), (0.0224894184324921+0j), (0.022151238110104592+0j), (0.021813134927973998+0j), (0.02147526174190576+0j), (0.021137768900305862+0j), (0.020800804146050605+0j), (0.020464512522854077+0j), (0.020129036286190508+0j), (0.01979451481882057+0j), (0.01946108455096267+0j), (0.019128878885142007+0j), (0.018798028125742418+0j), (0.01846865941327785+0j), (0.018140896663392796+0j), (0.017814860510593052+0j), (0.017490668256700835+0j), (0.017168433824020665+0j), (0.016848267713195406+0j), (0.016530276965724483+0j), (0.01621456513110967+0j), (0.015901232238586853+0j), (0.015590374773395907+0j), (0.015282085657534262+0j), (0.014976454234933868+0j), (0.014673566260995289+0j), (0.01437350389640698+0j), (0.014076345705172577+0j), (0.013782166656763729+0j), (0.013491038132311195+0j), (0.01320302793474233+0j), (0.012918200302768605+0j), (0.012636615928622877+0j), (0.012358331979442132+0j), (0.012083402122187968+0j), (0.011811876551993786+0j), (0.011543802023824578+0j), (0.01127922188733259+0j), (0.011018176124789537+0j), (0.010760701391973928+0j), (0.010506831061890142+0j), (0.010256595271194203+0j), (0.010010020969199819+0j), (0.009767131969337157+0j), (0.009527949002935913+0j), (0.009292489775203647+0j), (0.009060769023269952+0j), (0.008832798576166962+0j), (0.008608587416616745+0j), (0.008388141744496537+0j), (0.008171465041853291+0j), (0.007958558139339853+0j), (0.0077494192839460165+0j), (0.007544044207899011+0j), (0.007342426198609258+0j), (0.007144556169538905+0j), (0.006950422731872411+0j), (0.006760012266870349+0j), (0.006573308998789743+0j), (0.006390295068256507+0j), (0.006210950605977941+0j), (0.006035253806685803+0j), (0.005863181003203124+0j), (0.005694706740530764+0j), (0.005529803849852547+0j), (0.0053684435223608565+0j), (0.005210595382807676+0j), (0.005056227562689175+0j), (0.00490530677297525+0j), (0.004757798376298738+0j), (0.00461366645852235+0j), (0.004472873899604841+0j), (0.004335382443691365+0j), (0.00420115276835648+0j), (0.004070144552931742+0j), (0.003942316545853412+0j), (0.0038176266309692957+0j), (0.0036960318927472956+0j), (0.003577488680331787+0j), (0.0034619526703974545+0j), (0.003349378928753702+0j), (0.0032397219706562608+0j), (0.003132935819786004+0j), (0.003028974065858462+0j), (0.002927789920830779+0j), (0.0028293362736762687+0j), (0.002733565743699892+0j), (0.002640430732371218+0j), (0.0025498834736545546+0j), (0.0024618760828189652+0j), (0.0023763606037139062+0j), (0.00229328905449912+0j), (0.0022126134718202357+0j), (0.0021342859534243075+0j), (0.0020582586992121447+0j), (0.001984484050726921+0j), (0.0019129145290809613+0j), (0.0018435028713250836+0j), (0.0017762020652671022+0j), (0.0017109653827483589+0j), (0.0016477464113892253+0j), (0.0015864990848165619+0j), (0.0015271777113880197+0j), (0.0014697370014299018+0j), (0.0014141320930070214+0j), (0.0013603185762446192+0j), (0.001308252516223945+0j), (0.0012578904744745178+0j), (0.0012091895290874438+0j), (0.0011621072934753932+0j), (0.0011166019338059942+0j), (0.0010726321851364685+0j), (0.0010301573662782775+0j), (0.000989137393421446+0j), (0.0009495327925490024+0j), (0.0009113047106726964+0j), (0.0008744149259217456+0j), (0.0008388258565169343+0j), (0.0008045005686628154+0j), (0.0007714027833911662+0j), (0.0007394968823891409+0j), (0.0007087479128458104+0j), (0.000679121591350921+0j), (0.0006505843068798259+0j), (0.0006231031228985443+0j), (0.000596645778622899+0j), (0.0005711806894655669+0j), (0.0005466769467047441+0j), (0.0005231043164079211+0j), (0.0005004332376440023+0j), (0.0004786348200167087+0j), (0.0004576808405518453+0j), (0.00043754373997063444+0j), (0.00041819661838086536+0j), (0.00039961323041714847+0j), (0.00038176797986106103+0j)],
        },
        "q3_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005297769779599651, 0.0014400831323245211, 0.0035028948673558203, 0.007624505815941894, 0.014850509523929386, 0.025883086683548395, 0.04036787018225523, 0.05633790120061767, 0.0703575241963199, 0.07862587491885455] + [0.07972551970467169] * 84 + [0.07862587491885455, 0.0703575241963199, 0.05633790120061767, 0.04036787018225523, 0.025883086683548395, 0.014850509523929386, 0.007624505815941894, 0.0035028948673558203, 0.0014400831323245211, 0.0005297769779599651],
        },
        "q3_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0015778262083211557, -0.0038375051199620613, -0.008236275118899891, -0.015537013223027658, -0.025606281927606427, -0.03651497933986679, -0.04429414872795296, -0.04415533165953026, -0.03308600160203912, -0.012324745899567523] + [0.0] * 84 + [0.012324745899567523, 0.03308600160203912, 0.04415533165953026, 0.04429414872795296, 0.03651497933986679, 0.025606281927606427, 0.015537013223027658, 0.008236275118899891, 0.0038375051199620613, 0.0015778262083211557],
        },
        "q3_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002658773462345805, 0.000722729558868374, 0.0017579857755571989, 0.0038264844586092008, 0.007452974037599812, 0.012989855516714248, 0.020259283894384607, 0.028274108326349662, 0.035310088205392824, 0.03945969688848365] + [0.040011571827594065] * 84 + [0.03945969688848365, 0.035310088205392824, 0.028274108326349662, 0.020259283894384607, 0.012989855516714248, 0.007452974037599812, 0.0038264844586092008, 0.0017579857755571989, 0.000722729558868374, 0.0002658773462345805],
        },
        "q3_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0007918582017346574, -0.001925915469913515, -0.004133511010432188, -0.0077975072832673215, -0.012850936467762062, -0.01832564684497857, -0.022229751777544996, -0.022160084133800988, -0.01660475760448769, -0.006185377751617155] + [0.0] * 84 + [0.006185377751617155, 0.01660475760448769, 0.022160084133800988, 0.022229751777544996, 0.01832564684497857, 0.012850936467762062, 0.0077975072832673215, 0.004133511010432188, 0.001925915469913515, 0.0007918582017346574],
        },
        "q3_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002658773462345805, -0.000722729558868374, -0.0017579857755571989, -0.0038264844586092008, -0.007452974037599812, -0.012989855516714248, -0.020259283894384607, -0.028274108326349662, -0.035310088205392824, -0.03945969688848365] + [-0.040011571827594065] * 84 + [-0.03945969688848365, -0.035310088205392824, -0.028274108326349662, -0.020259283894384607, -0.012989855516714248, -0.007452974037599812, -0.0038264844586092008, -0.0017579857755571989, -0.000722729558868374, -0.0002658773462345805],
        },
        "q3_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0007918582017346574, 0.001925915469913515, 0.004133511010432188, 0.0077975072832673215, 0.012850936467762062, 0.01832564684497857, 0.022229751777544996, 0.022160084133800988, 0.01660475760448769, 0.006185377751617155] + [0.0] * 84 + [-0.006185377751617155, -0.01660475760448769, -0.022160084133800988, -0.022229751777544996, -0.01832564684497857, -0.012850936467762062, -0.0077975072832673215, -0.004133511010432188, -0.001925915469913515, -0.0007918582017346574],
        },
        "q3_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001579946678574493, 0.00384266241511345, 0.008247344003607104, 0.015557893706690171, 0.025640694690456798, 0.03656405250589932, 0.044353676465722296, 0.04421467283843608, 0.03313046650053617, 0.012341309356887565] + [0.0] * 84 + [-0.012341309356887565, -0.03313046650053617, -0.04421467283843608, -0.044353676465722296, -0.03656405250589932, -0.025640694690456798, -0.015557893706690171, -0.008247344003607104, -0.00384266241511345, -0.001579946678574493],
        },
        "q3_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005304889551832756, 0.0014420184870729228, 0.003507602473508908, 0.007634752532401437, 0.014870467402386671, 0.02591787144950523, 0.04042212132060027, 0.056413614763367065, 0.07045207899352757, 0.07873154170777515] + [0.07983266432685761] * 84 + [0.07873154170777515, 0.07045207899352757, 0.056413614763367065, 0.04042212132060027, 0.02591787144950523, 0.014870467402386671, 0.007634752532401437, 0.003507602473508908, 0.0014420184870729228, 0.0005304889551832756],
        },
        "q3_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007918582017346574, 0.001925915469913515, 0.004133511010432188, 0.0077975072832673215, 0.012850936467762062, 0.01832564684497857, 0.022229751777544996, 0.022160084133800988, 0.01660475760448769, 0.006185377751617155] + [0.0] * 84 + [-0.006185377751617155, -0.01660475760448769, -0.022160084133800988, -0.022229751777544996, -0.01832564684497857, -0.012850936467762062, -0.0077975072832673215, -0.004133511010432188, -0.001925915469913515, -0.0007918582017346574],
        },
        "q3_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002658773462345805, 0.000722729558868374, 0.0017579857755571989, 0.0038264844586092008, 0.007452974037599812, 0.012989855516714248, 0.020259283894384607, 0.028274108326349662, 0.035310088205392824, 0.03945969688848365] + [0.040011571827594065] * 84 + [0.03945969688848365, 0.035310088205392824, 0.028274108326349662, 0.020259283894384607, 0.012989855516714248, 0.007452974037599812, 0.0038264844586092008, 0.0017579857755571989, 0.000722729558868374, 0.0002658773462345805],
        },
        "q3_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0018464879486740189, 0.004490929938680866, 0.009638693202589267, 0.018182552377067635, 0.029966349107601292, 0.04273250687658816, 0.051836261428287955, 0.05167380751380678, 0.03871966564237693, 0.014423321563555132] + [0.0] * 84 + [-0.014423321563555132, -0.03871966564237693, -0.05167380751380678, -0.051836261428287955, -0.04273250687658816, -0.029966349107601292, -0.018182552377067635, -0.009638693202589267, -0.004490929938680866, -0.0018464879486740189],
        },
        "q3_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q3_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q3_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0018464879486740189, -0.004490929938680866, -0.009638693202589267, -0.018182552377067635, -0.029966349107601292, -0.04273250687658816, -0.051836261428287955, -0.05167380751380678, -0.03871966564237693, -0.014423321563555132] + [0.0] * 84 + [0.014423321563555132, 0.03871966564237693, 0.05167380751380678, 0.051836261428287955, 0.04273250687658816, 0.029966349107601292, 0.018182552377067635, 0.009638693202589267, 0.004490929938680866, 0.0018464879486740189],
        },
        "q3_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0007918582017346574, -0.001925915469913515, -0.004133511010432188, -0.0077975072832673215, -0.012850936467762062, -0.01832564684497857, -0.022229751777544996, -0.022160084133800988, -0.01660475760448769, -0.006185377751617155] + [0.0] * 84 + [0.006185377751617155, 0.01660475760448769, 0.022160084133800988, 0.022229751777544996, 0.01832564684497857, 0.012850936467762062, 0.0077975072832673215, 0.004133511010432188, 0.001925915469913515, 0.0007918582017346574],
        },
        "q3_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002658773462345805, -0.000722729558868374, -0.0017579857755571989, -0.0038264844586092008, -0.007452974037599812, -0.012989855516714248, -0.020259283894384607, -0.028274108326349662, -0.035310088205392824, -0.03945969688848365] + [-0.040011571827594065] * 84 + [-0.03945969688848365, -0.035310088205392824, -0.028274108326349662, -0.020259283894384607, -0.012989855516714248, -0.007452974037599812, -0.0038264844586092008, -0.0017579857755571989, -0.000722729558868374, -0.0002658773462345805],
        },
        "q4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 52 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005036741853813904+0j), (0.001369128385586146+0j), (0.0033303027352868946+0j), (0.007248836615301946+0j), (0.01411880583366716+0j), (0.024607793737457053+0j), (0.038378893337198995+0j), (0.05356206040244866+0j), (0.0668909185549978+0j), (0.074751877010869+0j)] + [(0.07579734088481482+0j)] * 52 + [(0.074751877010869+0j), (0.0668909185549978+0j), (0.05356206040244866+0j), (0.038378893337198995+0j), (0.024607793737457053+0j), (0.01411880583366716+0j), (0.007248836615301946+0j), (0.0033303027352868946+0j), (0.001369128385586146+0j), (0.0005036741853813904+0j)],
        },
        "q4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 52 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q4_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 52 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00024954327146837384+0j), (0.0006783289402467032+0j), (0.001649984580635748+0j), (0.0035914058250820498+0j), (0.006995103380754364+0j), (0.012191828628688103+0j), (0.01901466240809702+0j), (0.026537099115557586+0j), (0.03314082621704963+0j), (0.03703550525141325+0j)] + [(0.03755347596120631+0j)] * 52 + [(0.03703550525141325+0j), (0.03314082621704963+0j), (0.026537099115557586+0j), (0.01901466240809702+0j), (0.012191828628688103+0j), (0.006995103380754364+0j), (0.0035914058250820498+0j), (0.001649984580635748+0j), (0.0006783289402467032+0j), (0.00024954327146837384+0j)],
        },
        "q4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00024954327146837384+0j), (-0.0006783289402467032+0j), (-0.001649984580635748+0j), (-0.0035914058250820498+0j), (-0.006995103380754364+0j), (-0.012191828628688103+0j), (-0.01901466240809702+0j), (-0.026537099115557586+0j), (-0.03314082621704963+0j), (-0.03703550525141325+0j)] + [(-0.03755347596120631+0j)] * 52 + [(-0.03703550525141325+0j), (-0.03314082621704963+0j), (-0.026537099115557586+0j), (-0.01901466240809702+0j), (-0.012191828628688103+0j), (-0.006995103380754364+0j), (-0.0035914058250820498+0j), (-0.001649984580635748+0j), (-0.0006783289402467032+0j), (-0.00024954327146837384+0j)],
        },
        "q4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005036741853813904+0j), (0.001369128385586146+0j), (0.0033303027352868946+0j), (0.007248836615301946+0j), (0.01411880583366716+0j), (0.024607793737457053+0j), (0.038378893337198995+0j), (0.05356206040244866+0j), (0.0668909185549978+0j), (0.074751877010869+0j)] + [(0.07579734088481482+0j)] * 52 + [(0.074751877010869+0j), (0.0668909185549978+0j), (0.05356206040244866+0j), (0.038378893337198995+0j), (0.024607793737457053+0j), (0.01411880583366716+0j), (0.007248836615301946+0j), (0.0033303027352868946+0j), (0.001369128385586146+0j), (0.0005036741853813904+0j)],
        },
        "q4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00024954327146837384+0j), (0.0006783289402467032+0j), (0.001649984580635748+0j), (0.0035914058250820498+0j), (0.006995103380754364+0j), (0.012191828628688103+0j), (0.01901466240809702+0j), (0.026537099115557586+0j), (0.03314082621704963+0j), (0.03703550525141325+0j)] + [(0.03755347596120631+0j)] * 52 + [(0.03703550525141325+0j), (0.03314082621704963+0j), (0.026537099115557586+0j), (0.01901466240809702+0j), (0.012191828628688103+0j), (0.006995103380754364+0j), (0.0035914058250820498+0j), (0.001649984580635748+0j), (0.0006783289402467032+0j), (0.00024954327146837384+0j)],
        },
        "q4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00024954327146837384+0j), (-0.0006783289402467032+0j), (-0.001649984580635748+0j), (-0.0035914058250820498+0j), (-0.006995103380754364+0j), (-0.012191828628688103+0j), (-0.01901466240809702+0j), (-0.026537099115557586+0j), (-0.03314082621704963+0j), (-0.03703550525141325+0j)] + [(-0.03755347596120631+0j)] * 52 + [(-0.03703550525141325+0j), (-0.03314082621704963+0j), (-0.026537099115557586+0j), (-0.01901466240809702+0j), (-0.012191828628688103+0j), (-0.006995103380754364+0j), (-0.0035914058250820498+0j), (-0.001649984580635748+0j), (-0.0006783289402467032+0j), (-0.00024954327146837384+0j)],
        },
        "q4_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0009544199496526527+0j), (0.0009990330760428713+0j), (0.0010454915459521636+0j), (0.0010938593499265864+0j), (0.0011442021013796135+0j), (0.001196587050041772+0j), (0.0012510830941100059+0j), (0.0013077607910198027+0j), (0.0013666923667618605+0j), (0.0014279517236639174+0j), (0.0014916144465572478+0j), (0.0015577578072463608+0j), (0.0016264607671995649+0j), (0.001697803978377303+0j), (0.001771869782114526+0j), (0.0018487422059728525+0j), (0.001928506958477916+0j), (0.0020112514216570386+0j), (0.0020970646412923357+0j), (0.0021860373148043645+0j), (0.0022782617766817412+0j), (0.0023738319813725066+0j), (0.0024728434835536153+0j), (0.002575393415695694+0j), (0.002681580462841172+0j), (0.002791504834514986+0j), (0.0029052682336884834+0j), (0.0030229738227186102+0j), (0.0031447261861862947+0j), (0.003270631290559863+0j), (0.0034007964406115483+0j), (0.003535330232517554+0j), (0.003674342503574755+0j), (0.00381794427847005+0j), (0.003966247712041405+0j), (0.0041193660284730635+0j), (0.004277413456870898+0j), (0.004440505163167756+0j), (0.00460875717831271+0j), (0.004782286322702404+0j), (0.004961210126817303+0j), (0.005145646748030363+0j), (0.00533571488356077+0j), (0.005531533679550589+0j), (0.005733222636247801+0j), (0.0059409015092847664+0j), (0.006154690207047414+0j), (0.006374708684136388+0j), (0.006601076830928045+0j), (0.0068339143592497315+0j), (0.007073340684190673+0j), (0.0073194748020769486+0j), (0.007572435164646156+0j), (0.00783233954946501+0j), (0.008099304926640653+0j), (0.008373447321884256+0j), (0.008654881675993637+0j), (0.008943721700829469+0j), (0.00924007973186824+0j), (0.009544066577423242+0j), (0.00985579136463353+0j), (0.010175361382329356+0j), (0.0105028819208912+0j), (0.010838456109228414+0j), (0.011182184749012102+0j), (0.011534166146305877+0j), (0.011894495940746848+0j), (0.012263266932438125+0j), (0.01264056890672294+0j), (0.013026488457019193+0j), (0.013421108805902143+0j), (0.013824509624631368+0j), (0.014236766851326911+0j), (0.014657952508007811+0j), (0.015088134516714511+0j), (0.015527376514944857+0j), (0.01597573767064127+0j), (0.01643327249697436+0j), (0.016900030667175873+0j), (0.01737605682968103+0j), (0.017861390423847268+0j), (0.01835606549652315+0j), (0.018860110519747533+0j), (0.019373548209865043+0j), (0.019896395348349635+0j), (0.020428662604633233+0j), (0.020970354361241346+0j), (0.021521468541541865+0j), (0.022081996440417407+0j), (0.022651922558174883+0j), (0.02323122443800912+0j), (0.023819872507339787+0j), (0.024417829923342897+0j), (0.02502505242299955+0j), (0.025641488177985512+0j), (0.026267077654725357+0j), (0.02690175347993482+0j), (0.027545440311973847+0j), (0.028198054718331478+0j), (0.02885950505956145+0j), (0.029529691379984468+0j), (0.030208505305469927+0j), (0.030895829948605333+0j), (0.0315915398215572+0j), (0.032295500756921516+0j), (0.03300756983685583+0j), (0.033727595330777994+0j), (0.03445541664190933+0j), (0.03519086426293145+0j), (0.03593375974101745+0j), (0.03668391565248823+0j), (0.037441135587334674+0j), (0.03820521414383566+0j), (0.038975936933489774+0j), (0.039753080596467136+0j), (0.040536412827774176+0j), (0.04132569241431121+0j), (0.04212066928298852+0j), (0.04292108456005167+0j), (0.0437266706417521+0j), (0.04453715127648264+0j), (0.04535224165848199+0j), (0.04617164853319463+0j), (0.04699507031435605+0j), (0.04782219721285503+0j), (0.048652711377406684+0j), (0.04948628704705143+0j), (0.05032259071547628+0j), (0.0511612813071352+0j), (0.05200201036512652+0j), (0.05284442225076467+0j), (0.053688154354764414+0j), (0.054532837319935+0j), (0.05537809527526149+0j), (0.05622354608123026+0j), (0.05706880158623501+0j), (0.05791346789387918+0j), (0.05875714564097031+0j), (0.05959943028598117+0j), (0.06043991240773271+0j), (0.06127817801403309+0j), (0.06211380885998769+0j), (0.06294638277567495+0j), (0.06377547400286353+0j), (0.06460065354042732+0j), (0.065421489498096+0j), (0.0662375474581605+0j), (0.06704839084473528+0j), (0.06785358130016106+0j), (0.0686526790681164+0j), (0.06944524338298869+0j), (0.07023083286504059+0j), (0.07100900592089297+0j), (0.07177932114883076+0j), (0.07254133774842515+0j), (0.07329461593395258+0j), (0.07403871735107972+0j), (0.07477320549627173+0j), (0.0754976461383719+0j), (0.07621160774179116+0j), (0.07691466189073766+0j), (0.07760638371390959+0j), (0.078286352309068+0j), (0.0789541511669012+0j), (0.07960936859358786+0j), (0.08025159813146333+0j), (0.08088043897719088+0j), (0.08149549639683906+0j), (0.08209638213726655+0j), (0.08268271483321636+0j), (0.08325412040952458+0j), (0.08381023247785133+0j), (0.08435069272734667+0j), (0.08487515130866995+0j), (0.08538326721078707+0j), (0.08587470862997923+0j), (0.08634915333050441+0j), (0.08680628899636386+0j), (0.08724581357363653+0j), (0.08766743560285638+0j), (0.08807087454092134+0j), (0.08845586107203625+0j), (0.0888221374072075+0j), (0.08916945757182367+0j), (0.0894975876808728+0j), (0.08980630620136561+0j), (0.09009540420155242+0j), (0.09036468558654144+0j), (0.0906139673199465+0j), (0.09084307963121346+0j), (0.09105186620829663+0j), (0.09124018437537909+0j), (0.09140790525535415+0j), (0.0915549139168087+0j), (0.09168110950527397+0j), (0.09178640535853383+0j), (0.09187072910580608+0j), (0.0919340227506378+0j), (0.09197624273738188+0j), (0.09199736000114803+0j)] + [(0.09200000000000001+0j)] * 2800 + [(0.09199736000114803+0j), (0.09197624273738188+0j), (0.0919340227506378+0j), (0.09187072910580608+0j), (0.09178640535853383+0j), (0.09168110950527397+0j), (0.0915549139168087+0j), (0.09140790525535415+0j), (0.09124018437537909+0j), (0.09105186620829663+0j), (0.09084307963121346+0j), (0.0906139673199465+0j), (0.09036468558654144+0j), (0.09009540420155242+0j), (0.08980630620136561+0j), (0.0894975876808728+0j), (0.08916945757182367+0j), (0.0888221374072075+0j), (0.08845586107203625+0j), (0.08807087454092134+0j), (0.08766743560285638+0j), (0.08724581357363653+0j), (0.08680628899636386+0j), (0.08634915333050441+0j), (0.08587470862997923+0j), (0.08538326721078707+0j), (0.08487515130866995+0j), (0.08435069272734667+0j), (0.08381023247785133+0j), (0.08325412040952458+0j), (0.08268271483321636+0j), (0.08209638213726655+0j), (0.08149549639683906+0j), (0.08088043897719088+0j), (0.08025159813146333+0j), (0.07960936859358786+0j), (0.0789541511669012+0j), (0.078286352309068+0j), (0.07760638371390959+0j), (0.07691466189073766+0j), (0.07621160774179116+0j), (0.0754976461383719+0j), (0.07477320549627173+0j), (0.07403871735107972+0j), (0.07329461593395258+0j), (0.07254133774842515+0j), (0.07177932114883076+0j), (0.07100900592089297+0j), (0.07023083286504059+0j), (0.06944524338298869+0j), (0.0686526790681164+0j), (0.06785358130016106+0j), (0.06704839084473528+0j), (0.0662375474581605+0j), (0.065421489498096+0j), (0.06460065354042732+0j), (0.06377547400286353+0j), (0.06294638277567495+0j), (0.06211380885998769+0j), (0.06127817801403309+0j), (0.06043991240773271+0j), (0.05959943028598117+0j), (0.05875714564097031+0j), (0.05791346789387918+0j), (0.05706880158623501+0j), (0.05622354608123026+0j), (0.05537809527526149+0j), (0.054532837319935+0j), (0.053688154354764414+0j), (0.05284442225076467+0j), (0.05200201036512652+0j), (0.0511612813071352+0j), (0.05032259071547628+0j), (0.04948628704705143+0j), (0.048652711377406684+0j), (0.04782219721285503+0j), (0.04699507031435605+0j), (0.04617164853319463+0j), (0.04535224165848199+0j), (0.04453715127648264+0j), (0.0437266706417521+0j), (0.04292108456005167+0j), (0.04212066928298852+0j), (0.04132569241431121+0j), (0.040536412827774176+0j), (0.039753080596467136+0j), (0.038975936933489774+0j), (0.03820521414383566+0j), (0.037441135587334674+0j), (0.03668391565248823+0j), (0.03593375974101745+0j), (0.03519086426293145+0j), (0.03445541664190933+0j), (0.033727595330777994+0j), (0.03300756983685583+0j), (0.032295500756921516+0j), (0.0315915398215572+0j), (0.030895829948605333+0j), (0.030208505305469927+0j), (0.029529691379984468+0j), (0.02885950505956145+0j), (0.028198054718331478+0j), (0.027545440311973847+0j), (0.02690175347993482+0j), (0.026267077654725357+0j), (0.025641488177985512+0j), (0.02502505242299955+0j), (0.024417829923342897+0j), (0.023819872507339787+0j), (0.02323122443800912+0j), (0.022651922558174883+0j), (0.022081996440417407+0j), (0.021521468541541865+0j), (0.020970354361241346+0j), (0.020428662604633233+0j), (0.019896395348349635+0j), (0.019373548209865043+0j), (0.018860110519747533+0j), (0.01835606549652315+0j), (0.017861390423847268+0j), (0.01737605682968103+0j), (0.016900030667175873+0j), (0.01643327249697436+0j), (0.01597573767064127+0j), (0.015527376514944857+0j), (0.015088134516714511+0j), (0.014657952508007811+0j), (0.014236766851326911+0j), (0.013824509624631368+0j), (0.013421108805902143+0j), (0.013026488457019193+0j), (0.01264056890672294+0j), (0.012263266932438125+0j), (0.011894495940746848+0j), (0.011534166146305877+0j), (0.011182184749012102+0j), (0.010838456109228414+0j), (0.0105028819208912+0j), (0.010175361382329356+0j), (0.00985579136463353+0j), (0.009544066577423242+0j), (0.00924007973186824+0j), (0.008943721700829469+0j), (0.008654881675993637+0j), (0.008373447321884256+0j), (0.008099304926640653+0j), (0.00783233954946501+0j), (0.007572435164646156+0j), (0.0073194748020769486+0j), (0.007073340684190673+0j), (0.0068339143592497315+0j), (0.006601076830928045+0j), (0.006374708684136388+0j), (0.006154690207047414+0j), (0.0059409015092847664+0j), (0.005733222636247801+0j), (0.005531533679550589+0j), (0.00533571488356077+0j), (0.005145646748030363+0j), (0.004961210126817303+0j), (0.004782286322702404+0j), (0.00460875717831271+0j), (0.004440505163167756+0j), (0.004277413456870898+0j), (0.0041193660284730635+0j), (0.003966247712041405+0j), (0.00381794427847005+0j), (0.003674342503574755+0j), (0.003535330232517554+0j), (0.0034007964406115483+0j), (0.003270631290559863+0j), (0.0031447261861862947+0j), (0.0030229738227186102+0j), (0.0029052682336884834+0j), (0.002791504834514986+0j), (0.002681580462841172+0j), (0.002575393415695694+0j), (0.0024728434835536153+0j), (0.0023738319813725066+0j), (0.0022782617766817412+0j), (0.0021860373148043645+0j), (0.0020970646412923357+0j), (0.0020112514216570386+0j), (0.001928506958477916+0j), (0.0018487422059728525+0j), (0.001771869782114526+0j), (0.001697803978377303+0j), (0.0016264607671995649+0j), (0.0015577578072463608+0j), (0.0014916144465572478+0j), (0.0014279517236639174+0j), (0.0013666923667618605+0j), (0.0013077607910198027+0j), (0.0012510830941100059+0j), (0.001196587050041772+0j), (0.0011442021013796135+0j), (0.0010938593499265864+0j), (0.0010454915459521636+0j), (0.0009990330760428713+0j), (0.0009544199496526527+0j)],
        },
        "q4_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005036741853813904, 0.001369128385586146, 0.0033303027352868946, 0.007248836615301946, 0.01411880583366716, 0.024607793737457053, 0.038378893337198995, 0.05356206040244866, 0.0668909185549978, 0.074751877010869] + [0.07579734088481482] * 52 + [0.074751877010869, 0.0668909185549978, 0.05356206040244866, 0.038378893337198995, 0.024607793737457053, 0.01411880583366716, 0.007248836615301946, 0.0033303027352868946, 0.001369128385586146, 0.0005036741853813904],
        },
        "q4_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000229852241423118, -0.0005590344162393543, -0.0011998319504851734, -0.0022633781182614457, -0.0037302342073751572, -0.005319375354854596, -0.006452617730239048, -0.006432395341894583, -0.004819853788618043, -0.0017954261724427933] + [0.0] * 52 + [0.0017954261724427933, 0.004819853788618043, 0.006432395341894583, 0.006452617730239048, 0.005319375354854596, 0.0037302342073751572, 0.0022633781182614457, 0.0011998319504851734, 0.0005590344162393543, 0.000229852241423118],
        },
        "q4_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00024954327146837384, 0.0006783289402467032, 0.001649984580635748, 0.0035914058250820498, 0.006995103380754364, 0.012191828628688103, 0.01901466240809702, 0.026537099115557586, 0.03314082621704963, 0.03703550525141325] + [0.03755347596120631] * 52 + [0.03703550525141325, 0.03314082621704963, 0.026537099115557586, 0.01901466240809702, 0.012191828628688103, 0.006995103380754364, 0.0035914058250820498, 0.001649984580635748, 0.0006783289402467032, 0.00024954327146837384],
        },
        "q4_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00011387933299704621, -0.00027697126662575906, -0.0005944517285705875, -0.0011213812353182428, -0.001848128958101703, -0.00263546230230862, -0.003196922504017968, -0.003186903406174865, -0.002387976428651453, -0.0008895363982413645] + [0.0] * 52 + [0.0008895363982413645, 0.002387976428651453, 0.003186903406174865, 0.003196922504017968, 0.00263546230230862, 0.001848128958101703, 0.0011213812353182428, 0.0005944517285705875, 0.00027697126662575906, 0.00011387933299704621],
        },
        "q4_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00024954327146837384, -0.0006783289402467032, -0.001649984580635748, -0.0035914058250820498, -0.006995103380754364, -0.012191828628688103, -0.01901466240809702, -0.026537099115557586, -0.03314082621704963, -0.03703550525141325] + [-0.03755347596120631] * 52 + [-0.03703550525141325, -0.03314082621704963, -0.026537099115557586, -0.01901466240809702, -0.012191828628688103, -0.006995103380754364, -0.0035914058250820498, -0.001649984580635748, -0.0006783289402467032, -0.00024954327146837384],
        },
        "q4_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00011387933299704621, 0.00027697126662575906, 0.0005944517285705875, 0.0011213812353182428, 0.001848128958101703, 0.00263546230230862, 0.003196922504017968, 0.003186903406174865, 0.002387976428651453, 0.0008895363982413645] + [0.0] * 52 + [-0.0008895363982413645, -0.002387976428651453, -0.003186903406174865, -0.003196922504017968, -0.00263546230230862, -0.001848128958101703, -0.0011213812353182428, -0.0005944517285705875, -0.00027697126662575906, -0.00011387933299704621],
        },
        "q4_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.000229852241423118, 0.0005590344162393543, 0.0011998319504851734, 0.0022633781182614457, 0.0037302342073751572, 0.005319375354854596, 0.006452617730239048, 0.006432395341894583, 0.004819853788618043, 0.0017954261724427933] + [0.0] * 52 + [-0.0017954261724427933, -0.004819853788618043, -0.006432395341894583, -0.006452617730239048, -0.005319375354854596, -0.0037302342073751572, -0.0022633781182614457, -0.0011998319504851734, -0.0005590344162393543, -0.000229852241423118],
        },
        "q4_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005036741853813904, 0.001369128385586146, 0.0033303027352868946, 0.007248836615301946, 0.01411880583366716, 0.024607793737457053, 0.038378893337198995, 0.05356206040244866, 0.0668909185549978, 0.074751877010869] + [0.07579734088481482] * 52 + [0.074751877010869, 0.0668909185549978, 0.05356206040244866, 0.038378893337198995, 0.024607793737457053, 0.01411880583366716, 0.007248836615301946, 0.0033303027352868946, 0.001369128385586146, 0.0005036741853813904],
        },
        "q4_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00011387933299704621, 0.00027697126662575906, 0.0005944517285705875, 0.0011213812353182428, 0.001848128958101703, 0.00263546230230862, 0.003196922504017968, 0.003186903406174865, 0.002387976428651453, 0.0008895363982413645] + [0.0] * 52 + [-0.0008895363982413645, -0.002387976428651453, -0.003186903406174865, -0.003196922504017968, -0.00263546230230862, -0.001848128958101703, -0.0011213812353182428, -0.0005944517285705875, -0.00027697126662575906, -0.00011387933299704621],
        },
        "q4_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00024954327146837384, 0.0006783289402467032, 0.001649984580635748, 0.0035914058250820498, 0.006995103380754364, 0.012191828628688103, 0.01901466240809702, 0.026537099115557586, 0.03314082621704963, 0.03703550525141325] + [0.03755347596120631] * 52 + [0.03703550525141325, 0.03314082621704963, 0.026537099115557586, 0.01901466240809702, 0.012191828628688103, 0.006995103380754364, 0.0035914058250820498, 0.001649984580635748, 0.0006783289402467032, 0.00024954327146837384],
        },
        "q4_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 52 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
        },
        "q4_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 52 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q4_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 52 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q4_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 52 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
        },
        "q4_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00011387933299704621, -0.00027697126662575906, -0.0005944517285705875, -0.0011213812353182428, -0.001848128958101703, -0.00263546230230862, -0.003196922504017968, -0.003186903406174865, -0.002387976428651453, -0.0008895363982413645] + [0.0] * 52 + [0.0008895363982413645, 0.002387976428651453, 0.003186903406174865, 0.003196922504017968, 0.00263546230230862, 0.001848128958101703, 0.0011213812353182428, 0.0005944517285705875, 0.00027697126662575906, 0.00011387933299704621],
        },
        "q4_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00024954327146837384, -0.0006783289402467032, -0.001649984580635748, -0.0035914058250820498, -0.006995103380754364, -0.012191828628688103, -0.01901466240809702, -0.026537099115557586, -0.03314082621704963, -0.03703550525141325] + [-0.03755347596120631] * 52 + [-0.03703550525141325, -0.03314082621704963, -0.026537099115557586, -0.01901466240809702, -0.012191828628688103, -0.006995103380754364, -0.0035914058250820498, -0.001649984580635748, -0.0006783289402467032, -0.00024954327146837384],
        },
        "q5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 16 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0004584594824264715+0j), (0.0012462220801646164+0j), (0.0030313423094871675+0j), (0.006598110404107627+0j), (0.012851364240717448+0j), (0.022398758379862677+0j), (0.034933629886450615+0j), (0.048753807922889233+0j), (0.060886137884025485+0j), (0.06804142010744486+0j)] + [(0.06899303295649696+0j)] * 16 + [(0.06804142010744486+0j), (0.060886137884025485+0j), (0.048753807922889233+0j), (0.034933629886450615+0j), (0.022398758379862677+0j), (0.012851364240717448+0j), (0.006598110404107627+0j), (0.0030313423094871675+0j), (0.0012462220801646164+0j), (0.0004584594824264715+0j)],
        },
        "q5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0009237862108423386+0j), (0.002511111270313765+0j), (0.006108090972458691+0j), (0.013295053636299391+0j), (0.025895228545068077+0j), (0.045133026852869136+0j), (0.0703905291978525+0j), (0.09823789715690813+0j), (0.12268428675750831+0j), (0.13710202988651043+0j)] + [(0.13901950975487745+0j)] * 16 + [(0.13710202988651043+0j), (0.12268428675750831+0j), (0.09823789715690813+0j), (0.0703905291978525+0j), (0.045133026852869136+0j), (0.025895228545068077+0j), (0.013295053636299391+0j), (0.006108090972458691+0j), (0.002511111270313765+0j), (0.0009237862108423386+0j)],
        },
        "q5_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0009241585176275647+0j), (0.0025121233050826573+0j), (0.006110552671591168+0j), (0.01330041184431402+0j), (0.02590566490921722+0j), (0.045151216485857695+0j), (0.07041889817687431+0j), (0.09827748925651797+0j), (0.12273373130632745+0j), (0.13715728511266118+0j)] + [(0.13907553776888446+0j)] * 16 + [(0.13715728511266118+0j), (0.12273373130632745+0j), (0.09827748925651797+0j), (0.07041889817687431+0j), (0.045151216485857695+0j), (0.02590566490921722+0j), (0.01330041184431402+0j), (0.006110552671591168+0j), (0.0025121233050826573+0j), (0.0009241585176275647+0j)],
        },
        "q5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00022789192203926555+0j), (0.000619474470531941+0j), (0.0015068254704029846+0j), (0.0032798014207515514+0j), (0.006388180875097287+0j), (0.011134017932105219+0j), (0.017364875989686557+0j), (0.024234636691285665+0j), (0.030265398622578776+0j), (0.033822160083805515+0j)] + [(0.03429518963062599+0j)] * 16 + [(0.033822160083805515+0j), (0.030265398622578776+0j), (0.024234636691285665+0j), (0.017364875989686557+0j), (0.011134017932105219+0j), (0.006388180875097287+0j), (0.0032798014207515514+0j), (0.0015068254704029846+0j), (0.000619474470531941+0j), (0.00022789192203926555+0j)],
        },
        "q5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00022789192203926555+0j), (-0.000619474470531941+0j), (-0.0015068254704029846+0j), (-0.0032798014207515514+0j), (-0.006388180875097287+0j), (-0.011134017932105219+0j), (-0.017364875989686557+0j), (-0.024234636691285665+0j), (-0.030265398622578776+0j), (-0.033822160083805515+0j)] + [(-0.03429518963062599+0j)] * 16 + [(-0.033822160083805515+0j), (-0.030265398622578776+0j), (-0.024234636691285665+0j), (-0.017364875989686557+0j), (-0.011134017932105219+0j), (-0.006388180875097287+0j), (-0.0032798014207515514+0j), (-0.0015068254704029846+0j), (-0.000619474470531941+0j), (-0.00022789192203926555+0j)],
        },
        "q5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0004562520807894206+0j), (0.00124022174040651+0j), (0.0030167469303251783+0j), (0.006566341664958893+0j), (0.012789487186036074+0j), (0.022290912304449576+0j), (0.034765430613111666+0j), (0.04851906692712695+0j), (0.060592981856959424+0j), (0.06771381265708194+0j)] + [(0.06866084365791984+0j)] * 16 + [(0.06771381265708194+0j), (0.060592981856959424+0j), (0.04851906692712695+0j), (0.034765430613111666+0j), (0.022290912304449576+0j), (0.012789487186036074+0j), (0.006566341664958893+0j), (0.0030167469303251783+0j), (0.00124022174040651+0j), (0.0004562520807894206+0j)],
        },
        "q5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00022879494998169543+0j), (0.0006219291549784388+0j), (0.001512796307332889+0j), (0.003292797723130578+0j), (0.006413494215648757+0j), (0.01117813678113785+0j), (0.01743368478332521+0j), (0.02433066709864296+0j), (0.0303853260881967+0j), (0.03395618131349943+0j)] + [(0.03443108525277117+0j)] * 16 + [(0.03395618131349943+0j), (0.0303853260881967+0j), (0.02433066709864296+0j), (0.01743368478332521+0j), (0.01117813678113785+0j), (0.006413494215648757+0j), (0.003292797723130578+0j), (0.001512796307332889+0j), (0.0006219291549784388+0j), (0.00022879494998169543+0j)],
        },
        "q5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00022879494998169543+0j), (-0.0006219291549784388+0j), (-0.001512796307332889+0j), (-0.003292797723130578+0j), (-0.006413494215648757+0j), (-0.01117813678113785+0j), (-0.01743368478332521+0j), (-0.02433066709864296+0j), (-0.0303853260881967+0j), (-0.03395618131349943+0j)] + [(-0.03443108525277117+0j)] * 16 + [(-0.03395618131349943+0j), (-0.0303853260881967+0j), (-0.02433066709864296+0j), (-0.01743368478332521+0j), (-0.01117813678113785+0j), (-0.006413494215648757+0j), (-0.003292797723130578+0j), (-0.001512796307332889+0j), (-0.0006219291549784388+0j), (-0.00022879494998169543+0j)],
        },
        "q5_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0002116322497055882+0j), (0.00022152472555733233+0j), (0.00023182638627634928+0j), (0.0002425514210706778+0j), (0.00025371437900156645+0j), (0.0002653301719657842+0j), (0.00027741407738961+0j), (0.0002899817406174345+0j), (0.00030304917697762993+0j), (0.000316632773508086+0j), (0.00033074929032356367+0j), (0.00034541586160680176+0j), (0.0003606499962051209+0j), (0.00037646957781409756+0j), (0.0003928928647297427+0j), (0.00040993848915050205+0j), (0.00042762545601032043+0j), (0.00044597314132395206+0j), (0.0004650012900256918+0j), (0.00048473001328270686+0j), (0.0005051797852642122+0j), (0.0005263714393478166+0j), (0.0005483261637444973+0j), (0.0005710654965238277+0j), (0.0005946113200213033+0j), (0.0006189858546098447+0j), (0.0006442116518178811+0j), (0.0006703115867767352+0j), (0.0006973088499804392+0j), (0.0007252269383415348+0j), (0.0007540896455269085+0j), (0.0007839210515582401+0j), (0.0008147455116622282+0j), (0.0008465876443564023+0j), (0.0008794723187570072+0j), (0.000913424641096201+0j), (0.0009484699404365903+0j), (0.0009846337535719808+0j), (0.0010219418091041226+0j), (0.001060420010686185+0j), (0.0011000944194247064+0j), (0.0011409912354328196+0j), (0.0011831367785286922+0j), (0.001226557468074261+0j), (0.0012712798019505992+0j), (0.0013173303346674917+0j), (0.0013647356546061657+0j), (0.0014135223603954597+0j), (0.0014637170364231753+0j), (0.0015153462274858098+0j), (0.00156843641258141+0j), (0.0016230139778518448+0j), (0.0016791051886824084+0j), (0.0017367361609683285+0j), (0.001795932831559449+0j), (0.0018567209278960743+0j), (0.0019191259368507628+0j), (0.0019831730727926213+0j), (0.0020488872448925226+0j), (0.0021162930236895013+0j), (0.0021854146069404785+0j), (0.002256275784777379+0j), (0.002328899904197614+0j), (0.002403309832915866+0j), (0.002479527922607031+0j), (0.002557575971572173+0j), (0.0026374751868612576+0j), (0.0027192461458884535+0j), (0.002802908757577695+0j), (0.0028884822230781683+0j), (0.0029759849960913445+0j), (0.0030654347428530422+0j), (0.003156848301815967+0j), (0.003250241643079993+0j), (0.0033456298276193044+0j), (0.0034430269663573375+0j), (0.0035424461791421944+0j), (0.003643899553676923+0j), (0.003747398104460737+0j), (0.003852951731798837+0j), (0.003960569180940046+0j), (0.004070258001402959+0j), (0.004182024506552713+0j), (0.004295873733491814+0j), (0.004411809403329701+0j), (0.0045298338818969336+0j), (0.004649948140970907+0j), (0.004772151720081022+0j), (0.004896442688962121+0j), (0.0050228176107257345+0j), (0.005151271505819414+0j), (0.005281797816844909+0j), (0.005414388374306468+0j), (0.0055490333633607695+0j), (0.005685721291640265+0j), (0.005824438958221709+0j), (0.005965171423811634+0j), (0.0061079019822202875+0j), (0.006252612133195241+0j), (0.006399281556685365+0j), (0.006547888088605252+0j), (0.006698407698169418+0j), (0.00685081446686466+0j), (0.0070050805691279+0j), (0.00716117625479564+0j), (0.0073190698333897705+0j), (0.007478727660302946+0j), (0.007640114124945111+0j), (0.007803191640910885+0j), (0.007967920638225608+0j), (0.00813425955772565+0j), (0.008302164847626385+0j), (0.008471590962328777+0j), (0.00864249036351295+0j), (0.008814813523564452+0j), (0.008988508931376012+0j), (0.009163523100564659+0j), (0.009339800580140932+0j), (0.009517283967663631+0j), (0.009695913924910246+0j), (0.00987562919608963+0j), (0.01005636662861992+0j), (0.010238061196490983+0j), (0.010420646026226776+0j), (0.010604052425459157+0j), (0.010788209914120613+0j), (0.01097304625825923+0j), (0.011158487506475174+0j), (0.011344458028973457+0j), (0.011530880559223706+0j), (0.011717676238213034+0j), (0.011904764661273846+0j), (0.012092063927463847+0j), (0.012279490691471025+0j), (0.012466960218011925+0j), (0.012654386438686892+0j), (0.01284168201125147+0j), (0.013028758381258632+0j), (0.013215525846021911+0j), (0.013401893620845078+0j), (0.01358776990745951+0j), (0.013773061964605966+0j), (0.013957676180693141+0j), (0.014141518148461043+0j), (0.014324492741573014+0j), (0.014506504193056066+0j), (0.014687456175505155+0j), (0.01486725188296304+0j), (0.015045794114383539+0j), (0.015222985358582332+0j), (0.01539872788057575+0j), (0.01557292380920465+0j), (0.015745475225937135+0j), (0.015916284254740735+0j), (0.016085253152911663+0j), (0.016252284402746005+0j), (0.016417280803935067+0j), (0.0165801455665646+0j), (0.016740782404595506+0j), (0.016899095629701516+0j), (0.01705499024533748+0j), (0.017208372040910386+0j), (0.01735914768592377+0j), (0.017507224823965047+0j), (0.017652512166404264+0j), (0.017794919585672305+0j), (0.017934358207985803+0j), (0.018070740505386054+0j), (0.0182039803869591+0j), (0.018333993289104497+0j), (0.018460696264720668+0j), (0.018584008071175728+0j), (0.018703849256933393+0j), (0.018820142246705075+0j), (0.01893281142500061+0j), (0.019041783217951913+0j), (0.01914698617328576+0j), (0.01924835103832416+0j), (0.019345810835893318+0j), (0.019439300938024675+0j), (0.019528759137334734+0j), (0.019614125715973253+0j), (0.019695343512032965+0j), (0.01977235798331742+0j), (0.01984511726836745+0j), (0.019913572244650634+0j), (0.01997767658382249+0j), (0.02003738680397223+0j), (0.020092662318770747+0j), (0.020143465483442983+0j), (0.02018976163749186+0j), (0.020231519144105797+0j), (0.020268709426187224+0j), (0.020301306998944536+0j), (0.02032928949899553+0j), (0.02035263770993576+0j), (0.02037133558433091+0j), (0.020385370262097947+0j), (0.020394732085245545+0j), (0.02039941460895021+0j)] + [(0.0204+0j)] * 1360 + [(0.02039941460895021+0j), (0.020394732085245545+0j), (0.020385370262097947+0j), (0.02037133558433091+0j), (0.02035263770993576+0j), (0.02032928949899553+0j), (0.020301306998944536+0j), (0.020268709426187224+0j), (0.020231519144105797+0j), (0.02018976163749186+0j), (0.020143465483442983+0j), (0.020092662318770747+0j), (0.02003738680397223+0j), (0.01997767658382249+0j), (0.019913572244650634+0j), (0.01984511726836745+0j), (0.01977235798331742+0j), (0.019695343512032965+0j), (0.019614125715973253+0j), (0.019528759137334734+0j), (0.019439300938024675+0j), (0.019345810835893318+0j), (0.01924835103832416+0j), (0.01914698617328576+0j), (0.019041783217951913+0j), (0.01893281142500061+0j), (0.018820142246705075+0j), (0.018703849256933393+0j), (0.018584008071175728+0j), (0.018460696264720668+0j), (0.018333993289104497+0j), (0.0182039803869591+0j), (0.018070740505386054+0j), (0.017934358207985803+0j), (0.017794919585672305+0j), (0.017652512166404264+0j), (0.017507224823965047+0j), (0.01735914768592377+0j), (0.017208372040910386+0j), (0.01705499024533748+0j), (0.016899095629701516+0j), (0.016740782404595506+0j), (0.0165801455665646+0j), (0.016417280803935067+0j), (0.016252284402746005+0j), (0.016085253152911663+0j), (0.015916284254740735+0j), (0.015745475225937135+0j), (0.01557292380920465+0j), (0.01539872788057575+0j), (0.015222985358582332+0j), (0.015045794114383539+0j), (0.01486725188296304+0j), (0.014687456175505155+0j), (0.014506504193056066+0j), (0.014324492741573014+0j), (0.014141518148461043+0j), (0.013957676180693141+0j), (0.013773061964605966+0j), (0.01358776990745951+0j), (0.013401893620845078+0j), (0.013215525846021911+0j), (0.013028758381258632+0j), (0.01284168201125147+0j), (0.012654386438686892+0j), (0.012466960218011925+0j), (0.012279490691471025+0j), (0.012092063927463847+0j), (0.011904764661273846+0j), (0.011717676238213034+0j), (0.011530880559223706+0j), (0.011344458028973457+0j), (0.011158487506475174+0j), (0.01097304625825923+0j), (0.010788209914120613+0j), (0.010604052425459157+0j), (0.010420646026226776+0j), (0.010238061196490983+0j), (0.01005636662861992+0j), (0.00987562919608963+0j), (0.009695913924910246+0j), (0.009517283967663631+0j), (0.009339800580140932+0j), (0.009163523100564659+0j), (0.008988508931376012+0j), (0.008814813523564452+0j), (0.00864249036351295+0j), (0.008471590962328777+0j), (0.008302164847626385+0j), (0.00813425955772565+0j), (0.007967920638225608+0j), (0.007803191640910885+0j), (0.007640114124945111+0j), (0.007478727660302946+0j), (0.0073190698333897705+0j), (0.00716117625479564+0j), (0.0070050805691279+0j), (0.00685081446686466+0j), (0.006698407698169418+0j), (0.006547888088605252+0j), (0.006399281556685365+0j), (0.006252612133195241+0j), (0.0061079019822202875+0j), (0.005965171423811634+0j), (0.005824438958221709+0j), (0.005685721291640265+0j), (0.0055490333633607695+0j), (0.005414388374306468+0j), (0.005281797816844909+0j), (0.005151271505819414+0j), (0.0050228176107257345+0j), (0.004896442688962121+0j), (0.004772151720081022+0j), (0.004649948140970907+0j), (0.0045298338818969336+0j), (0.004411809403329701+0j), (0.004295873733491814+0j), (0.004182024506552713+0j), (0.004070258001402959+0j), (0.003960569180940046+0j), (0.003852951731798837+0j), (0.003747398104460737+0j), (0.003643899553676923+0j), (0.0035424461791421944+0j), (0.0034430269663573375+0j), (0.0033456298276193044+0j), (0.003250241643079993+0j), (0.003156848301815967+0j), (0.0030654347428530422+0j), (0.0029759849960913445+0j), (0.0028884822230781683+0j), (0.002802908757577695+0j), (0.0027192461458884535+0j), (0.0026374751868612576+0j), (0.002557575971572173+0j), (0.002479527922607031+0j), (0.002403309832915866+0j), (0.002328899904197614+0j), (0.002256275784777379+0j), (0.0021854146069404785+0j), (0.0021162930236895013+0j), (0.0020488872448925226+0j), (0.0019831730727926213+0j), (0.0019191259368507628+0j), (0.0018567209278960743+0j), (0.001795932831559449+0j), (0.0017367361609683285+0j), (0.0016791051886824084+0j), (0.0016230139778518448+0j), (0.00156843641258141+0j), (0.0015153462274858098+0j), (0.0014637170364231753+0j), (0.0014135223603954597+0j), (0.0013647356546061657+0j), (0.0013173303346674917+0j), (0.0012712798019505992+0j), (0.001226557468074261+0j), (0.0011831367785286922+0j), (0.0011409912354328196+0j), (0.0011000944194247064+0j), (0.001060420010686185+0j), (0.0010219418091041226+0j), (0.0009846337535719808+0j), (0.0009484699404365903+0j), (0.000913424641096201+0j), (0.0008794723187570072+0j), (0.0008465876443564023+0j), (0.0008147455116622282+0j), (0.0007839210515582401+0j), (0.0007540896455269085+0j), (0.0007252269383415348+0j), (0.0006973088499804392+0j), (0.0006703115867767352+0j), (0.0006442116518178811+0j), (0.0006189858546098447+0j), (0.0005946113200213033+0j), (0.0005710654965238277+0j), (0.0005483261637444973+0j), (0.0005263714393478166+0j), (0.0005051797852642122+0j), (0.00048473001328270686+0j), (0.0004650012900256918+0j), (0.00044597314132395206+0j), (0.00042762545601032043+0j), (0.00040993848915050205+0j), (0.0003928928647297427+0j), (0.00037646957781409756+0j), (0.0003606499962051209+0j), (0.00034541586160680176+0j), (0.00033074929032356367+0j), (0.000316632773508086+0j), (0.00030304917697762993+0j), (0.0002899817406174345+0j), (0.00027741407738961+0j), (0.0002653301719657842+0j), (0.00025371437900156645+0j), (0.0002425514210706778+0j), (0.00023182638627634928+0j), (0.00022152472555733233+0j), (0.0002116322497055882+0j)],
        },
        "q5_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004584594824264715, 0.0012462220801646164, 0.0030313423094871675, 0.006598110404107627, 0.012851364240717448, 0.022398758379862677, 0.034933629886450615, 0.048753807922889233, 0.060886137884025485, 0.06804142010744486] + [0.06899303295649696] * 16 + [0.06804142010744486, 0.060886137884025485, 0.048753807922889233, 0.034933629886450615, 0.022398758379862677, 0.012851364240717448, 0.006598110404107627, 0.0030313423094871675, 0.0012462220801646164, 0.0004584594824264715],
        },
        "q5_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002492222566622028, -0.0006061451387395355, -0.0013009437039374983, -0.002454116604739071, -0.004044586997649687, -0.00576764760596688, -0.006996390125030008, -0.0069744635637439285, -0.005226030560085027, -0.001946729601574247] + [0.0] * 16 + [0.001946729601574247, 0.005226030560085027, 0.0069744635637439285, 0.006996390125030008, 0.00576764760596688, 0.004044586997649687, 0.002454116604739071, 0.0013009437039374983, 0.0006061451387395355, 0.0002492222566622028],
        },
        "q5_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00022789192203926555, 0.000619474470531941, 0.0015068254704029846, 0.0032798014207515514, 0.006388180875097287, 0.011134017932105219, 0.017364875989686557, 0.024234636691285665, 0.030265398622578776, 0.033822160083805515] + [0.03429518963062599] * 16 + [0.033822160083805515, 0.030265398622578776, 0.024234636691285665, 0.017364875989686557, 0.011134017932105219, 0.006388180875097287, 0.0032798014207515514, 0.0015068254704029846, 0.000619474470531941, 0.00022789192203926555],
        },
        "q5_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0001238838790837346, -0.00030130379236787715, -0.0006466756006137288, -0.001219897005952234, -0.0020104910904470996, -0.002866993374446708, -0.003477779071098921, -0.003466879773807152, -0.002597765330690322, -0.0009676840977209827] + [0.0] * 16 + [0.0009676840977209827, 0.002597765330690322, 0.003466879773807152, 0.003477779071098921, 0.002866993374446708, 0.0020104910904470996, 0.001219897005952234, 0.0006466756006137288, 0.00030130379236787715, 0.0001238838790837346],
        },
        "q5_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00022789192203926555, -0.000619474470531941, -0.0015068254704029846, -0.0032798014207515514, -0.006388180875097287, -0.011134017932105219, -0.017364875989686557, -0.024234636691285665, -0.030265398622578776, -0.033822160083805515] + [-0.03429518963062599] * 16 + [-0.033822160083805515, -0.030265398622578776, -0.024234636691285665, -0.017364875989686557, -0.011134017932105219, -0.006388180875097287, -0.0032798014207515514, -0.0015068254704029846, -0.000619474470531941, -0.00022789192203926555],
        },
        "q5_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0001238838790837346, 0.00030130379236787715, 0.0006466756006137288, 0.001219897005952234, 0.0020104910904470996, 0.002866993374446708, 0.003477779071098921, 0.003466879773807152, 0.002597765330690322, 0.0009676840977209827] + [0.0] * 16 + [-0.0009676840977209827, -0.002597765330690322, -0.003466879773807152, -0.003477779071098921, -0.002866993374446708, -0.0020104910904470996, -0.001219897005952234, -0.0006466756006137288, -0.00030130379236787715, -0.0001238838790837346],
        },
        "q5_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002480222954040475, 0.000603226656686416, 0.0012946798892017146, 0.002442300465650523, 0.004025113023826409, 0.005739877398881272, 0.00696270373919347, 0.006940882750436988, 0.00520086814365391, 0.0019373564415151143] + [0.0] * 16 + [-0.0019373564415151143, -0.00520086814365391, -0.006940882750436988, -0.00696270373919347, -0.005739877398881272, -0.004025113023826409, -0.002442300465650523, -0.0012946798892017146, -0.000603226656686416, -0.0002480222954040475],
        },
        "q5_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0004562520807894206, 0.00124022174040651, 0.0030167469303251783, 0.006566341664958893, 0.012789487186036074, 0.022290912304449576, 0.034765430613111666, 0.04851906692712695, 0.060592981856959424, 0.06771381265708194] + [0.06866084365791984] * 16 + [0.06771381265708194, 0.060592981856959424, 0.04851906692712695, 0.034765430613111666, 0.022290912304449576, 0.012789487186036074, 0.006566341664958893, 0.0030167469303251783, 0.00124022174040651, 0.0004562520807894206],
        },
        "q5_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0001243747723257072, 0.0003024977168441533, 0.0006492380702783674, 0.0012247308810339125, 0.002018457716102077, 0.0028783539137090023, 0.003491559865304777, 0.0034806173792509007, 0.0026080590465030517, 0.0009715185722906277] + [0.0] * 16 + [-0.0009715185722906277, -0.0026080590465030517, -0.0034806173792509007, -0.003491559865304777, -0.0028783539137090023, -0.002018457716102077, -0.0012247308810339125, -0.0006492380702783674, -0.0003024977168441533, -0.0001243747723257072],
        },
        "q5_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00022879494998169543, 0.0006219291549784388, 0.001512796307332889, 0.003292797723130578, 0.006413494215648757, 0.01117813678113785, 0.01743368478332521, 0.02433066709864296, 0.0303853260881967, 0.03395618131349943] + [0.03443108525277117] * 16 + [0.03395618131349943, 0.0303853260881967, 0.02433066709864296, 0.01743368478332521, 0.01117813678113785, 0.006413494215648757, 0.003292797723130578, 0.001512796307332889, 0.0006219291549784388, 0.00022879494998169543],
        },
        "q5_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005023799923555449, 0.0012218619406013165, 0.0026224306640677134, 0.004946986266958927, 0.008153042236972684, 0.011626372375411373, 0.014103260537813954, 0.01405906117199963, 0.01053458558632632, 0.003924200091337616] + [0.0] * 16 + [-0.003924200091337616, -0.01053458558632632, -0.01405906117199963, -0.014103260537813954, -0.011626372375411373, -0.008153042236972684, -0.004946986266958927, -0.0026224306640677134, -0.0012218619406013165, -0.0005023799923555449],
        },
        "q5_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009241585176275647, 0.0025121233050826573, 0.006110552671591168, 0.01330041184431402, 0.02590566490921722, 0.045151216485857695, 0.07041889817687431, 0.09827748925651797, 0.12273373130632745, 0.13715728511266118] + [0.13907553776888446] * 16 + [0.13715728511266118, 0.12273373130632745, 0.09827748925651797, 0.07041889817687431, 0.045151216485857695, 0.02590566490921722, 0.01330041184431402, 0.006110552671591168, 0.0025121233050826573, 0.0009241585176275647],
        },
        "q5_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009237862108423386, 0.002511111270313765, 0.006108090972458691, 0.013295053636299391, 0.025895228545068077, 0.045133026852869136, 0.0703905291978525, 0.09823789715690813, 0.12268428675750831, 0.13710202988651043] + [0.13901950975487745] * 16 + [0.13710202988651043, 0.12268428675750831, 0.09823789715690813, 0.0703905291978525, 0.045133026852869136, 0.025895228545068077, 0.013295053636299391, 0.006108090972458691, 0.002511111270313765, 0.0009237862108423386],
        },
        "q5_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005021776033969969, -0.0012213697009233627, -0.0026213741908421855, -0.004944993322546817, -0.008149757699864426, -0.011621688571453107, -0.014097578893927232, -0.014053397334283041, -0.010530341619930378, -0.003922619186879429] + [0.0] * 16 + [0.003922619186879429, 0.010530341619930378, 0.014053397334283041, 0.014097578893927232, 0.011621688571453107, 0.008149757699864426, 0.004944993322546817, 0.0026213741908421855, 0.0012213697009233627, 0.0005021776033969969],
        },
        "q5_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0001243747723257072, -0.0003024977168441533, -0.0006492380702783674, -0.0012247308810339125, -0.002018457716102077, -0.0028783539137090023, -0.003491559865304777, -0.0034806173792509007, -0.0026080590465030517, -0.0009715185722906277] + [0.0] * 16 + [0.0009715185722906277, 0.0026080590465030517, 0.0034806173792509007, 0.003491559865304777, 0.0028783539137090023, 0.002018457716102077, 0.0012247308810339125, 0.0006492380702783674, 0.0003024977168441533, 0.0001243747723257072],
        },
        "q5_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00022879494998169543, -0.0006219291549784388, -0.001512796307332889, -0.003292797723130578, -0.006413494215648757, -0.01117813678113785, -0.01743368478332521, -0.02433066709864296, -0.0303853260881967, -0.03395618131349943] + [-0.03443108525277117] * 16 + [-0.03395618131349943, -0.0303853260881967, -0.02433066709864296, -0.01743368478332521, -0.01117813678113785, -0.006413494215648757, -0.003292797723130578, -0.001512796307332889, -0.0006219291549784388, -0.00022879494998169543],
        },
        "q6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0013108726096250905+0j), (0.003563321194168571+0j), (0.008667513174496726+0j), (0.018865968609154488+0j), (0.036745889277519136+0j), (0.06404474108457679+0j), (0.09988568309364833+0j), (0.13940170041370717+0j), (0.17409165589856954+0j), (0.1945507451754984+0j)] + [(0.1972716905733063+0j)] * 32 + [(0.1945507451754984+0j), (0.17409165589856954+0j), (0.13940170041370717+0j), (0.09988568309364833+0j), (0.06404474108457679+0j), (0.036745889277519136+0j), (0.018865968609154488+0j), (0.008667513174496726+0j), (0.003563321194168571+0j), (0.0013108726096250905+0j)],
        },
        "q6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q6_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006375492758954594+0j), (0.0017330386114138498+0j), (0.004215487231665607+0j), (0.009175555685211025+0j), (0.017871542153678276+0j), (0.03114847163910304+0j), (0.04857988828288349+0j), (0.06779869569688633+0j), (0.08467032444084573+0j), (0.09462070211920537+0j)] + [(0.09594404716081062+0j)] * 32 + [(0.09462070211920537+0j), (0.08467032444084573+0j), (0.06779869569688633+0j), (0.04857988828288349+0j), (0.03114847163910304+0j), (0.017871542153678276+0j), (0.009175555685211025+0j), (0.004215487231665607+0j), (0.0017330386114138498+0j), (0.0006375492758954594+0j)],
        },
        "q6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0006375492758954594+0j), (-0.0017330386114138498+0j), (-0.004215487231665607+0j), (-0.009175555685211025+0j), (-0.017871542153678276+0j), (-0.03114847163910304+0j), (-0.04857988828288349+0j), (-0.06779869569688633+0j), (-0.08467032444084573+0j), (-0.09462070211920537+0j)] + [(-0.09594404716081062+0j)] * 32 + [(-0.09462070211920537+0j), (-0.08467032444084573+0j), (-0.06779869569688633+0j), (-0.04857988828288349+0j), (-0.03114847163910304+0j), (-0.017871542153678276+0j), (-0.009175555685211025+0j), (-0.004215487231665607+0j), (-0.0017330386114138498+0j), (-0.0006375492758954594+0j)],
        },
        "q6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0013091869210360456+0j), (0.0035587390175085298+0j), (0.0086563673713528+0j), (0.018841708320418402+0j), (0.03669863668730205+0j), (0.06396238411987869+0j), (0.0997572372363136+0j), (0.13922243977926+0j), (0.17386778645798365+0j), (0.1943005668067351+0j)] + [(0.19701801326301746+0j)] * 32 + [(0.1943005668067351+0j), (0.17386778645798365+0j), (0.13922243977926+0j), (0.0997572372363136+0j), (0.06396238411987869+0j), (0.03669863668730205+0j), (0.018841708320418402+0j), (0.0086563673713528+0j), (0.0035587390175085298+0j), (0.0013091869210360456+0j)],
        },
        "q6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006407333543414328+0j), (0.0017416938339939274+0j), (0.00423654041538191+0j), (0.00922138067504585+0j), (0.01796079704631055+0j), (0.03130403479464389+0j), (0.04882250823562685+0j), (0.06813729911750878+0j), (0.08509318893973015+0j), (0.0950932612602027+0j)] + [(0.0964232154135784+0j)] * 32 + [(0.0950932612602027+0j), (0.08509318893973015+0j), (0.06813729911750878+0j), (0.04882250823562685+0j), (0.03130403479464389+0j), (0.01796079704631055+0j), (0.00922138067504585+0j), (0.00423654041538191+0j), (0.0017416938339939274+0j), (0.0006407333543414328+0j)],
        },
        "q6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0006407333543414328+0j), (-0.0017416938339939274+0j), (-0.00423654041538191+0j), (-0.00922138067504585+0j), (-0.01796079704631055+0j), (-0.03130403479464389+0j), (-0.04882250823562685+0j), (-0.06813729911750878+0j), (-0.08509318893973015+0j), (-0.0950932612602027+0j)] + [(-0.0964232154135784+0j)] * 32 + [(-0.0950932612602027+0j), (-0.08509318893973015+0j), (-0.06813729911750878+0j), (-0.04882250823562685+0j), (-0.03130403479464389+0j), (-0.01796079704631055+0j), (-0.00922138067504585+0j), (-0.00423654041538191+0j), (-0.0017416938339939274+0j), (-0.0006407333543414328+0j)],
        },
        "q6_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0003942169357260957+0j), (0.0004126440966264034+0j), (0.0004318334646324154+0j), (0.0004518114706218509+0j), (0.0004726052157872317+0j), (0.0004942424771911667+0j), (0.0005167517127845677+0j), (0.0005401620658560055+0j), (0.0005645033688798989+0j), (0.0005898061467307485+0j), (0.0006161016192301677+0j), (0.0006434217029930621+0j), (0.0006717990125389507+0j), (0.0007012668606341033+0j), (0.000731859257829913+0j), (0.0007636109111626999+0j), (0.0007965572219800087+0j), (0.0008307342828583421+0j), (0.0008661788735772692+0j), (0.0009029284561148462+0j), (0.0009410211686294149+0j), (0.000980495818392992+0j), (0.0010213918736417106+0j), (0.0010637494543090911+0j), (0.0011076093216083101+0j), (0.001153012866430103+0j), (0.0012000020965235042+0j), (0.001248619622427252+0j), (0.0012989086421204262+0j), (0.0013509129243616826+0j), (0.0014046767906873787+0j), (0.0014602450960398592+0j), (0.0015176632079982684+0j), (0.0015769769845854554+0j), (0.0016382327506257977+0j), (0.0017014772726301785+0j), (0.0017667577321858056+0j), (0.0018341216978301604+0j), (0.0019036170953900323+0j), (0.0019752921767683842+0j), (0.002049195487163669+0j), (0.0021253758307081933+0j), (0.002203882234514231+0j), (0.002284763911118722+0j), (0.002368070219319744+0j), (0.0024538506234002295+0j), (0.0025421546507369756+0j), (0.0026330318477954646+0j), (0.002726531734513758+0j), (0.0028227037570814108+0j), (0.0029215972391222348+0j), (0.0030232613312926528+0j), (0.003127744959310369+0j), (0.0032350967704312004+0j), (0.0033453650783950525+0j), (0.0034585978068652364+0j), (0.0035748424313886765+0j), (0.0036941459199078246+0j), (0.003816554671858621+0j), (0.003942114455892209+0j), (0.004070870346261676+0j), (0.004202866657918648+0j), (0.004338146880368105+0j), (0.004476753610333476+0j), (0.004618728483287608+0j), (0.004764112103908949+0j), (0.004912943975525872+0j), (0.005065262428615747+0j), (0.00522110454842904+0j), (0.005380506101812275+0j), (0.0055435014633074065+0j), (0.005710123540608609+0j), (0.005880403699461116+0j), (0.006054371688090183+0j), (0.006232055561251646+0j), (0.006413481603998962+0j), (0.006598674255264872+0j), (0.006787656031358974+0j), (0.006980447449485687+0j), (0.007177066951389991+0j), (0.007377530827241263+0j), (0.007581853139868257+0j), (0.007790045649460937+0j), (0.008002117738857301+0j), (0.008218076339535718+0j), (0.008437925858435466+0j), (0.008661668105730122+0j), (0.008889302223680336+0j), (0.009120824616694147+0j), (0.009356228882724409+0j), (0.009595505746134202+0j), (0.009838642992162087+0j), (0.010085625403119892+0j), (0.010336434696456337+0j), (0.010591049464820102+0j), (0.010849445118256126+0j), (0.011111593828668732+0j), (0.01137746447668485+0j), (0.01164702260104996+0j), (0.011920230350688425+0j), (0.012197046439558802+0j), (0.012477426104433231+0j), (0.01276132106572829+0j), (0.013048679491512756+0j), (0.013339445964815408+0j), (0.013633561454353495+0j), (0.013930963288799607+0j), (0.014231585134701678+0j), (0.014535356978167338+0j), (0.014842205110420252+0j), (0.015152052117332095+0j), (0.01546481687302954+0j), (0.01578041453767125+0j), (0.01609875655948491+0j), (0.01641975068114947+0j), (0.016743300950602377+0j), (0.017069307736345934+0j), (0.017397667747321346+0j), (0.017728274057412646+0j), (0.018061016134636735+0j), (0.018395779875068918+0j), (0.018732447641546912+0j), (0.019070898307189086+0j), (0.01941100730375576+0j), (0.019752646674874905+0j), (0.020095685134146238+0j), (0.02043998812812994+0j), (0.020785417904218464+0j), (0.021131833583381932+0j), (0.02147909123776965+0j), (0.02182704397314193+0j), (0.022175542016098344+0j), (0.022524432806060108+0j), (0.022873561091955832+0j), (0.023222769033551627+0j), (0.023571896307357936+0j), (0.023920780217037054+0j), (0.024269255808226867+0j), (0.024617155987687874+0j), (0.024964311646672205+0j), (0.025310551788404974+0j), (0.025655703659560134+0j), (0.025999592885604873+0j), (0.026342043609878414+0j), (0.026682878636263462+0j), (0.027021919575300517+0j), (0.027358986993588037+0j), (0.027693900566303702+0j), (0.028026479232675223+0j), (0.028356541354221994+0j), (0.028683904875582283+0j), (0.029008387487734155+0j), (0.029329806793412315+0j), (0.029647980474517055+0j), (0.02996272646130604+0j), (0.030273863103154327+0j), (0.030581209340663364+0j), (0.030884584878894845+0j), (0.03118381036150144+0j), (0.031478707545522434+0j), (0.03176909947660903+0j), (0.032054810664440915+0j), (0.0323356672580933+0j), (0.03261149722111136+0j), (0.032882130506047165+0j), (0.033147399228213116+0j), (0.03340713783840493+0j), (0.03366118329434657+0j), (0.0339093752306101+0j), (0.03415155612676328+0j), (0.03438757147349929+0j), (0.034617269936503804+0j), (0.034840503517817104+0j), (0.03505712771445063+0j), (0.03526700167402075+0j), (0.03546998834716533+0j), (0.03566595463651269+0j), (0.03585477154197638+0j), (0.03603631430215422+0j), (0.03621046253161459+0j), (0.03637710035385882+0j), (0.0365361165297541+0j), (0.03668740458123788+0j), (0.036830862910101084+0j), (0.036966394911664854+0j), (0.037093909083172755+0j), (0.03721331912672817+0j), (0.03732454404661494+0j), (0.03742750824084747+0j), (0.037522141586805564+0j), (0.03760837952081817+0j), (0.03768616311156962+0j), (0.0377554391272115+0j), (0.03781616009607316+0j), (0.037868284360874034+0j), (0.03791177612635093+0j), (0.03794660550022425+0j), (0.03797274852743736+0j), (0.037990187217614255+0j), (0.037998909565691574+0j)] + [(0.038000000000000006+0j)] * 640 + [(0.037998909565691574+0j), (0.037990187217614255+0j), (0.03797274852743736+0j), (0.03794660550022425+0j), (0.03791177612635093+0j), (0.037868284360874034+0j), (0.03781616009607316+0j), (0.0377554391272115+0j), (0.03768616311156962+0j), (0.03760837952081817+0j), (0.037522141586805564+0j), (0.03742750824084747+0j), (0.03732454404661494+0j), (0.03721331912672817+0j), (0.037093909083172755+0j), (0.036966394911664854+0j), (0.036830862910101084+0j), (0.03668740458123788+0j), (0.0365361165297541+0j), (0.03637710035385882+0j), (0.03621046253161459+0j), (0.03603631430215422+0j), (0.03585477154197638+0j), (0.03566595463651269+0j), (0.03546998834716533+0j), (0.03526700167402075+0j), (0.03505712771445063+0j), (0.034840503517817104+0j), (0.034617269936503804+0j), (0.03438757147349929+0j), (0.03415155612676328+0j), (0.0339093752306101+0j), (0.03366118329434657+0j), (0.03340713783840493+0j), (0.033147399228213116+0j), (0.032882130506047165+0j), (0.03261149722111136+0j), (0.0323356672580933+0j), (0.032054810664440915+0j), (0.03176909947660903+0j), (0.031478707545522434+0j), (0.03118381036150144+0j), (0.030884584878894845+0j), (0.030581209340663364+0j), (0.030273863103154327+0j), (0.02996272646130604+0j), (0.029647980474517055+0j), (0.029329806793412315+0j), (0.029008387487734155+0j), (0.028683904875582283+0j), (0.028356541354221994+0j), (0.028026479232675223+0j), (0.027693900566303702+0j), (0.027358986993588037+0j), (0.027021919575300517+0j), (0.026682878636263462+0j), (0.026342043609878414+0j), (0.025999592885604873+0j), (0.025655703659560134+0j), (0.025310551788404974+0j), (0.024964311646672205+0j), (0.024617155987687874+0j), (0.024269255808226867+0j), (0.023920780217037054+0j), (0.023571896307357936+0j), (0.023222769033551627+0j), (0.022873561091955832+0j), (0.022524432806060108+0j), (0.022175542016098344+0j), (0.02182704397314193+0j), (0.02147909123776965+0j), (0.021131833583381932+0j), (0.020785417904218464+0j), (0.02043998812812994+0j), (0.020095685134146238+0j), (0.019752646674874905+0j), (0.01941100730375576+0j), (0.019070898307189086+0j), (0.018732447641546912+0j), (0.018395779875068918+0j), (0.018061016134636735+0j), (0.017728274057412646+0j), (0.017397667747321346+0j), (0.017069307736345934+0j), (0.016743300950602377+0j), (0.01641975068114947+0j), (0.01609875655948491+0j), (0.01578041453767125+0j), (0.01546481687302954+0j), (0.015152052117332095+0j), (0.014842205110420252+0j), (0.014535356978167338+0j), (0.014231585134701678+0j), (0.013930963288799607+0j), (0.013633561454353495+0j), (0.013339445964815408+0j), (0.013048679491512756+0j), (0.01276132106572829+0j), (0.012477426104433231+0j), (0.012197046439558802+0j), (0.011920230350688425+0j), (0.01164702260104996+0j), (0.01137746447668485+0j), (0.011111593828668732+0j), (0.010849445118256126+0j), (0.010591049464820102+0j), (0.010336434696456337+0j), (0.010085625403119892+0j), (0.009838642992162087+0j), (0.009595505746134202+0j), (0.009356228882724409+0j), (0.009120824616694147+0j), (0.008889302223680336+0j), (0.008661668105730122+0j), (0.008437925858435466+0j), (0.008218076339535718+0j), (0.008002117738857301+0j), (0.007790045649460937+0j), (0.007581853139868257+0j), (0.007377530827241263+0j), (0.007177066951389991+0j), (0.006980447449485687+0j), (0.006787656031358974+0j), (0.006598674255264872+0j), (0.006413481603998962+0j), (0.006232055561251646+0j), (0.006054371688090183+0j), (0.005880403699461116+0j), (0.005710123540608609+0j), (0.0055435014633074065+0j), (0.005380506101812275+0j), (0.00522110454842904+0j), (0.005065262428615747+0j), (0.004912943975525872+0j), (0.004764112103908949+0j), (0.004618728483287608+0j), (0.004476753610333476+0j), (0.004338146880368105+0j), (0.004202866657918648+0j), (0.004070870346261676+0j), (0.003942114455892209+0j), (0.003816554671858621+0j), (0.0036941459199078246+0j), (0.0035748424313886765+0j), (0.0034585978068652364+0j), (0.0033453650783950525+0j), (0.0032350967704312004+0j), (0.003127744959310369+0j), (0.0030232613312926528+0j), (0.0029215972391222348+0j), (0.0028227037570814108+0j), (0.002726531734513758+0j), (0.0026330318477954646+0j), (0.0025421546507369756+0j), (0.0024538506234002295+0j), (0.002368070219319744+0j), (0.002284763911118722+0j), (0.002203882234514231+0j), (0.0021253758307081933+0j), (0.002049195487163669+0j), (0.0019752921767683842+0j), (0.0019036170953900323+0j), (0.0018341216978301604+0j), (0.0017667577321858056+0j), (0.0017014772726301785+0j), (0.0016382327506257977+0j), (0.0015769769845854554+0j), (0.0015176632079982684+0j), (0.0014602450960398592+0j), (0.0014046767906873787+0j), (0.0013509129243616826+0j), (0.0012989086421204262+0j), (0.001248619622427252+0j), (0.0012000020965235042+0j), (0.001153012866430103+0j), (0.0011076093216083101+0j), (0.0010637494543090911+0j), (0.0010213918736417106+0j), (0.000980495818392992+0j), (0.0009410211686294149+0j), (0.0009029284561148462+0j), (0.0008661788735772692+0j), (0.0008307342828583421+0j), (0.0007965572219800087+0j), (0.0007636109111626999+0j), (0.000731859257829913+0j), (0.0007012668606341033+0j), (0.0006717990125389507+0j), (0.0006434217029930621+0j), (0.0006161016192301677+0j), (0.0005898061467307485+0j), (0.0005645033688798989+0j), (0.0005401620658560055+0j), (0.0005167517127845677+0j), (0.0004942424771911667+0j), (0.0004726052157872317+0j), (0.0004518114706218509+0j), (0.0004318334646324154+0j), (0.0004126440966264034+0j), (0.0003942169357260957+0j)],
        },
        "q6_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0013108726096250905, 0.003563321194168571, 0.008667513174496726, 0.018865968609154488, 0.036745889277519136, 0.06404474108457679, 0.09988568309364833, 0.13940170041370717, 0.17409165589856954, 0.1945507451754984] + [0.1972716905733063] * 32 + [0.1945507451754984, 0.17409165589856954, 0.13940170041370717, 0.09988568309364833, 0.06404474108457679, 0.036745889277519136, 0.018865968609154488, 0.008667513174496726, 0.003563321194168571, 0.0013108726096250905],
        },
        "q6_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.001128538420722338, -0.002744771220528726, -0.005890986514419745, -0.011112831231339746, -0.018314864346118134, -0.026117297899854855, -0.03168134005447432, -0.03158205130242999, -0.023664725429875674, -0.00881526064147552] + [0.0] * 32 + [0.00881526064147552, 0.023664725429875674, 0.03158205130242999, 0.03168134005447432, 0.026117297899854855, 0.018314864346118134, 0.011112831231339746, 0.005890986514419745, 0.002744771220528726, 0.001128538420722338],
        },
        "q6_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006375492758954594, 0.0017330386114138498, 0.004215487231665607, 0.009175555685211025, 0.017871542153678276, 0.03114847163910304, 0.04857988828288349, 0.06779869569688633, 0.08467032444084573, 0.09462070211920537] + [0.09594404716081062] * 32 + [0.09462070211920537, 0.08467032444084573, 0.06779869569688633, 0.04857988828288349, 0.03114847163910304, 0.017871542153678276, 0.009175555685211025, 0.004215487231665607, 0.0017330386114138498, 0.0006375492758954594],
        },
        "q6_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005488701553978678, -0.0013349328464855672, -0.0028651099725490355, -0.00540477957405442, -0.00890752344373928, -0.012702274990062283, -0.015408373981438723, -0.015360084413477932, -0.011509454428525369, -0.004287344931564196] + [0.0] * 32 + [0.004287344931564196, 0.011509454428525369, 0.015360084413477932, 0.015408373981438723, 0.012702274990062283, 0.00890752344373928, 0.00540477957405442, 0.0028651099725490355, 0.0013349328464855672, 0.0005488701553978678],
        },
        "q6_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006375492758954594, -0.0017330386114138498, -0.004215487231665607, -0.009175555685211025, -0.017871542153678276, -0.03114847163910304, -0.04857988828288349, -0.06779869569688633, -0.08467032444084573, -0.09462070211920537] + [-0.09594404716081062] * 32 + [-0.09462070211920537, -0.08467032444084573, -0.06779869569688633, -0.04857988828288349, -0.03114847163910304, -0.017871542153678276, -0.009175555685211025, -0.004215487231665607, -0.0017330386114138498, -0.0006375492758954594],
        },
        "q6_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005488701553978678, 0.0013349328464855672, 0.0028651099725490355, 0.00540477957405442, 0.00890752344373928, 0.012702274990062283, 0.015408373981438723, 0.015360084413477932, 0.011509454428525369, 0.004287344931564196] + [0.0] * 32 + [-0.004287344931564196, -0.011509454428525369, -0.015360084413477932, -0.015408373981438723, -0.012702274990062283, -0.00890752344373928, -0.00540477957405442, -0.0028651099725490355, -0.0013349328464855672, -0.0005488701553978678],
        },
        "q6_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0011270872008828645, 0.002741241640696169, 0.005883411126336524, 0.011098540923752948, 0.01829131273811941, 0.026083712919344002, 0.031640600112985466, 0.03154143903918775, 0.023634294282465072, 0.008803924845637174] + [0.0] * 32 + [-0.008803924845637174, -0.023634294282465072, -0.03154143903918775, -0.031640600112985466, -0.026083712919344002, -0.01829131273811941, -0.011098540923752948, -0.005883411126336524, -0.002741241640696169, -0.0011270872008828645],
        },
        "q6_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0013091869210360456, 0.0035587390175085298, 0.0086563673713528, 0.018841708320418402, 0.03669863668730205, 0.06396238411987869, 0.0997572372363136, 0.13922243977926, 0.17386778645798365, 0.1943005668067351] + [0.19701801326301746] * 32 + [0.1943005668067351, 0.17386778645798365, 0.13922243977926, 0.0997572372363136, 0.06396238411987869, 0.03669863668730205, 0.018841708320418402, 0.0086563673713528, 0.0035587390175085298, 0.0013091869210360456],
        },
        "q6_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005516113484279842, 0.0013415998306137297, 0.0028794190389284514, 0.005431772377273924, 0.008952009814403536, 0.01276571328658278, 0.015485327204251009, 0.015436796466268823, 0.011566935484745388, 0.004308756990369962] + [0.0] * 32 + [-0.004308756990369962, -0.011566935484745388, -0.015436796466268823, -0.015485327204251009, -0.01276571328658278, -0.008952009814403536, -0.005431772377273924, -0.0028794190389284514, -0.0013415998306137297, -0.0005516113484279842],
        },
        "q6_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006407333543414328, 0.0017416938339939274, 0.00423654041538191, 0.00922138067504585, 0.01796079704631055, 0.03130403479464389, 0.04882250823562685, 0.06813729911750878, 0.08509318893973015, 0.0950932612602027] + [0.0964232154135784] * 32 + [0.0950932612602027, 0.08509318893973015, 0.06813729911750878, 0.04882250823562685, 0.03130403479464389, 0.01796079704631055, 0.00922138067504585, 0.00423654041538191, 0.0017416938339939274, 0.0006407333543414328],
        },
        "q6_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005337479912314077, 0.0012981535217997109, 0.0027861720617631197, 0.005255870103939153, 0.008662108329603272, 0.012352308999384576, 0.014983851061775466, 0.014936891941038026, 0.011192352364179408, 0.004169222397016189] + [0.0] * 32 + [-0.004169222397016189, -0.011192352364179408, -0.014936891941038026, -0.014983851061775466, -0.012352308999384576, -0.008662108329603272, -0.005255870103939153, -0.0027861720617631197, -0.0012981535217997109, -0.0005337479912314077],
        },
        "q6_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q6_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q6_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005337479912314077, -0.0012981535217997109, -0.0027861720617631197, -0.005255870103939153, -0.008662108329603272, -0.012352308999384576, -0.014983851061775466, -0.014936891941038026, -0.011192352364179408, -0.004169222397016189] + [0.0] * 32 + [0.004169222397016189, 0.011192352364179408, 0.014936891941038026, 0.014983851061775466, 0.012352308999384576, 0.008662108329603272, 0.005255870103939153, 0.0027861720617631197, 0.0012981535217997109, 0.0005337479912314077],
        },
        "q6_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005516113484279842, -0.0013415998306137297, -0.0028794190389284514, -0.005431772377273924, -0.008952009814403536, -0.01276571328658278, -0.015485327204251009, -0.015436796466268823, -0.011566935484745388, -0.004308756990369962] + [0.0] * 32 + [0.004308756990369962, 0.011566935484745388, 0.015436796466268823, 0.015485327204251009, 0.01276571328658278, 0.008952009814403536, 0.005431772377273924, 0.0028794190389284514, 0.0013415998306137297, 0.0005516113484279842],
        },
        "q6_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0006407333543414328, -0.0017416938339939274, -0.00423654041538191, -0.00922138067504585, -0.01796079704631055, -0.03130403479464389, -0.04882250823562685, -0.06813729911750878, -0.08509318893973015, -0.0950932612602027] + [-0.0964232154135784] * 32 + [-0.0950932612602027, -0.08509318893973015, -0.06813729911750878, -0.04882250823562685, -0.03130403479464389, -0.01796079704631055, -0.00922138067504585, -0.00423654041538191, -0.0017416938339939274, -0.0006407333543414328],
        },
        "q7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 480 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0012236318384043507+0j), (0.003326176191058481+0j), (0.008090675632574724+0j), (0.017610406749669433+0j), (0.034300388703150185+0j), (0.05978245612734586+0j), (0.09323812332085506+0j), (0.1301242833982944+0j), (0.16250556415161435+0j), (0.18160306671608326+0j)] + [(0.1841429286331537+0j)] * 480 + [(0.18160306671608326+0j), (0.16250556415161435+0j), (0.1301242833982944+0j), (0.09323812332085506+0j), (0.05978245612734586+0j), (0.034300388703150185+0j), (0.017610406749669433+0j), (0.008090675632574724+0j), (0.003326176191058481+0j), (0.0012236318384043507+0j)],
        },
        "q7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 480 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q7_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 480 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005964190784955906+0j), (0.0016212351432208527+0j), (0.003943533629755371+0j), (0.00858361333525516+0j), (0.016718595888327338+0j), (0.029138991218282048+0j), (0.04544585540059031+0j), (0.0634248004657296+0j), (0.0792079903282838+0j), (0.08851643958857824+0j)] + [(0.08975441171102691+0j)] * 480 + [(0.08851643958857824+0j), (0.0792079903282838+0j), (0.0634248004657296+0j), (0.04544585540059031+0j), (0.029138991218282048+0j), (0.016718595888327338+0j), (0.00858361333525516+0j), (0.003943533629755371+0j), (0.0016212351432208527+0j), (0.0005964190784955906+0j)],
        },
        "q7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005964190784955906+0j), (-0.0016212351432208527+0j), (-0.003943533629755371+0j), (-0.00858361333525516+0j), (-0.016718595888327338+0j), (-0.029138991218282048+0j), (-0.04544585540059031+0j), (-0.0634248004657296+0j), (-0.0792079903282838+0j), (-0.08851643958857824+0j)] + [(-0.08975441171102691+0j)] * 480 + [(-0.08851643958857824+0j), (-0.0792079903282838+0j), (-0.0634248004657296+0j), (-0.04544585540059031+0j), (-0.029138991218282048+0j), (-0.016718595888327338+0j), (-0.00858361333525516+0j), (-0.003943533629755371+0j), (-0.0016212351432208527+0j), (-0.0005964190784955906+0j)],
        },
        "q7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0012236318384043507+0j), (0.003326176191058481+0j), (0.008090675632574724+0j), (0.017610406749669433+0j), (0.034300388703150185+0j), (0.05978245612734586+0j), (0.09323812332085506+0j), (0.1301242833982944+0j), (0.16250556415161435+0j), (0.18160306671608326+0j)] + [(0.1841429286331537+0j)] * 480 + [(0.18160306671608326+0j), (0.16250556415161435+0j), (0.1301242833982944+0j), (0.09323812332085506+0j), (0.05978245612734586+0j), (0.034300388703150185+0j), (0.017610406749669433+0j), (0.008090675632574724+0j), (0.003326176191058481+0j), (0.0012236318384043507+0j)],
        },
        "q7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005964190784955906+0j), (0.0016212351432208527+0j), (0.003943533629755371+0j), (0.00858361333525516+0j), (0.016718595888327338+0j), (0.029138991218282048+0j), (0.04544585540059031+0j), (0.0634248004657296+0j), (0.0792079903282838+0j), (0.08851643958857824+0j)] + [(0.08975441171102691+0j)] * 480 + [(0.08851643958857824+0j), (0.0792079903282838+0j), (0.0634248004657296+0j), (0.04544585540059031+0j), (0.029138991218282048+0j), (0.016718595888327338+0j), (0.00858361333525516+0j), (0.003943533629755371+0j), (0.0016212351432208527+0j), (0.0005964190784955906+0j)],
        },
        "q7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005964190784955906+0j), (-0.0016212351432208527+0j), (-0.003943533629755371+0j), (-0.00858361333525516+0j), (-0.016718595888327338+0j), (-0.029138991218282048+0j), (-0.04544585540059031+0j), (-0.0634248004657296+0j), (-0.0792079903282838+0j), (-0.08851643958857824+0j)] + [(-0.08975441171102691+0j)] * 480 + [(-0.08851643958857824+0j), (-0.0792079903282838+0j), (-0.0634248004657296+0j), (-0.04544585540059031+0j), (-0.029138991218282048+0j), (-0.016718595888327338+0j), (-0.00858361333525516+0j), (-0.003943533629755371+0j), (-0.0016212351432208527+0j), (-0.0005964190784955906+0j)],
        },
        "q7_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.00016598607820046132+0j), (0.00017374488279006456+0j), (0.00018182461668733276+0j), (0.00019023640868288456+0j), (0.00019899166980515015+0j), (0.0002081020956594386+0j), (0.00021757966854087058+0j), (0.00022743665930779176+0j), (0.00023768562900206266+0j), (0.0002483394302024204+0j), (0.00025941120809691267+0j), (0.00027091440126023666+0j), (0.00028286274212166343+0j), (0.0002952702571090961+0j), (0.00030815126645470015+0j), (0.00032152038364745256+0j), (0.0003353925145178984+0j), (0.00034978285594035454+0j), (0.0003647068941377975+0j), (0.00038018040257467204+0j), (0.0003962194394229115+0j), (0.0004128403445865228+0j), (0.0004300597362701939+0j), (0.00044789450707751193+0j), (0.00046636181962455154+0j), (0.0004854791016547801+0j), (0.0005052640406414754+0j), (0.0005257345778641061+0j), (0.0005469089019454425+0j), (0.0005688054418364979+0j), (0.000591442859236791+0j), (0.0006148400404378353+0j), (0.0006390160875782182+0j), (0.0006639903092991391+0j), (0.0006897822107898095+0j), (0.0007164114832127066+0j), (0.0007438979924992865+0j), (0.0007722617675074359+0j), (0.0008015229875326451+0j), (0.0008317019691656353+0j), (0.0008628191524899657+0j), (0.000894895086613976+0j), (0.0009279504145323077+0j), (0.000962005857313146+0j), (0.000997082197608313+0j), (0.001033200262484307+0j), (0.0010703809055734633+0j), (0.0011086449885454586+0j), (0.0011480133619005295+0j), (0.0011885068450869097+0j), (0.0012301462059462038+0j), (0.001272952139491643+0j), (0.0013169452460254183+0j), (0.0013621460086026104+0j), (0.0014085747698505482+0j), (0.0014562517081537836+0j), (0.0015051968132162846+0j), (0.0015554298610138207+0j), (0.001606970388150998+0j), (0.0016598376656388244+0j), (0.001714050672110179+0j), (0.001769628066492062+0j), (0.0018265881601549911+0j), (0.0018849488885614631+0j), (0.0019447277824368872+0j), (0.0020059419384879785+0j), (0.0020686079896951037+0j), (0.0021327420752066304+0j), (0.0021983598098648588+0j), (0.002265476253394642+0j), (0.0023341058792873287+0j), (0.002404262543414151+0j), (0.00247595945240468+0j), (0.0025492091318274454+0j), (0.002624023394211219+0j), (0.002700413306946931+0j), (0.0027783891601115248+0j), (0.00285796043425641+0j), (0.0029391357682044994+0j), (0.0030219229269010483+0j), (0.003106328769364742+0j), (0.0031923592167866343+0j), (0.003280019220825657+0j), (0.003369312732150442+0j), (0.003460242669278197+0j), (0.0035528108877623007+0j), (0.0036470181497811035+0j), (0.0037428640941811935+0j), (0.003840347207029114+0j), (0.003939464792726066+0j), (0.004040212945740716+0j), (0.0041425865230156145+0j), (0.004246579117103112+0j), (0.004352183030086878+0j), (0.004459389248345306+0j), (0.004568187418213105+0j), (0.00467856582259736+0j), (0.004790511358604147+0j), (0.004904009516231561+0j), (0.0050190443581845995+0j), (0.0051355985008668635+0j), (0.005253653096603464+0j), (0.005373187817148753+0j), (0.005494180838531686+0j), (0.005616608827290697+0j), (0.005740446928148839+0j), (0.005865668753178781+0j), (0.005992246372505969+0j), (0.006120150306596773+0j), (0.006249349520176947+0j), (0.006379811417824038+0j), (0.0065115018412755955+0j), (0.006644385068493157+0j), (0.00677842381451996+0j), (0.006913579234168197+0j), (0.007049810926569421+0j), (0.00718707694161934+0j), (0.0073253337883458286+0j), (0.0074645364452263765+0j), (0.007604638372478625+0j), (0.007745591526344806+0j), (0.007887346375388172+0j), (0.008029851918816456+0j), (0.00817305570684453+0j), (0.008316903863105221+0j), (0.008461341109114204+0j), (0.008606310790791553+0j), (0.008751754907039352+0j), (0.00889761414037134+0j), (0.00904382788958722+0j), (0.00919033430448081+0j), (0.009337070322567722+0j), (0.009483971707814782+0j), (0.009630973091349823+0j), (0.009778008014127+0j), (0.00992500897151913+0j), (0.010071907459805074+0j), (0.010218634024516574+0j), (0.01036511831060542+0j), (0.010511289114388296+0j), (0.010657074437223146+0j), (0.010802401540867423+0j), (0.010947197004465208+0j), (0.0110913867831067+0j), (0.011234896267900403+0j), (0.011377650347494953+0j), (0.011519573470984435+0j), (0.011660589712127873+0j), (0.011800622834810618+0j), (0.011939596359672417+0j), (0.012077433631824118+0j), (0.012214057889572274+0j), (0.012349392334068341+0j), (0.012483360199796654+0j), (0.012615884825813068+0j), (0.012746889727643925+0j), (0.012876298669752994+0j), (0.013004035738482038+0j), (0.013130025415369024+0j), (0.013254192650746286+0j), (0.013376462937519592+0j), (0.013496762385027752+0j), (0.013615017792881389+0j), (0.013731156724678468+0j), (0.01384510758149354+0j), (0.0139567996750371+0j), (0.014066163300381022+0j), (0.014173129808145923+0j), (0.014277631676046355+0j), (0.014379602579689801+0j), (0.014478977462526013+0j), (0.014575692604843706+0j), (0.014669685691712463+0j), (0.014760895879768685+0j), (0.014849263862745576+0j), (0.014934731935648558+0j), (0.015017244057479026+0j), (0.015096745912411105+0j), (0.015173184969328091+0j), (0.015246510539627195+0j), (0.01531667383320371+0j), (0.015383628012528041+0j), (0.015447328244731736+0j), (0.015507731751621507+0j), (0.015564797857543096+0j), (0.015618488035020103+0j), (0.01566876594809607+0j), (0.015715597493311553+0j), (0.015758950838251566+0j), (0.01579879645760234+0j), (0.01583510716666028+0j), (0.01586785815223984+0j), (0.015897027000931156+0j), (0.01592259372466238+0j), (0.015944540783525907+0j), (0.015962853105831967+0j), (0.015977518105357576+0j), (0.015988525695763096+0j), (0.015995868302153368+0j), (0.01599954086976487+0j)] + [(0.016+0j)] * 3600 + [(0.01599954086976487+0j), (0.015995868302153368+0j), (0.015988525695763096+0j), (0.015977518105357576+0j), (0.015962853105831967+0j), (0.015944540783525907+0j), (0.01592259372466238+0j), (0.015897027000931156+0j), (0.01586785815223984+0j), (0.01583510716666028+0j), (0.01579879645760234+0j), (0.015758950838251566+0j), (0.015715597493311553+0j), (0.01566876594809607+0j), (0.015618488035020103+0j), (0.015564797857543096+0j), (0.015507731751621507+0j), (0.015447328244731736+0j), (0.015383628012528041+0j), (0.01531667383320371+0j), (0.015246510539627195+0j), (0.015173184969328091+0j), (0.015096745912411105+0j), (0.015017244057479026+0j), (0.014934731935648558+0j), (0.014849263862745576+0j), (0.014760895879768685+0j), (0.014669685691712463+0j), (0.014575692604843706+0j), (0.014478977462526013+0j), (0.014379602579689801+0j), (0.014277631676046355+0j), (0.014173129808145923+0j), (0.014066163300381022+0j), (0.0139567996750371+0j), (0.01384510758149354+0j), (0.013731156724678468+0j), (0.013615017792881389+0j), (0.013496762385027752+0j), (0.013376462937519592+0j), (0.013254192650746286+0j), (0.013130025415369024+0j), (0.013004035738482038+0j), (0.012876298669752994+0j), (0.012746889727643925+0j), (0.012615884825813068+0j), (0.012483360199796654+0j), (0.012349392334068341+0j), (0.012214057889572274+0j), (0.012077433631824118+0j), (0.011939596359672417+0j), (0.011800622834810618+0j), (0.011660589712127873+0j), (0.011519573470984435+0j), (0.011377650347494953+0j), (0.011234896267900403+0j), (0.0110913867831067+0j), (0.010947197004465208+0j), (0.010802401540867423+0j), (0.010657074437223146+0j), (0.010511289114388296+0j), (0.01036511831060542+0j), (0.010218634024516574+0j), (0.010071907459805074+0j), (0.00992500897151913+0j), (0.009778008014127+0j), (0.009630973091349823+0j), (0.009483971707814782+0j), (0.009337070322567722+0j), (0.00919033430448081+0j), (0.00904382788958722+0j), (0.00889761414037134+0j), (0.008751754907039352+0j), (0.008606310790791553+0j), (0.008461341109114204+0j), (0.008316903863105221+0j), (0.00817305570684453+0j), (0.008029851918816456+0j), (0.007887346375388172+0j), (0.007745591526344806+0j), (0.007604638372478625+0j), (0.0074645364452263765+0j), (0.0073253337883458286+0j), (0.00718707694161934+0j), (0.007049810926569421+0j), (0.006913579234168197+0j), (0.00677842381451996+0j), (0.006644385068493157+0j), (0.0065115018412755955+0j), (0.006379811417824038+0j), (0.006249349520176947+0j), (0.006120150306596773+0j), (0.005992246372505969+0j), (0.005865668753178781+0j), (0.005740446928148839+0j), (0.005616608827290697+0j), (0.005494180838531686+0j), (0.005373187817148753+0j), (0.005253653096603464+0j), (0.0051355985008668635+0j), (0.0050190443581845995+0j), (0.004904009516231561+0j), (0.004790511358604147+0j), (0.00467856582259736+0j), (0.004568187418213105+0j), (0.004459389248345306+0j), (0.004352183030086878+0j), (0.004246579117103112+0j), (0.0041425865230156145+0j), (0.004040212945740716+0j), (0.003939464792726066+0j), (0.003840347207029114+0j), (0.0037428640941811935+0j), (0.0036470181497811035+0j), (0.0035528108877623007+0j), (0.003460242669278197+0j), (0.003369312732150442+0j), (0.003280019220825657+0j), (0.0031923592167866343+0j), (0.003106328769364742+0j), (0.0030219229269010483+0j), (0.0029391357682044994+0j), (0.00285796043425641+0j), (0.0027783891601115248+0j), (0.002700413306946931+0j), (0.002624023394211219+0j), (0.0025492091318274454+0j), (0.00247595945240468+0j), (0.002404262543414151+0j), (0.0023341058792873287+0j), (0.002265476253394642+0j), (0.0021983598098648588+0j), (0.0021327420752066304+0j), (0.0020686079896951037+0j), (0.0020059419384879785+0j), (0.0019447277824368872+0j), (0.0018849488885614631+0j), (0.0018265881601549911+0j), (0.001769628066492062+0j), (0.001714050672110179+0j), (0.0016598376656388244+0j), (0.001606970388150998+0j), (0.0015554298610138207+0j), (0.0015051968132162846+0j), (0.0014562517081537836+0j), (0.0014085747698505482+0j), (0.0013621460086026104+0j), (0.0013169452460254183+0j), (0.001272952139491643+0j), (0.0012301462059462038+0j), (0.0011885068450869097+0j), (0.0011480133619005295+0j), (0.0011086449885454586+0j), (0.0010703809055734633+0j), (0.001033200262484307+0j), (0.000997082197608313+0j), (0.000962005857313146+0j), (0.0009279504145323077+0j), (0.000894895086613976+0j), (0.0008628191524899657+0j), (0.0008317019691656353+0j), (0.0008015229875326451+0j), (0.0007722617675074359+0j), (0.0007438979924992865+0j), (0.0007164114832127066+0j), (0.0006897822107898095+0j), (0.0006639903092991391+0j), (0.0006390160875782182+0j), (0.0006148400404378353+0j), (0.000591442859236791+0j), (0.0005688054418364979+0j), (0.0005469089019454425+0j), (0.0005257345778641061+0j), (0.0005052640406414754+0j), (0.0004854791016547801+0j), (0.00046636181962455154+0j), (0.00044789450707751193+0j), (0.0004300597362701939+0j), (0.0004128403445865228+0j), (0.0003962194394229115+0j), (0.00038018040257467204+0j), (0.0003647068941377975+0j), (0.00034978285594035454+0j), (0.0003353925145178984+0j), (0.00032152038364745256+0j), (0.00030815126645470015+0j), (0.0002952702571090961+0j), (0.00028286274212166343+0j), (0.00027091440126023666+0j), (0.00025941120809691267+0j), (0.0002483394302024204+0j), (0.00023768562900206266+0j), (0.00022743665930779176+0j), (0.00021757966854087058+0j), (0.0002081020956594386+0j), (0.00019899166980515015+0j), (0.00019023640868288456+0j), (0.00018182461668733276+0j), (0.00017374488279006456+0j), (0.00016598607820046132+0j)],
        },
        "q7_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 480 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
        },
        "q7_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005584056695718085, -0.0013581246177154947, -0.0029148854913752247, -0.0054986767403123705, -0.009062273734344742, -0.01292295145063834, -0.015676063465103366, -0.0156269349630974, -0.011709408032776217, -0.004361828920102192] + [0.0] * 480 + [0.004361828920102192, 0.011709408032776217, 0.0156269349630974, 0.015676063465103366, 0.01292295145063834, 0.009062273734344742, 0.0054986767403123705, 0.0029148854913752247, 0.0013581246177154947, 0.0005584056695718085],
        },
        "q7_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 480 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
        },
        "q7_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002721764704218791, -0.0006619731585575026, -0.001420765024350152, -0.0026801490542112897, -0.004417107155989697, -0.006298867480993105, -0.007640781346852948, -0.007616835275024287, -0.005707365671151718, -0.0021260299899315835] + [0.0] * 480 + [0.0021260299899315835, 0.005707365671151718, 0.007616835275024287, 0.007640781346852948, 0.006298867480993105, 0.004417107155989697, 0.0026801490542112897, 0.001420765024350152, 0.0006619731585575026, 0.0002721764704218791],
        },
        "q7_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 480 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
        },
        "q7_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002721764704218791, 0.0006619731585575026, 0.001420765024350152, 0.0026801490542112897, 0.004417107155989697, 0.006298867480993105, 0.007640781346852948, 0.007616835275024287, 0.005707365671151718, 0.0021260299899315835] + [0.0] * 480 + [-0.0021260299899315835, -0.005707365671151718, -0.007616835275024287, -0.007640781346852948, -0.006298867480993105, -0.004417107155989697, -0.0026801490542112897, -0.001420765024350152, -0.0006619731585575026, -0.0002721764704218791],
        },
        "q7_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005584056695718085, 0.0013581246177154947, 0.0029148854913752247, 0.0054986767403123705, 0.009062273734344742, 0.01292295145063834, 0.015676063465103366, 0.0156269349630974, 0.011709408032776217, 0.004361828920102192] + [0.0] * 480 + [-0.004361828920102192, -0.011709408032776217, -0.0156269349630974, -0.015676063465103366, -0.01292295145063834, -0.009062273734344742, -0.0054986767403123705, -0.0029148854913752247, -0.0013581246177154947, -0.0005584056695718085],
        },
        "q7_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 480 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
        },
        "q7_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002721764704218791, 0.0006619731585575026, 0.001420765024350152, 0.0026801490542112897, 0.004417107155989697, 0.006298867480993105, 0.007640781346852948, 0.007616835275024287, 0.005707365671151718, 0.0021260299899315835] + [0.0] * 480 + [-0.0021260299899315835, -0.005707365671151718, -0.007616835275024287, -0.007640781346852948, -0.006298867480993105, -0.004417107155989697, -0.0026801490542112897, -0.001420765024350152, -0.0006619731585575026, -0.0002721764704218791],
        },
        "q7_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 480 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
        },
        "q7_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 480 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
        },
        "q7_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 480 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q7_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 480 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q7_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 480 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
        },
        "q7_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002721764704218791, -0.0006619731585575026, -0.001420765024350152, -0.0026801490542112897, -0.004417107155989697, -0.006298867480993105, -0.007640781346852948, -0.007616835275024287, -0.005707365671151718, -0.0021260299899315835] + [0.0] * 480 + [0.0021260299899315835, 0.005707365671151718, 0.007616835275024287, 0.007640781346852948, 0.006298867480993105, 0.004417107155989697, 0.0026801490542112897, 0.001420765024350152, 0.0006619731585575026, 0.0002721764704218791],
        },
        "q7_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 480 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
        },
        "q8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 280 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 280 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 280 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q8_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 280 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 280 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 280 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
        "q8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 280 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 280 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 280 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
        "q8_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0004149651955011534+0j), (0.0004343622069751615+0j), (0.000454561541718332+0j), (0.0004755910217072115+0j), (0.0004974791745128755+0j), (0.0005202552391485965+0j), (0.0005439491713521765+0j), (0.0005685916482694795+0j), (0.0005942140725051567+0j), (0.000620848575506051+0j), (0.0006485280202422817+0j), (0.0006772860031505917+0j), (0.0007071568553041587+0j), (0.0007381756427727404+0j), (0.0007703781661367505+0j), (0.0008038009591186315+0j), (0.0008384812862947461+0j), (0.0008744571398508864+0j), (0.000911767235344494+0j), (0.0009504510064366802+0j), (0.000990548598557279+0j), (0.0010321008614663071+0j), (0.0010751493406754849+0j), (0.00111973626769378+0j), (0.001165904549061379+0j), (0.0012136977541369505+0j), (0.0012631601016036885+0j), (0.0013143364446602654+0j), (0.0013672722548636065+0j), (0.0014220136045912449+0j), (0.0014786071480919778+0j), (0.0015371001010945887+0j), (0.0015975402189455457+0j), (0.0016599757732478479+0j), (0.001724455526974524+0j), (0.001791028708031767+0j), (0.0018597449812482166+0j), (0.0019306544187685899+0j), (0.002003807468831613+0j), (0.002079254922914089+0j), (0.0021570478812249147+0j), (0.0022372377165349403+0j), (0.0023198760363307694+0j), (0.0024050146432828654+0j), (0.002492705494020783+0j), (0.0025830006562107682+0j), (0.0026759522639336585+0j), (0.002771612471363647+0j), (0.002870033404751324+0j), (0.002971267112717275+0j), (0.00307536551486551+0j), (0.003182380348729108+0j), (0.0032923631150635463+0j), (0.003405365021506527+0j), (0.0035214369246263713+0j), (0.0036406292703844594+0j), (0.003762992033040712+0j), (0.0038885746525345525+0j), (0.004017425970377496+0j), (0.004149594164097062+0j), (0.004285126680275449+0j), (0.004424070166230155+0j), (0.004566470400387479+0j), (0.004712372221403659+0j), (0.0048618194560922185+0j), (0.005014854846219947+0j), (0.00517151997423776+0j), (0.005331855188016576+0j), (0.005495899524662148+0j), (0.005663690633486606+0j), (0.005835264698218323+0j), (0.006010656358535378+0j), (0.006189898631011701+0j), (0.006373022829568614+0j), (0.006560058485528049+0j), (0.006751033267367329+0j), (0.006945972900278813+0j), (0.007144901085641026+0j), (0.00734783942051125+0j), (0.007554807317252622+0j), (0.007765821923411856+0j), (0.007980898041966587+0j), (0.008200048052064144+0j), (0.008423281830376106+0j), (0.008650606673195494+0j), (0.008882027219405753+0j), (0.00911754537445276+0j), (0.009357160235452985+0j), (0.009600868017572787+0j), (0.009848661981815167+0j), (0.010100532364351792+0j), (0.010356466307539038+0j), (0.01061644779275778+0j), (0.010880457575217196+0j), (0.011148473120863266+0j), (0.011420468545532764+0j), (0.011696414556493402+0j), (0.01197627839651037+0j), (0.012260023790578905+0j), (0.0125476108954615+0j), (0.01283899625216716+0j), (0.013134132741508665+0j), (0.013432969542871884+0j), (0.013735452096329218+0j), (0.014041522068226746+0j), (0.0143511173203721+0j), (0.014664171882946955+0j), (0.014980615931264925+0j), (0.015300375766491934+0j), (0.015623373800442372+0j), (0.0159495285445601+0j), (0.01627875460318899+0j), (0.016610962671232896+0j), (0.016946059536299903+0j), (0.017283948085420497+0j), (0.017624527316423555+0j), (0.017967692354048354+0j), (0.018313334470864574+0j), (0.018661341113065943+0j), (0.019011595931196563+0j), (0.019363978815862017+0j), (0.019718365938470435+0j), (0.020074629797041145+0j), (0.02043263926711133+0j), (0.020792259657763056+0j), (0.021153352772785516+0j), (0.021515776976978884+0j), (0.021879387267598385+0j), (0.02224403535092835+0j), (0.022609569723968055+0j), (0.022975835761202032+0j), (0.02334267580641931+0j), (0.023709929269536956+0j), (0.02407743272837456+0j), (0.024445020035317504+0j), (0.02481252242879783+0j), (0.02517976864951269+0j), (0.025546585061291437+0j), (0.025912795776513554+0j), (0.026278222785970744+0j), (0.026642686093057866+0j), (0.027006003852168566+0j), (0.027367992511163026+0j), (0.027728466957766755+0j), (0.028087240669751014+0j), (0.028444125868737388+0j), (0.028798933677461093+0j), (0.029151474280319688+0j), (0.02950155708702655+0j), (0.029848990899181048+0j), (0.0301935840795603+0j), (0.03053514472393069+0j), (0.030873480835170858+0j), (0.03120840049949164+0j), (0.031539712064532675+0j), (0.03186722431910982+0j), (0.03219074667438249+0j), (0.032510089346205105+0j), (0.032825063538422565+0j), (0.03313548162686572+0j), (0.03344115734379898+0j), (0.03374190596256939+0j), (0.03403754448220348+0j), (0.034327891811696175+0j), (0.03461276895373386+0j), (0.034891999187592754+0j), (0.03516540825095256+0j), (0.035432824520364815+0j), (0.03569407919011589+0j), (0.03594900644922451+0j), (0.03619744365631504+0j), (0.036439231512109274+0j), (0.03667421422928117+0j), (0.03690223969942172+0j), (0.03712315965686395+0j), (0.037336829839121406+0j), (0.03754311014369757+0j), (0.03774186478102777+0j), (0.037932962423320234+0j), (0.038116276349067994+0j), (0.038291684583009286+0j), (0.03845907003132011+0j), (0.03861832061182935+0j), (0.03876932937905377+0j), (0.03891199464385774+0j), (0.039046220087550265+0j), (0.03917191487024018+0j), (0.03928899373327889+0j), (0.03939737709562892+0j), (0.03949699114400586+0j), (0.03958776791665071+0j), (0.03966964538059961+0j), (0.039742567502327894+0j), (0.03980648431165596+0j), (0.039861351958814774+0j), (0.039907132764579925+0j), (0.03994379526339395+0j), (0.039971314239407744+0j), (0.03998967075538343+0j), (0.03999885217441219+0j)] + [(0.04000000000000001+0j)] * 1600 + [(0.03999885217441219+0j), (0.03998967075538343+0j), (0.039971314239407744+0j), (0.03994379526339395+0j), (0.039907132764579925+0j), (0.039861351958814774+0j), (0.03980648431165596+0j), (0.039742567502327894+0j), (0.03966964538059961+0j), (0.03958776791665071+0j), (0.03949699114400586+0j), (0.03939737709562892+0j), (0.03928899373327889+0j), (0.03917191487024018+0j), (0.039046220087550265+0j), (0.03891199464385774+0j), (0.03876932937905377+0j), (0.03861832061182935+0j), (0.03845907003132011+0j), (0.038291684583009286+0j), (0.038116276349067994+0j), (0.037932962423320234+0j), (0.03774186478102777+0j), (0.03754311014369757+0j), (0.037336829839121406+0j), (0.03712315965686395+0j), (0.03690223969942172+0j), (0.03667421422928117+0j), (0.036439231512109274+0j), (0.03619744365631504+0j), (0.03594900644922451+0j), (0.03569407919011589+0j), (0.035432824520364815+0j), (0.03516540825095256+0j), (0.034891999187592754+0j), (0.03461276895373386+0j), (0.034327891811696175+0j), (0.03403754448220348+0j), (0.03374190596256939+0j), (0.03344115734379898+0j), (0.03313548162686572+0j), (0.032825063538422565+0j), (0.032510089346205105+0j), (0.03219074667438249+0j), (0.03186722431910982+0j), (0.031539712064532675+0j), (0.03120840049949164+0j), (0.030873480835170858+0j), (0.03053514472393069+0j), (0.0301935840795603+0j), (0.029848990899181048+0j), (0.02950155708702655+0j), (0.029151474280319688+0j), (0.028798933677461093+0j), (0.028444125868737388+0j), (0.028087240669751014+0j), (0.027728466957766755+0j), (0.027367992511163026+0j), (0.027006003852168566+0j), (0.026642686093057866+0j), (0.026278222785970744+0j), (0.025912795776513554+0j), (0.025546585061291437+0j), (0.02517976864951269+0j), (0.02481252242879783+0j), (0.024445020035317504+0j), (0.02407743272837456+0j), (0.023709929269536956+0j), (0.02334267580641931+0j), (0.022975835761202032+0j), (0.022609569723968055+0j), (0.02224403535092835+0j), (0.021879387267598385+0j), (0.021515776976978884+0j), (0.021153352772785516+0j), (0.020792259657763056+0j), (0.02043263926711133+0j), (0.020074629797041145+0j), (0.019718365938470435+0j), (0.019363978815862017+0j), (0.019011595931196563+0j), (0.018661341113065943+0j), (0.018313334470864574+0j), (0.017967692354048354+0j), (0.017624527316423555+0j), (0.017283948085420497+0j), (0.016946059536299903+0j), (0.016610962671232896+0j), (0.01627875460318899+0j), (0.0159495285445601+0j), (0.015623373800442372+0j), (0.015300375766491934+0j), (0.014980615931264925+0j), (0.014664171882946955+0j), (0.0143511173203721+0j), (0.014041522068226746+0j), (0.013735452096329218+0j), (0.013432969542871884+0j), (0.013134132741508665+0j), (0.01283899625216716+0j), (0.0125476108954615+0j), (0.012260023790578905+0j), (0.01197627839651037+0j), (0.011696414556493402+0j), (0.011420468545532764+0j), (0.011148473120863266+0j), (0.010880457575217196+0j), (0.01061644779275778+0j), (0.010356466307539038+0j), (0.010100532364351792+0j), (0.009848661981815167+0j), (0.009600868017572787+0j), (0.009357160235452985+0j), (0.00911754537445276+0j), (0.008882027219405753+0j), (0.008650606673195494+0j), (0.008423281830376106+0j), (0.008200048052064144+0j), (0.007980898041966587+0j), (0.007765821923411856+0j), (0.007554807317252622+0j), (0.00734783942051125+0j), (0.007144901085641026+0j), (0.006945972900278813+0j), (0.006751033267367329+0j), (0.006560058485528049+0j), (0.006373022829568614+0j), (0.006189898631011701+0j), (0.006010656358535378+0j), (0.005835264698218323+0j), (0.005663690633486606+0j), (0.005495899524662148+0j), (0.005331855188016576+0j), (0.00517151997423776+0j), (0.005014854846219947+0j), (0.0048618194560922185+0j), (0.004712372221403659+0j), (0.004566470400387479+0j), (0.004424070166230155+0j), (0.004285126680275449+0j), (0.004149594164097062+0j), (0.004017425970377496+0j), (0.0038885746525345525+0j), (0.003762992033040712+0j), (0.0036406292703844594+0j), (0.0035214369246263713+0j), (0.003405365021506527+0j), (0.0032923631150635463+0j), (0.003182380348729108+0j), (0.00307536551486551+0j), (0.002971267112717275+0j), (0.002870033404751324+0j), (0.002771612471363647+0j), (0.0026759522639336585+0j), (0.0025830006562107682+0j), (0.002492705494020783+0j), (0.0024050146432828654+0j), (0.0023198760363307694+0j), (0.0022372377165349403+0j), (0.0021570478812249147+0j), (0.002079254922914089+0j), (0.002003807468831613+0j), (0.0019306544187685899+0j), (0.0018597449812482166+0j), (0.001791028708031767+0j), (0.001724455526974524+0j), (0.0016599757732478479+0j), (0.0015975402189455457+0j), (0.0015371001010945887+0j), (0.0014786071480919778+0j), (0.0014220136045912449+0j), (0.0013672722548636065+0j), (0.0013143364446602654+0j), (0.0012631601016036885+0j), (0.0012136977541369505+0j), (0.001165904549061379+0j), (0.00111973626769378+0j), (0.0010751493406754849+0j), (0.0010321008614663071+0j), (0.000990548598557279+0j), (0.0009504510064366802+0j), (0.000911767235344494+0j), (0.0008744571398508864+0j), (0.0008384812862947461+0j), (0.0008038009591186315+0j), (0.0007703781661367505+0j), (0.0007381756427727404+0j), (0.0007071568553041587+0j), (0.0006772860031505917+0j), (0.0006485280202422817+0j), (0.000620848575506051+0j), (0.0005942140725051567+0j), (0.0005685916482694795+0j), (0.0005439491713521765+0j), (0.0005202552391485965+0j), (0.0004974791745128755+0j), (0.0004755910217072115+0j), (0.000454561541718332+0j), (0.0004343622069751615+0j), (0.0004149651955011534+0j)],
        },
        "q8_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
        },
        "q8_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0004454716972071287, -0.0010834526070203215, -0.002325368558673589, -0.004386604566136695, -0.0072294868784010405, -0.010309367238437193, -0.012505679970407689, -0.012466487393465151, -0.00934125520905161, -0.003479676940699813] + [0.0] * 280 + [0.003479676940699813, 0.00934125520905161, 0.012466487393465151, 0.012505679970407689, 0.010309367238437193, 0.0072294868784010405, 0.004386604566136695, 0.002325368558673589, 0.0010834526070203215, 0.0004454716972071287],
        },
        "q8_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
        },
        "q8_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00020222042215584682, -0.0004918297726906548, -0.0010555934631785654, -0.001991284817321347, -0.0032818019588810336, -0.004679903590254542, -0.005676912582363025, -0.005659121240052427, -0.0042404322961097215, -0.0015795879835371531] + [0.0] * 280 + [0.0015795879835371531, 0.0042404322961097215, 0.005659121240052427, 0.005676912582363025, 0.004679903590254542, 0.0032818019588810336, 0.001991284817321347, 0.0010555934631785654, 0.0004918297726906548, 0.00020222042215584682],
        },
        "q8_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
        },
        "q8_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00020222042215584682, 0.0004918297726906548, 0.0010555934631785654, 0.001991284817321347, 0.0032818019588810336, 0.004679903590254542, 0.005676912582363025, 0.005659121240052427, 0.0042404322961097215, 0.0015795879835371531] + [0.0] * 280 + [-0.0015795879835371531, -0.0042404322961097215, -0.005659121240052427, -0.005676912582363025, -0.004679903590254542, -0.0032818019588810336, -0.001991284817321347, -0.0010555934631785654, -0.0004918297726906548, -0.00020222042215584682],
        },
        "q8_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004454716972071287, 0.0010834526070203215, 0.002325368558673589, 0.004386604566136695, 0.0072294868784010405, 0.010309367238437193, 0.012505679970407689, 0.012466487393465151, 0.00934125520905161, 0.003479676940699813] + [0.0] * 280 + [-0.003479676940699813, -0.00934125520905161, -0.012466487393465151, -0.012505679970407689, -0.010309367238437193, -0.0072294868784010405, -0.004386604566136695, -0.002325368558673589, -0.0010834526070203215, -0.0004454716972071287],
        },
        "q8_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
        },
        "q8_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00020222042215584682, 0.0004918297726906548, 0.0010555934631785654, 0.001991284817321347, 0.0032818019588810336, 0.004679903590254542, 0.005676912582363025, 0.005659121240052427, 0.0042404322961097215, 0.0015795879835371531] + [0.0] * 280 + [-0.0015795879835371531, -0.0042404322961097215, -0.005659121240052427, -0.005676912582363025, -0.004679903590254542, -0.0032818019588810336, -0.001991284817321347, -0.0010555934631785654, -0.0004918297726906548, -0.00020222042215584682],
        },
        "q8_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
        },
        "q8_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 280 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
        },
        "q8_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q8_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q8_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 280 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
        },
        "q8_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00020222042215584682, -0.0004918297726906548, -0.0010555934631785654, -0.001991284817321347, -0.0032818019588810336, -0.004679903590254542, -0.005676912582363025, -0.005659121240052427, -0.0042404322961097215, -0.0015795879835371531] + [0.0] * 280 + [0.0015795879835371531, 0.0042404322961097215, 0.005659121240052427, 0.005676912582363025, 0.004679903590254542, 0.0032818019588810336, 0.001991284817321347, 0.0010555934631785654, 0.0004918297726906548, 0.00020222042215584682],
        },
        "q8_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
        },
        "rise_wf": {
            "type": "arbitrary",
            "samples": [0.0032754804057496334, 0.005968314427627137, 0.010448563941567294, 0.01757477344936297, 0.028402141495854794, 0.04410021012179409, 0.06578978263086196, 0.09429843062234541, 0.1298609869433399, 0.17182294328429568, 0.21842977065588376, 0.26679072434338974, 0.3130818152967473, 0.3529987610338382, 0.38239899273324, 0.39800499167707293],
        },
        "fall_wf": {
            "type": "arbitrary",
            "samples": [0.39800499167707293, 0.38239899273324, 0.3529987610338382, 0.3130818152967473, 0.26679072434338974, 0.21842977065588376, 0.17182294328429568, 0.1298609869433399, 0.09429843062234541, 0.06578978263086196, 0.04410021012179409, 0.028402141495854794, 0.01757477344936297, 0.010448563941567294, 0.005968314427627137, 0.0032754804057496334],
        },
        "q12_1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0015648193824325564+0j), (0.004253620092086923+0j), (0.010346613784859734+0j), (0.02252074925603363+0j), (0.04386442995603347+0j), (0.07645170969029776+0j), (0.11923588286520037+0j), (0.1664070796427832+0j), (0.20781729320576267+0j), (0.23223978797175873+0j)] + [(0.23548784431664505+0j)] * 32 + [(0.23223978797175873+0j), (0.20781729320576267+0j), (0.1664070796427832+0j), (0.11923588286520037+0j), (0.07645170969029776+0j), (0.04386442995603347+0j), (0.02252074925603363+0j), (0.010346613784859734+0j), (0.004253620092086923+0j), (0.0015648193824325564+0j)],
        },
        "q12_1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0007723712416023449+0j), (0.0020995227108720053+0j), (0.005106932483779149+0j), (0.011115902103447699+0j), (0.021650820923916358+0j), (0.03773541061609538+0j), (0.05885303308870271+0j), (0.08213602423259626+0j), (0.10257548096717262+0j), (0.11463005596618349+0j)] + [(0.11623324758053732+0j)] * 32 + [(0.11463005596618349+0j), (0.10257548096717262+0j), (0.08213602423259626+0j), (0.05885303308870271+0j), (0.03773541061609538+0j), (0.021650820923916358+0j), (0.011115902103447699+0j), (0.005106932483779149+0j), (0.0020995227108720053+0j), (0.0007723712416023449+0j)],
        },
        "q12_1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0007723712416023449+0j), (-0.0020995227108720053+0j), (-0.005106932483779149+0j), (-0.011115902103447699+0j), (-0.021650820923916358+0j), (-0.03773541061609538+0j), (-0.05885303308870271+0j), (-0.08213602423259626+0j), (-0.10257548096717262+0j), (-0.11463005596618349+0j)] + [(-0.11623324758053732+0j)] * 32 + [(-0.11463005596618349+0j), (-0.10257548096717262+0j), (-0.08213602423259626+0j), (-0.05885303308870271+0j), (-0.03773541061609538+0j), (-0.021650820923916358+0j), (-0.011115902103447699+0j), (-0.005106932483779149+0j), (-0.0020995227108720053+0j), (-0.0007723712416023449+0j)],
        },
        "q12_1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0015648193824325564+0j), (0.004253620092086923+0j), (0.010346613784859734+0j), (0.02252074925603363+0j), (0.04386442995603347+0j), (0.07645170969029776+0j), (0.11923588286520037+0j), (0.1664070796427832+0j), (0.20781729320576267+0j), (0.23223978797175873+0j)] + [(0.23548784431664505+0j)] * 32 + [(0.23223978797175873+0j), (0.20781729320576267+0j), (0.1664070796427832+0j), (0.11923588286520037+0j), (0.07645170969029776+0j), (0.04386442995603347+0j), (0.02252074925603363+0j), (0.010346613784859734+0j), (0.004253620092086923+0j), (0.0015648193824325564+0j)],
        },
        "q12_1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0007723712416023449+0j), (0.0020995227108720053+0j), (0.005106932483779149+0j), (0.011115902103447699+0j), (0.021650820923916358+0j), (0.03773541061609538+0j), (0.05885303308870271+0j), (0.08213602423259626+0j), (0.10257548096717262+0j), (0.11463005596618349+0j)] + [(0.11623324758053732+0j)] * 32 + [(0.11463005596618349+0j), (0.10257548096717262+0j), (0.08213602423259626+0j), (0.05885303308870271+0j), (0.03773541061609538+0j), (0.021650820923916358+0j), (0.011115902103447699+0j), (0.005106932483779149+0j), (0.0020995227108720053+0j), (0.0007723712416023449+0j)],
        },
        "q12_1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0007723712416023449+0j), (-0.0020995227108720053+0j), (-0.005106932483779149+0j), (-0.011115902103447699+0j), (-0.021650820923916358+0j), (-0.03773541061609538+0j), (-0.05885303308870271+0j), (-0.08213602423259626+0j), (-0.10257548096717262+0j), (-0.11463005596618349+0j)] + [(-0.11623324758053732+0j)] * 32 + [(-0.11463005596618349+0j), (-0.10257548096717262+0j), (-0.08213602423259626+0j), (-0.05885303308870271+0j), (-0.03773541061609538+0j), (-0.021650820923916358+0j), (-0.011115902103447699+0j), (-0.005106932483779149+0j), (-0.0020995227108720053+0j), (-0.0007723712416023449+0j)],
        },
        "q12_2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.001135946761023375+0j), (0.0030878234385867498+0j), (0.007510900330363067+0j), (0.016348450473205704+0j), (0.03184243350515918+0j), (0.055498463894529455+0j), (0.08655670837098965+0j), (0.1207996176771063+0j), (0.15086046591188984+0j), (0.1685894473758188+0j)] + [(0.17094730357699864+0j)] * 32 + [(0.1685894473758188+0j), (0.15086046591188984+0j), (0.1207996176771063+0j), (0.08655670837098965+0j), (0.055498463894529455+0j), (0.03184243350515918+0j), (0.016348450473205704+0j), (0.007510900330363067+0j), (0.0030878234385867498+0j), (0.001135946761023375+0j)],
        },
        "q12_2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005662189655832061+0j), (0.0015391427250737064+0j), (0.0037438499422502635+0j), (0.008148975844156069+0j), (0.01587203765139504+0j), (0.02766351724926547+0j), (0.04314467152840492+0j), (0.06021323966129995+0j), (0.07519723624994168+0j), (0.08403434542599673+0j)] + [(0.08520963193152209+0j)] * 32 + [(0.08403434542599673+0j), (0.07519723624994168+0j), (0.06021323966129995+0j), (0.04314467152840492+0j), (0.02766351724926547+0j), (0.01587203765139504+0j), (0.008148975844156069+0j), (0.0037438499422502635+0j), (0.0015391427250737064+0j), (0.0005662189655832061+0j)],
        },
        "q12_2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005662189655832061+0j), (-0.0015391427250737064+0j), (-0.0037438499422502635+0j), (-0.008148975844156069+0j), (-0.01587203765139504+0j), (-0.02766351724926547+0j), (-0.04314467152840492+0j), (-0.06021323966129995+0j), (-0.07519723624994168+0j), (-0.08403434542599673+0j)] + [(-0.08520963193152209+0j)] * 32 + [(-0.08403434542599673+0j), (-0.07519723624994168+0j), (-0.06021323966129995+0j), (-0.04314467152840492+0j), (-0.02766351724926547+0j), (-0.01587203765139504+0j), (-0.008148975844156069+0j), (-0.0037438499422502635+0j), (-0.0015391427250737064+0j), (-0.0005662189655832061+0j)],
        },
        "q12_2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.001135946761023375+0j), (0.0030878234385867498+0j), (0.007510900330363067+0j), (0.016348450473205704+0j), (0.03184243350515918+0j), (0.055498463894529455+0j), (0.08655670837098965+0j), (0.1207996176771063+0j), (0.15086046591188984+0j), (0.1685894473758188+0j)] + [(0.17094730357699864+0j)] * 32 + [(0.1685894473758188+0j), (0.15086046591188984+0j), (0.1207996176771063+0j), (0.08655670837098965+0j), (0.055498463894529455+0j), (0.03184243350515918+0j), (0.016348450473205704+0j), (0.007510900330363067+0j), (0.0030878234385867498+0j), (0.001135946761023375+0j)],
        },
        "q12_2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005662189655832061+0j), (0.0015391427250737064+0j), (0.0037438499422502635+0j), (0.008148975844156069+0j), (0.01587203765139504+0j), (0.02766351724926547+0j), (0.04314467152840492+0j), (0.06021323966129995+0j), (0.07519723624994168+0j), (0.08403434542599673+0j)] + [(0.08520963193152209+0j)] * 32 + [(0.08403434542599673+0j), (0.07519723624994168+0j), (0.06021323966129995+0j), (0.04314467152840492+0j), (0.02766351724926547+0j), (0.01587203765139504+0j), (0.008148975844156069+0j), (0.0037438499422502635+0j), (0.0015391427250737064+0j), (0.0005662189655832061+0j)],
        },
        "q12_2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005662189655832061+0j), (-0.0015391427250737064+0j), (-0.0037438499422502635+0j), (-0.008148975844156069+0j), (-0.01587203765139504+0j), (-0.02766351724926547+0j), (-0.04314467152840492+0j), (-0.06021323966129995+0j), (-0.07519723624994168+0j), (-0.08403434542599673+0j)] + [(-0.08520963193152209+0j)] * 32 + [(-0.08403434542599673+0j), (-0.07519723624994168+0j), (-0.06021323966129995+0j), (-0.04314467152840492+0j), (-0.02766351724926547+0j), (-0.01587203765139504+0j), (-0.008148975844156069+0j), (-0.0037438499422502635+0j), (-0.0015391427250737064+0j), (-0.0005662189655832061+0j)],
        },
        "q12_3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 84 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005136476804361093+0j), (0.0013962391559596142+0j), (0.003396247663228654+0j), (0.007392374319304851+0j), (0.014398379105928448+0j), (0.025095064509458653+0j), (0.03913885228290969+0j), (0.05462266854963783+0j), (0.06821545784006897+0j), (0.07623207491923373+0j)] + [(0.07729824052671945+0j)] * 84 + [(0.07623207491923373+0j), (0.06821545784006897+0j), (0.05462266854963783+0j), (0.03913885228290969+0j), (0.025095064509458653+0j), (0.014398379105928448+0j), (0.007392374319304851+0j), (0.003396247663228654+0j), (0.0013962391559596142+0j), (0.0005136476804361093+0j)],
        },
        "q12_3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 84 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0002553521424438162+0j), (0.0006941190886631113+0j), (0.001688392939570792+0j), (0.003675006608768168+0j), (0.007157935472998664+0j), (0.01247563014752701+0j), (0.019457285925534668+0j), (0.02715482999612888+0j), (0.033912278728598505+0j), (0.037897618143697916+0j)] + [(0.038427646181282436+0j)] * 84 + [(0.037897618143697916+0j), (0.033912278728598505+0j), (0.02715482999612888+0j), (0.019457285925534668+0j), (0.01247563014752701+0j), (0.007157935472998664+0j), (0.003675006608768168+0j), (0.001688392939570792+0j), (0.0006941190886631113+0j), (0.0002553521424438162+0j)],
        },
        "q12_3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002553521424438162+0j), (-0.0006941190886631113+0j), (-0.001688392939570792+0j), (-0.003675006608768168+0j), (-0.007157935472998664+0j), (-0.01247563014752701+0j), (-0.019457285925534668+0j), (-0.02715482999612888+0j), (-0.033912278728598505+0j), (-0.037897618143697916+0j)] + [(-0.038427646181282436+0j)] * 84 + [(-0.037897618143697916+0j), (-0.033912278728598505+0j), (-0.02715482999612888+0j), (-0.019457285925534668+0j), (-0.01247563014752701+0j), (-0.007157935472998664+0j), (-0.003675006608768168+0j), (-0.001688392939570792+0j), (-0.0006941190886631113+0j), (-0.0002553521424438162+0j)],
        },
        "q12_3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005136476804361093+0j), (0.0013962391559596142+0j), (0.003396247663228654+0j), (0.007392374319304851+0j), (0.014398379105928448+0j), (0.025095064509458653+0j), (0.03913885228290969+0j), (0.05462266854963783+0j), (0.06821545784006897+0j), (0.07623207491923373+0j)] + [(0.07729824052671945+0j)] * 84 + [(0.07623207491923373+0j), (0.06821545784006897+0j), (0.05462266854963783+0j), (0.03913885228290969+0j), (0.025095064509458653+0j), (0.014398379105928448+0j), (0.007392374319304851+0j), (0.003396247663228654+0j), (0.0013962391559596142+0j), (0.0005136476804361093+0j)],
        },
        "q12_3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0002553521424438162+0j), (0.0006941190886631113+0j), (0.001688392939570792+0j), (0.003675006608768168+0j), (0.007157935472998664+0j), (0.01247563014752701+0j), (0.019457285925534668+0j), (0.02715482999612888+0j), (0.033912278728598505+0j), (0.037897618143697916+0j)] + [(0.038427646181282436+0j)] * 84 + [(0.037897618143697916+0j), (0.033912278728598505+0j), (0.02715482999612888+0j), (0.019457285925534668+0j), (0.01247563014752701+0j), (0.007157935472998664+0j), (0.003675006608768168+0j), (0.001688392939570792+0j), (0.0006941190886631113+0j), (0.0002553521424438162+0j)],
        },
        "q12_3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002553521424438162+0j), (-0.0006941190886631113+0j), (-0.001688392939570792+0j), (-0.003675006608768168+0j), (-0.007157935472998664+0j), (-0.01247563014752701+0j), (-0.019457285925534668+0j), (-0.02715482999612888+0j), (-0.033912278728598505+0j), (-0.037897618143697916+0j)] + [(-0.038427646181282436+0j)] * 84 + [(-0.037897618143697916+0j), (-0.033912278728598505+0j), (-0.02715482999612888+0j), (-0.019457285925534668+0j), (-0.01247563014752701+0j), (-0.007157935472998664+0j), (-0.003675006608768168+0j), (-0.001688392939570792+0j), (-0.0006941190886631113+0j), (-0.0002553521424438162+0j)],
        },
        "q12_4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005045155839941109+0j), (0.0013714155441455946+0j), (0.003335866077984888+0j), (0.007260945953538794+0j), (0.014142391603965713+0j), (0.024648901588750105+0j), (0.03844300610801177+0j), (0.05365153698200165+0j), (0.0670026612801747+0j), (0.07487675163704735+0j)] + [(0.0759239619809905+0j)] * 32 + [(0.07487675163704735+0j), (0.0670026612801747+0j), (0.05365153698200165+0j), (0.03844300610801177+0j), (0.024648901588750105+0j), (0.014142391603965713+0j), (0.007260945953538794+0j), (0.003335866077984888+0j), (0.0013714155441455946+0j), (0.0005045155839941109+0j)],
        },
        "q12_4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00022595032861955896+0j), (0.0006141966724208969+0j), (0.0014939876199350922+0j), (0.0032518581711642393+0j), (0.006333754856658392+0j), (0.011039158334808279+0j), (0.01721693073276873+0j), (0.024028162452498593+0j), (0.03000754350299156+0j), (0.03353400207069409+0j)] + [(0.03400300150075038+0j)] * 32 + [(0.03353400207069409+0j), (0.03000754350299156+0j), (0.024028162452498593+0j), (0.01721693073276873+0j), (0.011039158334808279+0j), (0.006333754856658392+0j), (0.0032518581711642393+0j), (0.0014939876199350922+0j), (0.0006141966724208969+0j), (0.00022595032861955896+0j)],
        },
        "q12_4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00022595032861955896+0j), (-0.0006141966724208969+0j), (-0.0014939876199350922+0j), (-0.0032518581711642393+0j), (-0.006333754856658392+0j), (-0.011039158334808279+0j), (-0.01721693073276873+0j), (-0.024028162452498593+0j), (-0.03000754350299156+0j), (-0.03353400207069409+0j)] + [(-0.03400300150075038+0j)] * 32 + [(-0.03353400207069409+0j), (-0.03000754350299156+0j), (-0.024028162452498593+0j), (-0.01721693073276873+0j), (-0.011039158334808279+0j), (-0.006333754856658392+0j), (-0.0032518581711642393+0j), (-0.0014939876199350922+0j), (-0.0006141966724208969+0j), (-0.00022595032861955896+0j)],
        },
        "q12_4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005045155839941109+0j), (0.0013714155441455946+0j), (0.003335866077984888+0j), (0.007260945953538794+0j), (0.014142391603965713+0j), (0.024648901588750105+0j), (0.03844300610801177+0j), (0.05365153698200165+0j), (0.0670026612801747+0j), (0.07487675163704735+0j)] + [(0.0759239619809905+0j)] * 32 + [(0.07487675163704735+0j), (0.0670026612801747+0j), (0.05365153698200165+0j), (0.03844300610801177+0j), (0.024648901588750105+0j), (0.014142391603965713+0j), (0.007260945953538794+0j), (0.003335866077984888+0j), (0.0013714155441455946+0j), (0.0005045155839941109+0j)],
        },
        "q12_4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00022595032861955896+0j), (0.0006141966724208969+0j), (0.0014939876199350922+0j), (0.0032518581711642393+0j), (0.006333754856658392+0j), (0.011039158334808279+0j), (0.01721693073276873+0j), (0.024028162452498593+0j), (0.03000754350299156+0j), (0.03353400207069409+0j)] + [(0.03400300150075038+0j)] * 32 + [(0.03353400207069409+0j), (0.03000754350299156+0j), (0.024028162452498593+0j), (0.01721693073276873+0j), (0.011039158334808279+0j), (0.006333754856658392+0j), (0.0032518581711642393+0j), (0.0014939876199350922+0j), (0.0006141966724208969+0j), (0.00022595032861955896+0j)],
        },
        "q12_4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00022595032861955896+0j), (-0.0006141966724208969+0j), (-0.0014939876199350922+0j), (-0.0032518581711642393+0j), (-0.006333754856658392+0j), (-0.011039158334808279+0j), (-0.01721693073276873+0j), (-0.024028162452498593+0j), (-0.03000754350299156+0j), (-0.03353400207069409+0j)] + [(-0.03400300150075038+0j)] * 32 + [(-0.03353400207069409+0j), (-0.03000754350299156+0j), (-0.024028162452498593+0j), (-0.01721693073276873+0j), (-0.011039158334808279+0j), (-0.006333754856658392+0j), (-0.0032518581711642393+0j), (-0.0014939876199350922+0j), (-0.0006141966724208969+0j), (-0.00022595032861955896+0j)],
        },
        "q12_5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 84 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0001241310711956625+0j), (0.0003374232351783254+0j), (0.0008207568661156978+0j), (0.001786483961449053+0j), (0.0034795956255125296+0j), (0.006064618527311404+0j), (0.009458521559216294+0j), (0.013200430210986913+0j), (0.016485342339326647+0j), (0.018422684418935128+0j)] + [(0.018680340170085043+0j)] * 84 + [(0.018422684418935128+0j), (0.016485342339326647+0j), (0.013200430210986913+0j), (0.009458521559216294+0j), (0.006064618527311404+0j), (0.0034795956255125296+0j), (0.001786483961449053+0j), (0.0008207568661156978+0j), (0.0003374232351783254+0j), (0.0001241310711956625+0j)],
        },
        "q12_5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0002308102618338501+0j), (0.0006274073405648289+0j), (0.0015261215853965336+0j), (0.003321801922212349+0j), (0.006469986681533849+0j), (0.01127659800828397+0j), (0.0175872472267855+0j), (0.024544980752762718+0j), (0.03065297145275578+0j), (0.034255280112054566+0j)] + [(0.0347343671835918+0j)] * 84 + [(0.034255280112054566+0j), (0.03065297145275578+0j), (0.024544980752762718+0j), (0.0175872472267855+0j), (0.01127659800828397+0j), (0.006469986681533849+0j), (0.003321801922212349+0j), (0.0015261215853965336+0j), (0.0006274073405648289+0j), (0.0002308102618338501+0j)],
        },
        "q12_5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(5.831587440376806e-05+0j), (0.00015851898170246266+0j), (0.0003855856060807585+0j), (0.0008392771714343294+0j), (0.0016346887166827247+0j), (0.0028491136742709+0j), (0.004443544633745687+0j), (0.006201466102280098+0j), (0.007744693927984771+0j), (0.008654843146092307+0j)] + [(0.008775887943971985+0j)] * 84 + [(0.008654843146092307+0j), (0.007744693927984771+0j), (0.006201466102280098+0j), (0.004443544633745687+0j), (0.0028491136742709+0j), (0.0016346887166827247+0j), (0.0008392771714343294+0j), (0.0003855856060807585+0j), (0.00015851898170246266+0j), (5.831587440376806e-05+0j)],
        },
        "q12_5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-5.831587440376806e-05+0j), (-0.00015851898170246266+0j), (-0.0003855856060807585+0j), (-0.0008392771714343294+0j), (-0.0016346887166827247+0j), (-0.0028491136742709+0j), (-0.004443544633745687+0j), (-0.006201466102280098+0j), (-0.007744693927984771+0j), (-0.008654843146092307+0j)] + [(-0.008775887943971985+0j)] * 84 + [(-0.008654843146092307+0j), (-0.007744693927984771+0j), (-0.006201466102280098+0j), (-0.004443544633745687+0j), (-0.0028491136742709+0j), (-0.0016346887166827247+0j), (-0.0008392771714343294+0j), (-0.0003855856060807585+0j), (-0.00015851898170246266+0j), (-5.831587440376806e-05+0j)],
        },
        "q12_5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0001241310711956625+0j), (0.0003374232351783254+0j), (0.0008207568661156978+0j), (0.001786483961449053+0j), (0.0034795956255125296+0j), (0.006064618527311404+0j), (0.009458521559216294+0j), (0.013200430210986913+0j), (0.016485342339326647+0j), (0.018422684418935128+0j)] + [(0.018680340170085043+0j)] * 84 + [(0.018422684418935128+0j), (0.016485342339326647+0j), (0.013200430210986913+0j), (0.009458521559216294+0j), (0.006064618527311404+0j), (0.0034795956255125296+0j), (0.001786483961449053+0j), (0.0008207568661156978+0j), (0.0003374232351783254+0j), (0.0001241310711956625+0j)],
        },
        "q12_5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(5.831587440376806e-05+0j), (0.00015851898170246266+0j), (0.0003855856060807585+0j), (0.0008392771714343294+0j), (0.0016346887166827247+0j), (0.0028491136742709+0j), (0.004443544633745687+0j), (0.006201466102280098+0j), (0.007744693927984771+0j), (0.008654843146092307+0j)] + [(0.008775887943971985+0j)] * 84 + [(0.008654843146092307+0j), (0.007744693927984771+0j), (0.006201466102280098+0j), (0.004443544633745687+0j), (0.0028491136742709+0j), (0.0016346887166827247+0j), (0.0008392771714343294+0j), (0.0003855856060807585+0j), (0.00015851898170246266+0j), (5.831587440376806e-05+0j)],
        },
        "q12_5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-5.831587440376806e-05+0j), (-0.00015851898170246266+0j), (-0.0003855856060807585+0j), (-0.0008392771714343294+0j), (-0.0016346887166827247+0j), (-0.0028491136742709+0j), (-0.004443544633745687+0j), (-0.006201466102280098+0j), (-0.007744693927984771+0j), (-0.008654843146092307+0j)] + [(-0.008775887943971985+0j)] * 84 + [(-0.008654843146092307+0j), (-0.007744693927984771+0j), (-0.006201466102280098+0j), (-0.004443544633745687+0j), (-0.0028491136742709+0j), (-0.0016346887166827247+0j), (-0.0008392771714343294+0j), (-0.0003855856060807585+0j), (-0.00015851898170246266+0j), (-5.831587440376806e-05+0j)],
        },
        "q12_6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0003100814903685395+0j), (0.0008428888806102992+0j), (0.0020502643683321443+0j), (0.004462666792043051+0j), (0.008692088024746518+0j), (0.015149518435244825+0j), (0.023627544929034936+0j), (0.032974895277240984+0j), (0.04118066067243132+0j), (0.04602017356483014+0j)] + [(0.04666380193723544+0j)] * 32 + [(0.04602017356483014+0j), (0.04118066067243132+0j), (0.032974895277240984+0j), (0.023627544929034936+0j), (0.015149518435244825+0j), (0.008692088024746518+0j), (0.004462666792043051+0j), (0.0020502643683321443+0j), (0.0008428888806102992+0j), (0.0003100814903685395+0j)],
        },
        "q12_6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00015482992756182996+0j), (0.0004208713785929527+0j), (0.0010237382542704469+0j), (0.0022282993264879933+0j), (0.004340134451859872+0j), (0.007564459391425662+0j), (0.011797708613559749+0j), (0.01646502872862917+0j), (0.020562332505828746+0j), (0.02297879867307429+0j)] + [(0.02330017527042556+0j)] * 32 + [(0.02297879867307429+0j), (0.020562332505828746+0j), (0.01646502872862917+0j), (0.011797708613559749+0j), (0.007564459391425662+0j), (0.004340134451859872+0j), (0.0022282993264879933+0j), (0.0010237382542704469+0j), (0.0004208713785929527+0j), (0.00015482992756182996+0j)],
        },
        "q12_6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00015482992756182996+0j), (-0.0004208713785929527+0j), (-0.0010237382542704469+0j), (-0.0022282993264879933+0j), (-0.004340134451859872+0j), (-0.007564459391425662+0j), (-0.011797708613559749+0j), (-0.01646502872862917+0j), (-0.020562332505828746+0j), (-0.02297879867307429+0j)] + [(-0.02330017527042556+0j)] * 32 + [(-0.02297879867307429+0j), (-0.020562332505828746+0j), (-0.01646502872862917+0j), (-0.011797708613559749+0j), (-0.007564459391425662+0j), (-0.004340134451859872+0j), (-0.0022282993264879933+0j), (-0.0010237382542704469+0j), (-0.0004208713785929527+0j), (-0.00015482992756182996+0j)],
        },
        "q12_6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0003100814903685395+0j), (0.0008428888806102992+0j), (0.0020502643683321443+0j), (0.004462666792043051+0j), (0.008692088024746518+0j), (0.015149518435244825+0j), (0.023627544929034936+0j), (0.032974895277240984+0j), (0.04118066067243132+0j), (0.04602017356483014+0j)] + [(0.04666380193723544+0j)] * 32 + [(0.04602017356483014+0j), (0.04118066067243132+0j), (0.032974895277240984+0j), (0.023627544929034936+0j), (0.015149518435244825+0j), (0.008692088024746518+0j), (0.004462666792043051+0j), (0.0020502643683321443+0j), (0.0008428888806102992+0j), (0.0003100814903685395+0j)],
        },
        "q12_6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00015482992756182996+0j), (0.0004208713785929527+0j), (0.0010237382542704469+0j), (0.0022282993264879933+0j), (0.004340134451859872+0j), (0.007564459391425662+0j), (0.011797708613559749+0j), (0.01646502872862917+0j), (0.020562332505828746+0j), (0.02297879867307429+0j)] + [(0.02330017527042556+0j)] * 32 + [(0.02297879867307429+0j), (0.020562332505828746+0j), (0.01646502872862917+0j), (0.011797708613559749+0j), (0.007564459391425662+0j), (0.004340134451859872+0j), (0.0022282993264879933+0j), (0.0010237382542704469+0j), (0.0004208713785929527+0j), (0.00015482992756182996+0j)],
        },
        "q12_6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00015482992756182996+0j), (-0.0004208713785929527+0j), (-0.0010237382542704469+0j), (-0.0022282993264879933+0j), (-0.004340134451859872+0j), (-0.007564459391425662+0j), (-0.011797708613559749+0j), (-0.01646502872862917+0j), (-0.020562332505828746+0j), (-0.02297879867307429+0j)] + [(-0.02330017527042556+0j)] * 32 + [(-0.02297879867307429+0j), (-0.020562332505828746+0j), (-0.01646502872862917+0j), (-0.011797708613559749+0j), (-0.007564459391425662+0j), (-0.004340134451859872+0j), (-0.0022282993264879933+0j), (-0.0010237382542704469+0j), (-0.0004208713785929527+0j), (-0.00015482992756182996+0j)],
        },
        "q12_7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 84 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0012236318384043507+0j), (0.003326176191058481+0j), (0.008090675632574724+0j), (0.017610406749669433+0j), (0.034300388703150185+0j), (0.05978245612734586+0j), (0.09323812332085506+0j), (0.1301242833982944+0j), (0.16250556415161435+0j), (0.18160306671608326+0j)] + [(0.1841429286331537+0j)] * 84 + [(0.18160306671608326+0j), (0.16250556415161435+0j), (0.1301242833982944+0j), (0.09323812332085506+0j), (0.05978245612734586+0j), (0.034300388703150185+0j), (0.017610406749669433+0j), (0.008090675632574724+0j), (0.003326176191058481+0j), (0.0012236318384043507+0j)],
        },
        "q12_7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 84 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005964190784955906+0j), (0.0016212351432208527+0j), (0.003943533629755371+0j), (0.00858361333525516+0j), (0.016718595888327338+0j), (0.029138991218282048+0j), (0.04544585540059031+0j), (0.0634248004657296+0j), (0.0792079903282838+0j), (0.08851643958857824+0j)] + [(0.08975441171102691+0j)] * 84 + [(0.08851643958857824+0j), (0.0792079903282838+0j), (0.0634248004657296+0j), (0.04544585540059031+0j), (0.029138991218282048+0j), (0.016718595888327338+0j), (0.00858361333525516+0j), (0.003943533629755371+0j), (0.0016212351432208527+0j), (0.0005964190784955906+0j)],
        },
        "q12_7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005964190784955906+0j), (-0.0016212351432208527+0j), (-0.003943533629755371+0j), (-0.00858361333525516+0j), (-0.016718595888327338+0j), (-0.029138991218282048+0j), (-0.04544585540059031+0j), (-0.0634248004657296+0j), (-0.0792079903282838+0j), (-0.08851643958857824+0j)] + [(-0.08975441171102691+0j)] * 84 + [(-0.08851643958857824+0j), (-0.0792079903282838+0j), (-0.0634248004657296+0j), (-0.04544585540059031+0j), (-0.029138991218282048+0j), (-0.016718595888327338+0j), (-0.00858361333525516+0j), (-0.003943533629755371+0j), (-0.0016212351432208527+0j), (-0.0005964190784955906+0j)],
        },
        "q12_7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0012236318384043507+0j), (0.003326176191058481+0j), (0.008090675632574724+0j), (0.017610406749669433+0j), (0.034300388703150185+0j), (0.05978245612734586+0j), (0.09323812332085506+0j), (0.1301242833982944+0j), (0.16250556415161435+0j), (0.18160306671608326+0j)] + [(0.1841429286331537+0j)] * 84 + [(0.18160306671608326+0j), (0.16250556415161435+0j), (0.1301242833982944+0j), (0.09323812332085506+0j), (0.05978245612734586+0j), (0.034300388703150185+0j), (0.017610406749669433+0j), (0.008090675632574724+0j), (0.003326176191058481+0j), (0.0012236318384043507+0j)],
        },
        "q12_7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005964190784955906+0j), (0.0016212351432208527+0j), (0.003943533629755371+0j), (0.00858361333525516+0j), (0.016718595888327338+0j), (0.029138991218282048+0j), (0.04544585540059031+0j), (0.0634248004657296+0j), (0.0792079903282838+0j), (0.08851643958857824+0j)] + [(0.08975441171102691+0j)] * 84 + [(0.08851643958857824+0j), (0.0792079903282838+0j), (0.0634248004657296+0j), (0.04544585540059031+0j), (0.029138991218282048+0j), (0.016718595888327338+0j), (0.00858361333525516+0j), (0.003943533629755371+0j), (0.0016212351432208527+0j), (0.0005964190784955906+0j)],
        },
        "q12_7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005964190784955906+0j), (-0.0016212351432208527+0j), (-0.003943533629755371+0j), (-0.00858361333525516+0j), (-0.016718595888327338+0j), (-0.029138991218282048+0j), (-0.04544585540059031+0j), (-0.0634248004657296+0j), (-0.0792079903282838+0j), (-0.08851643958857824+0j)] + [(-0.08975441171102691+0j)] * 84 + [(-0.08851643958857824+0j), (-0.0792079903282838+0j), (-0.0634248004657296+0j), (-0.04544585540059031+0j), (-0.029138991218282048+0j), (-0.016718595888327338+0j), (-0.00858361333525516+0j), (-0.003943533629755371+0j), (-0.0016212351432208527+0j), (-0.0005964190784955906+0j)],
        },
        "q12_8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 32 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q12_8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 32 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q12_8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 32 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
        "q12_8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 32 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q12_8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 32 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q12_8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 32 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
        "stark_wf": {
            "type": "constant",
            "sample": 0.0,
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
    },
    "elements": {
        "q1": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q1",
            },
            "intermediate_frequency": 362155363.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q1_grft",
                "X180": "q1_X180",
                "X360": "q1_X360",
                "Y360": "q1_Y360",
                "X90": "q1_X90",
                "mX90": "q1_mX90",
                "Y180": "q1_Y180",
                "Y90": "q1_Y90",
                "mY90": "q1_mY90",
                "I": "zero",
                "d_X180": "q1_d_X180",
                "d_X90": "q1_d_X90",
                "d_mX90": "q1_d_mX90",
                "d_Y180": "q1_d_Y180",
                "d_Y90": "q1_d_Y90",
                "d_Y360": "q1_d_Y360",
                "d_X360": "q1_d_X360",
                "d_mY90": "q1_d_mY90",
            },
        },
        "rr1": {
            "mixInputs": {
                "I": ('con1', 5),
                "Q": ('con1', 6),
                "lo_frequency": 7399028000.0,
                "mixer": "mixer_rr1",
            },
            "intermediate_frequency": -14273000.0,
            "outputs": {
                "out1": ('con1', 1),
                "out2": ('con1', 2),
            },
            "time_of_flight": 340,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q1_ro_pulse",
            },
        },
        "q2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q2",
            },
            "intermediate_frequency": 255421989.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q2_grft",
                "X180": "q2_X180",
                "X360": "q2_X360",
                "Y360": "q2_Y360",
                "X90": "q2_X90",
                "mX90": "q2_mX90",
                "Y180": "q2_Y180",
                "Y90": "q2_Y90",
                "mY90": "q2_mY90",
                "I": "zero",
                "d_X180": "q2_d_X180",
                "d_X90": "q2_d_X90",
                "d_mX90": "q2_d_mX90",
                "d_Y180": "q2_d_Y180",
                "d_Y90": "q2_d_Y90",
                "d_Y360": "q2_d_Y360",
                "d_X360": "q2_d_X360",
                "d_mY90": "q2_d_mY90",
            },
        },
        "rr2": {
            "mixInputs": {
                "I": ('con1', 9),
                "Q": ('con1', 10),
                "lo_frequency": 7399028000.0,
                "mixer": "mixer_rr2",
            },
            "intermediate_frequency": 14273000.0,
            "outputs": {
                "out1": ('con1', 1),
                "out2": ('con1', 2),
            },
            "time_of_flight": 340,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q2_ro_pulse",
            },
        },
        "q3": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q3",
            },
            "intermediate_frequency": 359962738.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q3_grft",
                "X180": "q3_X180",
                "X360": "q3_X360",
                "Y360": "q3_Y360",
                "X90": "q3_X90",
                "mX90": "q3_mX90",
                "Y180": "q3_Y180",
                "Y90": "q3_Y90",
                "mY90": "q3_mY90",
                "I": "zero",
                "d_X180": "q3_d_X180",
                "d_X90": "q3_d_X90",
                "d_mX90": "q3_d_mX90",
                "d_Y180": "q3_d_Y180",
                "d_Y90": "q3_d_Y90",
                "d_Y360": "q3_d_Y360",
                "d_X360": "q3_d_X360",
                "d_mY90": "q3_d_mY90",
            },
        },
        "rr3": {
            "mixInputs": {
                "I": ('con2', 8),
                "Q": ('con2', 7),
                "lo_frequency": 7421703000.0,
                "mixer": "mixer_rr3",
            },
            "intermediate_frequency": 52410500.0,
            "outputs": {
                "out1": ('con2', 1),
                "out2": ('con2', 2),
            },
            "time_of_flight": 340,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q3_ro_pulse",
            },
        },
        "q4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q4",
            },
            "intermediate_frequency": 298673853.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q4_grft",
                "X180": "q4_X180",
                "X360": "q4_X360",
                "Y360": "q4_Y360",
                "X90": "q4_X90",
                "mX90": "q4_mX90",
                "Y180": "q4_Y180",
                "Y90": "q4_Y90",
                "mY90": "q4_mY90",
                "I": "zero",
                "d_X180": "q4_d_X180",
                "d_X90": "q4_d_X90",
                "d_mX90": "q4_d_mX90",
                "d_Y180": "q4_d_Y180",
                "d_Y90": "q4_d_Y90",
                "d_Y360": "q4_d_Y360",
                "d_X360": "q4_d_X360",
                "d_mY90": "q4_d_mY90",
            },
        },
        "rr4": {
            "mixInputs": {
                "I": ('con2', 9),
                "Q": ('con2', 10),
                "lo_frequency": 7421703000.0,
                "mixer": "mixer_rr4",
            },
            "intermediate_frequency": -52210500.0,
            "outputs": {
                "out1": ('con2', 1),
                "out2": ('con2', 2),
            },
            "time_of_flight": 340,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q4_ro_pulse",
            },
        },
        "q5": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q5",
            },
            "intermediate_frequency": -45252279.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q5_grft",
                "X180": "q5_X180",
                "X360": "q5_X360",
                "Y360": "q5_Y360",
                "X90": "q5_X90",
                "mX90": "q5_mX90",
                "Y180": "q5_Y180",
                "Y90": "q5_Y90",
                "mY90": "q5_mY90",
                "I": "zero",
                "d_X180": "q5_d_X180",
                "d_X90": "q5_d_X90",
                "d_mX90": "q5_d_mX90",
                "d_Y180": "q5_d_Y180",
                "d_Y90": "q5_d_Y90",
                "d_Y360": "q5_d_Y360",
                "d_X360": "q5_d_X360",
                "d_mY90": "q5_d_mY90",
            },
        },
        "rr5": {
            "mixInputs": {
                "I": ('con3', 7),
                "Q": ('con3', 8),
                "lo_frequency": 7365673000.0,
                "mixer": "mixer_rr5",
            },
            "intermediate_frequency": 31068000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q5_ro_pulse",
            },
        },
        "q6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q6",
            },
            "intermediate_frequency": 319918280.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q6_grft",
                "X180": "q6_X180",
                "X360": "q6_X360",
                "Y360": "q6_Y360",
                "X90": "q6_X90",
                "mX90": "q6_mX90",
                "Y180": "q6_Y180",
                "Y90": "q6_Y90",
                "mY90": "q6_mY90",
                "I": "zero",
                "d_X180": "q6_d_X180",
                "d_X90": "q6_d_X90",
                "d_mX90": "q6_d_mX90",
                "d_Y180": "q6_d_Y180",
                "d_Y90": "q6_d_Y90",
                "d_Y360": "q6_d_Y360",
                "d_X360": "q6_d_X360",
                "d_mY90": "q6_d_mY90",
            },
        },
        "rr6": {
            "mixInputs": {
                "I": ('con3', 9),
                "Q": ('con3', 10),
                "lo_frequency": 7365673000.0,
                "mixer": "mixer_rr6",
            },
            "intermediate_frequency": -30938000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q6_ro_pulse",
            },
        },
        "q7": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q7",
            },
            "intermediate_frequency": -136848020.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q7_grft",
                "X180": "q7_X180",
                "X360": "q7_X360",
                "Y360": "q7_Y360",
                "X90": "q7_X90",
                "mX90": "q7_mX90",
                "Y180": "q7_Y180",
                "Y90": "q7_Y90",
                "mY90": "q7_mY90",
                "I": "zero",
                "d_X180": "q7_d_X180",
                "d_X90": "q7_d_X90",
                "d_mX90": "q7_d_mX90",
                "d_Y180": "q7_d_Y180",
                "d_Y90": "q7_d_Y90",
                "d_Y360": "q7_d_Y360",
                "d_X360": "q7_d_X360",
                "d_mY90": "q7_d_mY90",
            },
        },
        "rr7": {
            "mixInputs": {
                "I": ('con3', 7),
                "Q": ('con3', 8),
                "lo_frequency": 7036398000.0,
                "mixer": "mixer_rr7",
            },
            "intermediate_frequency": 20000000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q7_ro_pulse",
            },
        },
        "q8": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4300000000.0,
                "mixer": "mixer_q8",
            },
            "intermediate_frequency": -140337100.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q8_grft",
                "X180": "q8_X180",
                "X360": "q8_X360",
                "Y360": "q8_Y360",
                "X90": "q8_X90",
                "mX90": "q8_mX90",
                "Y180": "q8_Y180",
                "Y90": "q8_Y90",
                "mY90": "q8_mY90",
                "I": "zero",
                "d_X180": "q8_d_X180",
                "d_X90": "q8_d_X90",
                "d_mX90": "q8_d_mX90",
                "d_Y180": "q8_d_Y180",
                "d_Y90": "q8_d_Y90",
                "d_Y360": "q8_d_Y360",
                "d_X360": "q8_d_X360",
                "d_mY90": "q8_d_mY90",
            },
        },
        "rr8": {
            "mixInputs": {
                "I": ('con3', 7),
                "Q": ('con3', 8),
                "lo_frequency": 7036398000.0,
                "mixer": "mixer_rr8",
            },
            "intermediate_frequency": 20000000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q8_ro_pulse",
            },
        },
        "cr_c1t2": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c1t2",
            },
            "intermediate_frequency": 255421989.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c1t2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q2",
            },
            "intermediate_frequency": 255421989.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c1t4": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c1t4",
            },
            "intermediate_frequency": 298673853.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c1t4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q4",
            },
            "intermediate_frequency": 298673853.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c1t6": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c1t6",
            },
            "intermediate_frequency": 319918280.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c1t6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q6",
            },
            "intermediate_frequency": 319918280.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c3t2": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c3t2",
            },
            "intermediate_frequency": 255421989.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c3t2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q2",
            },
            "intermediate_frequency": 255421989.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c3t4": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c3t4",
            },
            "intermediate_frequency": 298673853.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c3t4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q4",
            },
            "intermediate_frequency": 298673853.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c3t6": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c3t6",
            },
            "intermediate_frequency": 319918280.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c3t6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q6",
            },
            "intermediate_frequency": 319918280.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c5t2": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c5t2",
            },
            "intermediate_frequency": 255421989.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c5t2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q2",
            },
            "intermediate_frequency": 255421989.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c5t4": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c5t4",
            },
            "intermediate_frequency": 298673853.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c5t4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q4",
            },
            "intermediate_frequency": 298673853.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c5t6": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c5t6",
            },
            "intermediate_frequency": 319918280.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c5t6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q6",
            },
            "intermediate_frequency": 319918280.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "q12_1": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_1",
            },
            "intermediate_frequency": -11320000.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_1_grft",
                "X180": "q12_1_X180",
                "X360": "q12_1_X360",
                "X90": "q12_1_X90",
                "mX90": "q12_1_mX90",
                "Y180": "q12_1_Y180",
                "Y90": "q12_1_Y90",
                "mY90": "q12_1_mY90",
                "I": "zero",
            },
        },
        "q12_2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_2",
            },
            "intermediate_frequency": -114664284.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_2_grft",
                "X180": "q12_2_X180",
                "X360": "q12_2_X360",
                "X90": "q12_2_X90",
                "mX90": "q12_2_mX90",
                "Y180": "q12_2_Y180",
                "Y90": "q12_2_Y90",
                "mY90": "q12_2_mY90",
                "I": "zero",
            },
        },
        "q12_3": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_3",
            },
            "intermediate_frequency": -8168081.000000001,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_3_grft",
                "X180": "q12_3_X180",
                "X360": "q12_3_X360",
                "X90": "q12_3_X90",
                "mX90": "q12_3_mX90",
                "Y180": "q12_3_Y180",
                "Y90": "q12_3_Y90",
                "mY90": "q12_3_mY90",
                "I": "zero",
            },
        },
        "q12_4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_4",
            },
            "intermediate_frequency": 30572017.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_4_grft",
                "X180": "q12_4_X180",
                "X360": "q12_4_X360",
                "X90": "q12_4_X90",
                "mX90": "q12_4_mX90",
                "Y180": "q12_4_Y180",
                "Y90": "q12_4_Y90",
                "mY90": "q12_4_mY90",
                "I": "zero",
            },
        },
        "q12_5": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_5",
            },
            "intermediate_frequency": -323684090.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_5_grft",
                "X180": "q12_5_X180",
                "X360": "q12_5_X360",
                "X90": "q12_5_X90",
                "mX90": "q12_5_mX90",
                "Y180": "q12_5_Y180",
                "Y90": "q12_5_Y90",
                "mY90": "q12_5_mY90",
                "I": "zero",
            },
        },
        "q12_6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_6",
            },
            "intermediate_frequency": -48785066.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_6_grft",
                "X180": "q12_6_X180",
                "X360": "q12_6_X360",
                "X90": "q12_6_X90",
                "mX90": "q12_6_mX90",
                "Y180": "q12_6_Y180",
                "Y90": "q12_6_Y90",
                "mY90": "q12_6_mY90",
                "I": "zero",
            },
        },
        "q12_7": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_7",
            },
            "intermediate_frequency": -204595000.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_7_grft",
                "X180": "q12_7_X180",
                "X360": "q12_7_X360",
                "X90": "q12_7_X90",
                "mX90": "q12_7_mX90",
                "Y180": "q12_7_Y180",
                "Y90": "q12_7_Y90",
                "mY90": "q12_7_mY90",
                "I": "zero",
            },
        },
        "q12_8": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4300000000.0,
                "mixer": "mixer_q12_8",
            },
            "intermediate_frequency": -204595000.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_8_grft",
                "X180": "q12_8_X180",
                "X360": "q12_8_X360",
                "X90": "q12_8_X90",
                "mX90": "q12_8_mX90",
                "Y180": "q12_8_Y180",
                "Y90": "q12_8_Y90",
                "mY90": "q12_8_mY90",
                "I": "zero",
            },
        },
        "stark_1": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_stark_1",
            },
            "intermediate_frequency": 402155363.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
        "stark_2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_stark_2",
            },
            "intermediate_frequency": 295421989.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
        "stark_3": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_stark_3",
            },
            "intermediate_frequency": 399962738.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
        "stark_4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_stark_4",
            },
            "intermediate_frequency": 338673853.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
        "stark_5": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_stark_5",
            },
            "intermediate_frequency": -5252279.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
        "stark_6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_stark_6",
            },
            "intermediate_frequency": 359918280.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
        "stark_7": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_stark_7",
            },
            "intermediate_frequency": -96848020.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
        "stark_8": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4300000000.0,
                "mixer": "mixer_stark_8",
            },
            "intermediate_frequency": -100337100.0,
            "sticky": {
                "analog": True,
                "duration": 4,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
        },
    },
    "integration_weights": {
        "integW_cos_rr1": {
            "cosine": [(-0.9740589738999803, 3040)],
            "sine": [(-0.22629431138435055, 3040)],
        },
        "integW_sin_rr1": {
            "cosine": [(0.22629431138435055, 3040)],
            "sine": [(-0.9740589738999803, 3040)],
        },
        "integW_minus_sin_rr1": {
            "cosine": [(-0.22629431138435055, 3040)],
            "sine": [(0.9740589738999803, 3040)],
        },
        "integW_cos_rr2": {
            "cosine": [(-0.31412402771819214, 10000)],
            "sine": [(0.9493819543313957, 10000)],
        },
        "integW_sin_rr2": {
            "cosine": [(-0.9493819543313957, 10000)],
            "sine": [(-0.31412402771819214, 10000)],
        },
        "integW_minus_sin_rr2": {
            "cosine": [(0.9493819543313957, 10000)],
            "sine": [(0.31412402771819214, 10000)],
        },
        "integW_cos_rr3": {
            "cosine": [(0.5459374486282426, 4000)],
            "sine": [(0.8378259378804676, 4000)],
        },
        "integW_sin_rr3": {
            "cosine": [(-0.8378259378804676, 4000)],
            "sine": [(0.5459374486282426, 4000)],
        },
        "integW_minus_sin_rr3": {
            "cosine": [(0.8378259378804676, 4000)],
            "sine": [(-0.5459374486282426, 4000)],
        },
        "integW_cos_rr4": {
            "cosine": [(-0.999764306047515, 3200)],
            "sine": [(0.021710190080485362, 3200)],
        },
        "integW_sin_rr4": {
            "cosine": [(-0.021710190080485362, 3200)],
            "sine": [(-0.999764306047515, 3200)],
        },
        "integW_minus_sin_rr4": {
            "cosine": [(0.021710190080485362, 3200)],
            "sine": [(0.999764306047515, 3200)],
        },
        "integW_cos_rr5": {
            "cosine": [(-0.9996569764968893, 1760)],
            "sine": [(0.026190252787966134, 1760)],
        },
        "integW_sin_rr5": {
            "cosine": [(-0.026190252787966134, 1760)],
            "sine": [(-0.9996569764968893, 1760)],
        },
        "integW_minus_sin_rr5": {
            "cosine": [(0.026190252787966134, 1760)],
            "sine": [(0.9996569764968893, 1760)],
        },
        "integW_cos_rr6": {
            "cosine": [(-0.2144083768151524, 1040)],
            "sine": [(-0.9767441056650875, 1040)],
        },
        "integW_sin_rr6": {
            "cosine": [(0.9767441056650875, 1040)],
            "sine": [(-0.2144083768151524, 1040)],
        },
        "integW_minus_sin_rr6": {
            "cosine": [(-0.9767441056650875, 1040)],
            "sine": [(0.2144083768151524, 1040)],
        },
        "integW_cos_rr7": {
            "cosine": [(0.8232967711436545, 4000)],
            "sine": [(-0.5676111579456776, 4000)],
        },
        "integW_sin_rr7": {
            "cosine": [(0.5676111579456776, 4000)],
            "sine": [(0.8232967711436545, 4000)],
        },
        "integW_minus_sin_rr7": {
            "cosine": [(-0.5676111579456776, 4000)],
            "sine": [(-0.8232967711436545, 4000)],
        },
        "integW_cos_rr8": {
            "cosine": [(0.8416630519706616, 2000)],
            "sine": [(-0.5400030619796812, 2000)],
        },
        "integW_sin_rr8": {
            "cosine": [(0.5400030619796812, 2000)],
            "sine": [(0.8416630519706616, 2000)],
        },
        "integW_minus_sin_rr8": {
            "cosine": [(-0.5400030619796812, 2000)],
            "sine": [(-0.8416630519706616, 2000)],
        },
    },
    "mixers": {
        "mixer_q1": [{'intermediate_frequency': 362155363.0, 'lo_frequency': 4700000000.0, 'correction': [1.0403961374441604, 0.08620365944377892, 0.09111386578534227, 0.9843282748001614]}],
        "mixer_rr1": [{'intermediate_frequency': -14273000.0, 'lo_frequency': 7399028000.0, 'correction': [1.6535896287305312, 0.2754312691549308, 0.5115152141448717, 0.8903944154702859]}],
        "mixer_q2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': [1.0137535772204032, -0.023556778310603196, -0.024164067010625925, 0.9882760327415352]}],
        "mixer_rr2": [{'intermediate_frequency': 14273000.0, 'lo_frequency': 7399028000.0, 'correction': [1.4325167632183953, 0.03306994338092208, 0.06141560913599801, 0.7713551801945223]}],
        "mixer_q3": [{'intermediate_frequency': 359962738.0, 'lo_frequency': 4700000000.0, 'correction': [1.0039990793637215, 0.042815700862599504, 0.0429226956450435, 1.001496378602361]}],
        "mixer_rr3": [{'intermediate_frequency': 52410500.0, 'lo_frequency': 7421703000.0, 'correction': [1.431804631737311, 0.02992665337714791, 0.05557807055756039, 0.7709717247816292]}],
        "mixer_q4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': [1.0193579031557578, 0.12486540584167889, 0.1240894560926829, 1.0257320991108114]}],
        "mixer_rr4": [{'intermediate_frequency': -52210500.0, 'lo_frequency': 7421703000.0, 'correction': [1.2882567049749953, 0.031353284497739886, 0.049251912255567694, 0.8200915888831498]}],
        "mixer_q5": [{'intermediate_frequency': -45252279.0, 'lo_frequency': 4700000000.0, 'correction': [0.9382861082818438, 0.037662667021408955, 0.03288392472810774, 1.0746392822395396]}],
        "mixer_rr5": [{'intermediate_frequency': 31068000.0, 'lo_frequency': 7365673000.0, 'correction': [0.9375057045439633, 0.043820895142713874, 0.03813999878401696, 1.0771457914081837]}],
        "mixer_q6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': [0.9390212711106408, 0.028444429315723052, 0.024919012889332414, 1.071869270692552]}],
        "mixer_rr6": [{'intermediate_frequency': -30938000.0, 'lo_frequency': 7365673000.0, 'correction': [1.1624594745793735, 0.15129870545135313, 0.1870056694732569, 0.9404988316071948]}],
        "mixer_q7": [{'intermediate_frequency': -136848020.0, 'lo_frequency': 4700000000.0, 'correction': [0.9531282230165004, 0.04084422885368196, 0.03684101032608277, 1.0566970591527876]}],
        "mixer_rr7": [{'intermediate_frequency': 20000000.0, 'lo_frequency': 7036398000.0, 'correction': [1.433221002403429, 0.035912548247809734, 0.06669473246021809, 0.7717343859095386]}],
        "mixer_q8": [{'intermediate_frequency': -140337100.0, 'lo_frequency': 4300000000.0, 'correction': [0.9501664441395031, 0.05850250509417677, 0.0521698803260484, 1.0655021037269372]}],
        "mixer_rr8": [{'intermediate_frequency': 20000000.0, 'lo_frequency': 7036398000.0, 'correction': [1.4323943156170444, 0.032550787359555716, 0.060451462239174865, 0.7712892468707166]}],
        "mixer_cr_c1t2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': [0.9994478269317117, 0.05799530611969734, 0.05735960529050436, 1.010524434050917]}],
        "mixer_cr_c1t4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': [1.0004610094040567, 0.05006488688367021, 0.0497401592685447, 1.006992498695352]}],
        "mixer_cr_c1t6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': [0.9985726912731867, 0.0443569355559235, 0.043972928556151814, 1.007293031623957]}],
        "mixer_cr_c3t2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': [1.0076884136821063, 0.03998122052115623, 0.040401894989739694, 0.9971961140503417]}],
        "mixer_cr_c3t4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': [1.0056392481876182, 0.03830960018530201, 0.038571790344144825, 0.9988034567486318]}],
        "mixer_cr_c3t6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': [1.0075217905279001, 0.039895832667472875, 0.04030322579213445, 0.9973375573222321]}],
        "mixer_cr_c5t2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': [0.9684553435373363, 0.0713975510023274, 0.06593422441851332, 1.048701799308168]}],
        "mixer_cr_c5t4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': [0.9634597757129584, 0.072616433625605, 0.06631787837323827, 1.054964582254082]}],
        "mixer_cr_c5t6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': [0.9691754975480648, 0.0701122327240297, 0.06487874415554874, 1.0473547063673503]}],
        "mixer_q12_1": [{'intermediate_frequency': -11320000.0, 'lo_frequency': 4700000000.0, 'correction': [0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035]}],
        "mixer_q12_2": [{'intermediate_frequency': -114664284.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_3": [{'intermediate_frequency': -8168081.000000001, 'lo_frequency': 4700000000.0, 'correction': [1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166]}],
        "mixer_q12_4": [{'intermediate_frequency': 30572017.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_5": [{'intermediate_frequency': -323684090.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_6": [{'intermediate_frequency': -48785066.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_7": [{'intermediate_frequency': -204595000.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_8": [{'intermediate_frequency': -204595000.0, 'lo_frequency': 4300000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_1": [{'intermediate_frequency': 402155363.0, 'lo_frequency': 4700000000.0, 'correction': [0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035]}],
        "mixer_stark_2": [{'intermediate_frequency': 295421989.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_3": [{'intermediate_frequency': 399962738.0, 'lo_frequency': 4700000000.0, 'correction': [1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166]}],
        "mixer_stark_4": [{'intermediate_frequency': 338673853.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_5": [{'intermediate_frequency': -5252279.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_6": [{'intermediate_frequency': 359918280.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_7": [{'intermediate_frequency': -96848020.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_8": [{'intermediate_frequency': -100337100.0, 'lo_frequency': 4300000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
    },
}

loaded_config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.03439100687984689,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "2": {
                    "offset": -0.00456807440883176,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "3": {
                    "offset": -0.027224942669403993,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "4": {
                    "offset": -0.00746944472185292,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "5": {
                    "offset": 0.007251527048272247,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "6": {
                    "offset": 0.004582863340542396,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "7": {
                    "offset": -0.01004958944627166,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "8": {
                    "offset": 0.004911278856552271,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "9": {
                    "offset": 0.011454769566979228,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "10": {
                    "offset": 0.001733100950205538,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": 0.2629143867543879,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
                "2": {
                    "offset": 0.2840686339716801,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
            },
            "digital_outputs": {},
            "digital_inputs": {},
        },
        "con2": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.023109068899027727,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "2": {
                    "offset": -0.030702739253611902,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "3": {
                    "offset": -0.00977638920851303,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "4": {
                    "offset": -0.027215368254123427,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "5": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "6": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "7": {
                    "offset": 0.011644772330749321,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "8": {
                    "offset": 0.001698276611435881,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "9": {
                    "offset": -0.00027563385255682457,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "10": {
                    "offset": -0.0022497087424338796,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": 0.23809878542844415,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
                "2": {
                    "offset": 0.23036690812516145,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
            },
            "digital_outputs": {},
            "digital_inputs": {},
        },
        "con3": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": 0.003256753126844797,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "2": {
                    "offset": -0.0005252833477161794,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "3": {
                    "offset": -0.0015988851853745718,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "4": {
                    "offset": 0.0026215662243260036,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "5": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "6": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "7": {
                    "offset": -0.008435945429116389,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "8": {
                    "offset": -0.0022479689331722026,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "9": {
                    "offset": -0.011279786195934931,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "10": {
                    "offset": -0.007801638796693005,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": 0.15253875033329783,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
                "2": {
                    "offset": 0.2151648584392131,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
            },
            "digital_outputs": {},
            "digital_inputs": {},
        },
    },
    "oscillators": {},
    "elements": {
        "q1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q1_grft",
                "X180": "q1_X180",
                "X360": "q1_X360",
                "Y360": "q1_Y360",
                "X90": "q1_X90",
                "mX90": "q1_mX90",
                "Y180": "q1_Y180",
                "Y90": "q1_Y90",
                "mY90": "q1_mY90",
                "I": "zero",
                "d_X180": "q1_d_X180",
                "d_X90": "q1_d_X90",
                "d_mX90": "q1_d_mX90",
                "d_Y180": "q1_d_Y180",
                "d_Y90": "q1_d_Y90",
                "d_Y360": "q1_d_Y360",
                "d_X360": "q1_d_X360",
                "d_mY90": "q1_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_q1",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 362155363.0,
        },
        "rr1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con1', 1, 1),
                "out2": ('con1', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q1_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 5),
                "Q": ('con1', 1, 6),
                "mixer": "mixer_rr1",
                "lo_frequency": 7399028000.0,
            },
            "smearing": 0,
            "time_of_flight": 340,
            "intermediate_frequency": -14273000.0,
        },
        "q2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q2_grft",
                "X180": "q2_X180",
                "X360": "q2_X360",
                "Y360": "q2_Y360",
                "X90": "q2_X90",
                "mX90": "q2_mX90",
                "Y180": "q2_Y180",
                "Y90": "q2_Y90",
                "mY90": "q2_mY90",
                "I": "zero",
                "d_X180": "q2_d_X180",
                "d_X90": "q2_d_X90",
                "d_mX90": "q2_d_mX90",
                "d_Y180": "q2_d_Y180",
                "d_Y90": "q2_d_Y90",
                "d_Y360": "q2_d_Y360",
                "d_X360": "q2_d_X360",
                "d_mY90": "q2_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_q2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 255421989.0,
        },
        "rr2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con1', 1, 1),
                "out2": ('con1', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q2_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 9),
                "Q": ('con1', 1, 10),
                "mixer": "mixer_rr2",
                "lo_frequency": 7399028000.0,
            },
            "smearing": 0,
            "time_of_flight": 340,
            "intermediate_frequency": 14273000.0,
        },
        "q3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q3_grft",
                "X180": "q3_X180",
                "X360": "q3_X360",
                "Y360": "q3_Y360",
                "X90": "q3_X90",
                "mX90": "q3_mX90",
                "Y180": "q3_Y180",
                "Y90": "q3_Y90",
                "mY90": "q3_mY90",
                "I": "zero",
                "d_X180": "q3_d_X180",
                "d_X90": "q3_d_X90",
                "d_mX90": "q3_d_mX90",
                "d_Y180": "q3_d_Y180",
                "d_Y90": "q3_d_Y90",
                "d_Y360": "q3_d_Y360",
                "d_X360": "q3_d_X360",
                "d_mY90": "q3_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_q3",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 359962738.0,
        },
        "rr3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con2', 1, 1),
                "out2": ('con2', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q3_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 8),
                "Q": ('con2', 1, 7),
                "mixer": "mixer_rr3",
                "lo_frequency": 7421703000.0,
            },
            "smearing": 0,
            "time_of_flight": 340,
            "intermediate_frequency": 52410500.0,
        },
        "q4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q4_grft",
                "X180": "q4_X180",
                "X360": "q4_X360",
                "Y360": "q4_Y360",
                "X90": "q4_X90",
                "mX90": "q4_mX90",
                "Y180": "q4_Y180",
                "Y90": "q4_Y90",
                "mY90": "q4_mY90",
                "I": "zero",
                "d_X180": "q4_d_X180",
                "d_X90": "q4_d_X90",
                "d_mX90": "q4_d_mX90",
                "d_Y180": "q4_d_Y180",
                "d_Y90": "q4_d_Y90",
                "d_Y360": "q4_d_Y360",
                "d_X360": "q4_d_X360",
                "d_mY90": "q4_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_q4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 298673853.0,
        },
        "rr4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con2', 1, 1),
                "out2": ('con2', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q4_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 9),
                "Q": ('con2', 1, 10),
                "mixer": "mixer_rr4",
                "lo_frequency": 7421703000.0,
            },
            "smearing": 0,
            "time_of_flight": 340,
            "intermediate_frequency": -52210500.0,
        },
        "q5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q5_grft",
                "X180": "q5_X180",
                "X360": "q5_X360",
                "Y360": "q5_Y360",
                "X90": "q5_X90",
                "mX90": "q5_mX90",
                "Y180": "q5_Y180",
                "Y90": "q5_Y90",
                "mY90": "q5_mY90",
                "I": "zero",
                "d_X180": "q5_d_X180",
                "d_X90": "q5_d_X90",
                "d_mX90": "q5_d_mX90",
                "d_Y180": "q5_d_Y180",
                "d_Y90": "q5_d_Y90",
                "d_Y360": "q5_d_Y360",
                "d_X360": "q5_d_X360",
                "d_mY90": "q5_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q5",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -45252279.0,
        },
        "rr5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q5_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 7),
                "Q": ('con3', 1, 8),
                "mixer": "mixer_rr5",
                "lo_frequency": 7365673000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 31068000.0,
        },
        "q6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q6_grft",
                "X180": "q6_X180",
                "X360": "q6_X360",
                "Y360": "q6_Y360",
                "X90": "q6_X90",
                "mX90": "q6_mX90",
                "Y180": "q6_Y180",
                "Y90": "q6_Y90",
                "mY90": "q6_mY90",
                "I": "zero",
                "d_X180": "q6_d_X180",
                "d_X90": "q6_d_X90",
                "d_mX90": "q6_d_mX90",
                "d_Y180": "q6_d_Y180",
                "d_Y90": "q6_d_Y90",
                "d_Y360": "q6_d_Y360",
                "d_X360": "q6_d_X360",
                "d_mY90": "q6_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_q6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 319918280.0,
        },
        "rr6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q6_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 9),
                "Q": ('con3', 1, 10),
                "mixer": "mixer_rr6",
                "lo_frequency": 7365673000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": -30938000.0,
        },
        "q7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q7_grft",
                "X180": "q7_X180",
                "X360": "q7_X360",
                "Y360": "q7_Y360",
                "X90": "q7_X90",
                "mX90": "q7_mX90",
                "Y180": "q7_Y180",
                "Y90": "q7_Y90",
                "mY90": "q7_mY90",
                "I": "zero",
                "d_X180": "q7_d_X180",
                "d_X90": "q7_d_X90",
                "d_mX90": "q7_d_mX90",
                "d_Y180": "q7_d_Y180",
                "d_Y90": "q7_d_Y90",
                "d_Y360": "q7_d_Y360",
                "d_X360": "q7_d_X360",
                "d_mY90": "q7_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q7",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -136848020.0,
        },
        "rr7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q7_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 7),
                "Q": ('con3', 1, 8),
                "mixer": "mixer_rr7",
                "lo_frequency": 7036398000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 20000000.0,
        },
        "q8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q8_grft",
                "X180": "q8_X180",
                "X360": "q8_X360",
                "Y360": "q8_Y360",
                "X90": "q8_X90",
                "mX90": "q8_mX90",
                "Y180": "q8_Y180",
                "Y90": "q8_Y90",
                "mY90": "q8_mY90",
                "I": "zero",
                "d_X180": "q8_d_X180",
                "d_X90": "q8_d_X90",
                "d_mX90": "q8_d_mX90",
                "d_Y180": "q8_d_Y180",
                "d_Y90": "q8_d_Y90",
                "d_Y360": "q8_d_Y360",
                "d_X360": "q8_d_X360",
                "d_mY90": "q8_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q8",
                "lo_frequency": 4300000000.0,
            },
            "intermediate_frequency": -140337100.0,
        },
        "rr8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q8_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 7),
                "Q": ('con3', 1, 8),
                "mixer": "mixer_rr8",
                "lo_frequency": 7036398000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 20000000.0,
        },
        "cr_c1t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_cr_c1t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 255421989.0,
        },
        "cr_ac_c1t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 3),
                "mixer": "mixer_q2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 255421989.0,
        },
        "cr_c1t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_cr_c1t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 298673853.0,
        },
        "cr_ac_c1t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 4),
                "mixer": "mixer_q4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 298673853.0,
        },
        "cr_c1t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_cr_c1t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 319918280.0,
        },
        "cr_ac_c1t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 3),
                "mixer": "mixer_q6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 319918280.0,
        },
        "cr_c3t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_cr_c3t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 255421989.0,
        },
        "cr_ac_c3t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 3),
                "mixer": "mixer_q2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 255421989.0,
        },
        "cr_c3t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_cr_c3t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 298673853.0,
        },
        "cr_ac_c3t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 4),
                "mixer": "mixer_q4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 298673853.0,
        },
        "cr_c3t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_cr_c3t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 319918280.0,
        },
        "cr_ac_c3t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 3),
                "mixer": "mixer_q6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 319918280.0,
        },
        "cr_c5t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_cr_c5t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 255421989.0,
        },
        "cr_ac_c5t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 3),
                "mixer": "mixer_q2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 255421989.0,
        },
        "cr_c5t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_cr_c5t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 298673853.0,
        },
        "cr_ac_c5t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 4),
                "mixer": "mixer_q4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 298673853.0,
        },
        "cr_c5t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_cr_c5t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 319918280.0,
        },
        "cr_ac_c5t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 3),
                "mixer": "mixer_q6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 319918280.0,
        },
        "q12_1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_1_grft",
                "X180": "q12_1_X180",
                "X360": "q12_1_X360",
                "X90": "q12_1_X90",
                "mX90": "q12_1_mX90",
                "Y180": "q12_1_Y180",
                "Y90": "q12_1_Y90",
                "mY90": "q12_1_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_q12_1",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -11320000.0,
        },
        "q12_2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_2_grft",
                "X180": "q12_2_X180",
                "X360": "q12_2_X360",
                "X90": "q12_2_X90",
                "mX90": "q12_2_mX90",
                "Y180": "q12_2_Y180",
                "Y90": "q12_2_Y90",
                "mY90": "q12_2_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_q12_2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -114664284.0,
        },
        "q12_3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_3_grft",
                "X180": "q12_3_X180",
                "X360": "q12_3_X360",
                "X90": "q12_3_X90",
                "mX90": "q12_3_mX90",
                "Y180": "q12_3_Y180",
                "Y90": "q12_3_Y90",
                "mY90": "q12_3_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_q12_3",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -8168081.000000001,
        },
        "q12_4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_4_grft",
                "X180": "q12_4_X180",
                "X360": "q12_4_X360",
                "X90": "q12_4_X90",
                "mX90": "q12_4_mX90",
                "Y180": "q12_4_Y180",
                "Y90": "q12_4_Y90",
                "mY90": "q12_4_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_q12_4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 30572017.0,
        },
        "q12_5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_5_grft",
                "X180": "q12_5_X180",
                "X360": "q12_5_X360",
                "X90": "q12_5_X90",
                "mX90": "q12_5_mX90",
                "Y180": "q12_5_Y180",
                "Y90": "q12_5_Y90",
                "mY90": "q12_5_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q12_5",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -323684090.0,
        },
        "q12_6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_6_grft",
                "X180": "q12_6_X180",
                "X360": "q12_6_X360",
                "X90": "q12_6_X90",
                "mX90": "q12_6_mX90",
                "Y180": "q12_6_Y180",
                "Y90": "q12_6_Y90",
                "mY90": "q12_6_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_q12_6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -48785066.0,
        },
        "q12_7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_7_grft",
                "X180": "q12_7_X180",
                "X360": "q12_7_X360",
                "X90": "q12_7_X90",
                "mX90": "q12_7_mX90",
                "Y180": "q12_7_Y180",
                "Y90": "q12_7_Y90",
                "mY90": "q12_7_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q12_7",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -204595000.0,
        },
        "q12_8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_8_grft",
                "X180": "q12_8_X180",
                "X360": "q12_8_X360",
                "X90": "q12_8_X90",
                "mX90": "q12_8_mX90",
                "Y180": "q12_8_Y180",
                "Y90": "q12_8_Y90",
                "mY90": "q12_8_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q12_8",
                "lo_frequency": 4300000000.0,
            },
            "intermediate_frequency": -204595000.0,
        },
        "stark_1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_stark_1",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 402155363.0,
        },
        "stark_2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_stark_2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 295421989.0,
        },
        "stark_3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_stark_3",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 399962738.0,
        },
        "stark_4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_stark_4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 338673853.0,
        },
        "stark_5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_stark_5",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -5252279.0,
        },
        "stark_6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_stark_6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 359918280.0,
        },
        "stark_7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_stark_7",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -96848020.0,
        },
        "stark_8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
                "stark": "stark_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_stark_8",
                "lo_frequency": 4300000000.0,
            },
            "intermediate_frequency": -100337100.0,
        },
    },
    "pulses": {
        "zero": {
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "const_pulse": {
            "length": 100,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_grft": {
            "length": 52,
            "waveforms": {
                "I": "q1_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_X180": {
            "length": 52,
            "waveforms": {
                "I": "q1_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_X360": {
            "length": 52,
            "waveforms": {
                "I": "q1_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_X90": {
            "length": 52,
            "waveforms": {
                "I": "q1_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q1_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_ro_pulse": {
            "length": 3040,
            "waveforms": {
                "I": "q1_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr1",
                "integW_sin": "integW_sin_rr1",
                "integW_minus_sin": "integW_minus_sin_rr1",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q1_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_X180_I_wf",
                "Q": "q1_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_X90_I_wf",
                "Q": "q1_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_mX90_I_wf",
                "Q": "q1_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y180_I_wf",
                "Q": "q1_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y90_I_wf",
                "Q": "q1_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y360_I_wf",
                "Q": "q1_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_X360_I_wf",
                "Q": "q1_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_mY90_I_wf",
                "Q": "q1_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_grft": {
            "length": 52,
            "waveforms": {
                "I": "q2_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_X180": {
            "length": 52,
            "waveforms": {
                "I": "q2_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_X360": {
            "length": 52,
            "waveforms": {
                "I": "q2_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_X90": {
            "length": 52,
            "waveforms": {
                "I": "q2_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q2_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_ro_pulse": {
            "length": 10000,
            "waveforms": {
                "I": "q2_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr2",
                "integW_sin": "integW_sin_rr2",
                "integW_minus_sin": "integW_minus_sin_rr2",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q2_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_X180_I_wf",
                "Q": "q2_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_X90_I_wf",
                "Q": "q2_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_mX90_I_wf",
                "Q": "q2_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y180_I_wf",
                "Q": "q2_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y90_I_wf",
                "Q": "q2_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y360_I_wf",
                "Q": "q2_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_X360_I_wf",
                "Q": "q2_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_mY90_I_wf",
                "Q": "q2_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_grft": {
            "length": 104,
            "waveforms": {
                "I": "q3_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_X180": {
            "length": 104,
            "waveforms": {
                "I": "q3_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_X360": {
            "length": 104,
            "waveforms": {
                "I": "q3_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_Y360": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_X90": {
            "length": 104,
            "waveforms": {
                "I": "q3_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_mX90": {
            "length": 104,
            "waveforms": {
                "I": "q3_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_Y180": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_Y90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_mY90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_ro_pulse": {
            "length": 4000,
            "waveforms": {
                "I": "q3_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr3",
                "integW_sin": "integW_sin_rr3",
                "integW_minus_sin": "integW_minus_sin_rr3",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q3_d_X180": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_X180_I_wf",
                "Q": "q3_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_X90": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_X90_I_wf",
                "Q": "q3_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_mX90": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_mX90_I_wf",
                "Q": "q3_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_Y180": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_Y180_I_wf",
                "Q": "q3_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_Y90": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_Y90_I_wf",
                "Q": "q3_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_Y360": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_Y360_I_wf",
                "Q": "q3_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_X360": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_X360_I_wf",
                "Q": "q3_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_mY90": {
            "length": 104,
            "waveforms": {
                "I": "q3_d_mY90_I_wf",
                "Q": "q3_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_grft": {
            "length": 72,
            "waveforms": {
                "I": "q4_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_X180": {
            "length": 72,
            "waveforms": {
                "I": "q4_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_X360": {
            "length": 72,
            "waveforms": {
                "I": "q4_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_Y360": {
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_X90": {
            "length": 72,
            "waveforms": {
                "I": "q4_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_mX90": {
            "length": 72,
            "waveforms": {
                "I": "q4_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_Y180": {
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_Y90": {
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_mY90": {
            "length": 72,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_ro_pulse": {
            "length": 3200,
            "waveforms": {
                "I": "q4_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr4",
                "integW_sin": "integW_sin_rr4",
                "integW_minus_sin": "integW_minus_sin_rr4",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q4_d_X180": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_X180_I_wf",
                "Q": "q4_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_X90": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_X90_I_wf",
                "Q": "q4_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_mX90": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_mX90_I_wf",
                "Q": "q4_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_Y180": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_Y180_I_wf",
                "Q": "q4_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_Y90": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_Y90_I_wf",
                "Q": "q4_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_Y360": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_Y360_I_wf",
                "Q": "q4_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_X360": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_X360_I_wf",
                "Q": "q4_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_mY90": {
            "length": 72,
            "waveforms": {
                "I": "q4_d_mY90_I_wf",
                "Q": "q4_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_grft": {
            "length": 36,
            "waveforms": {
                "I": "q5_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_X180": {
            "length": 36,
            "waveforms": {
                "I": "q5_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_X360": {
            "length": 36,
            "waveforms": {
                "I": "q5_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_Y360": {
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_X90": {
            "length": 36,
            "waveforms": {
                "I": "q5_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_mX90": {
            "length": 36,
            "waveforms": {
                "I": "q5_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_Y180": {
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_Y90": {
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_mY90": {
            "length": 36,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_ro_pulse": {
            "length": 1760,
            "waveforms": {
                "I": "q5_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr5",
                "integW_sin": "integW_sin_rr5",
                "integW_minus_sin": "integW_minus_sin_rr5",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q5_d_X180": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_X180_I_wf",
                "Q": "q5_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_X90": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_X90_I_wf",
                "Q": "q5_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_mX90": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_mX90_I_wf",
                "Q": "q5_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_Y180": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_Y180_I_wf",
                "Q": "q5_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_Y90": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_Y90_I_wf",
                "Q": "q5_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_Y360": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_Y360_I_wf",
                "Q": "q5_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_X360": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_X360_I_wf",
                "Q": "q5_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_mY90": {
            "length": 36,
            "waveforms": {
                "I": "q5_d_mY90_I_wf",
                "Q": "q5_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_grft": {
            "length": 52,
            "waveforms": {
                "I": "q6_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_X180": {
            "length": 52,
            "waveforms": {
                "I": "q6_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_X360": {
            "length": 52,
            "waveforms": {
                "I": "q6_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_X90": {
            "length": 52,
            "waveforms": {
                "I": "q6_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q6_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_ro_pulse": {
            "length": 1040,
            "waveforms": {
                "I": "q6_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr6",
                "integW_sin": "integW_sin_rr6",
                "integW_minus_sin": "integW_minus_sin_rr6",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q6_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_X180_I_wf",
                "Q": "q6_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_X90_I_wf",
                "Q": "q6_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_mX90_I_wf",
                "Q": "q6_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_Y180_I_wf",
                "Q": "q6_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_Y90_I_wf",
                "Q": "q6_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_Y360_I_wf",
                "Q": "q6_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_X360_I_wf",
                "Q": "q6_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q6_d_mY90_I_wf",
                "Q": "q6_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_grft": {
            "length": 500,
            "waveforms": {
                "I": "q7_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_X180": {
            "length": 500,
            "waveforms": {
                "I": "q7_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_X360": {
            "length": 500,
            "waveforms": {
                "I": "q7_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_Y360": {
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_X90": {
            "length": 500,
            "waveforms": {
                "I": "q7_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_mX90": {
            "length": 500,
            "waveforms": {
                "I": "q7_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_Y180": {
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_Y90": {
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_mY90": {
            "length": 500,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_ro_pulse": {
            "length": 4000,
            "waveforms": {
                "I": "q7_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr7",
                "integW_sin": "integW_sin_rr7",
                "integW_minus_sin": "integW_minus_sin_rr7",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q7_d_X180": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_X180_I_wf",
                "Q": "q7_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_X90": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_X90_I_wf",
                "Q": "q7_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_mX90": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_mX90_I_wf",
                "Q": "q7_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_Y180": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_Y180_I_wf",
                "Q": "q7_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_Y90": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_Y90_I_wf",
                "Q": "q7_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_Y360": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_Y360_I_wf",
                "Q": "q7_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_X360": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_X360_I_wf",
                "Q": "q7_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_mY90": {
            "length": 500,
            "waveforms": {
                "I": "q7_d_mY90_I_wf",
                "Q": "q7_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_grft": {
            "length": 300,
            "waveforms": {
                "I": "q8_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_X180": {
            "length": 300,
            "waveforms": {
                "I": "q8_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_X360": {
            "length": 300,
            "waveforms": {
                "I": "q8_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_Y360": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_X90": {
            "length": 300,
            "waveforms": {
                "I": "q8_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_mX90": {
            "length": 300,
            "waveforms": {
                "I": "q8_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_Y180": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_Y90": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_mY90": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_ro_pulse": {
            "length": 2000,
            "waveforms": {
                "I": "q8_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr8",
                "integW_sin": "integW_sin_rr8",
                "integW_minus_sin": "integW_minus_sin_rr8",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q8_d_X180": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_X180_I_wf",
                "Q": "q8_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_X90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_X90_I_wf",
                "Q": "q8_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_mX90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_mX90_I_wf",
                "Q": "q8_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_Y180": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y180_I_wf",
                "Q": "q8_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_Y90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y90_I_wf",
                "Q": "q8_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_Y360": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y360_I_wf",
                "Q": "q8_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_X360": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_X360_I_wf",
                "Q": "q8_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_mY90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_mY90_I_wf",
                "Q": "q8_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "rise_pulse": {
            "length": 16,
            "waveforms": {
                "I": "rise_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "fall_pulse": {
            "length": 16,
            "waveforms": {
                "I": "fall_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_grft": {
            "length": 104,
            "waveforms": {
                "I": "q12_3_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_X180": {
            "length": 104,
            "waveforms": {
                "I": "q12_3_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_X360": {
            "length": 104,
            "waveforms": {
                "I": "q12_3_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_X90": {
            "length": 104,
            "waveforms": {
                "I": "q12_3_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_mX90": {
            "length": 104,
            "waveforms": {
                "I": "q12_3_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_Y180": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_Y90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_mY90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_grft": {
            "length": 104,
            "waveforms": {
                "I": "q12_5_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_X180": {
            "length": 104,
            "waveforms": {
                "I": "q12_5_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_X360": {
            "length": 104,
            "waveforms": {
                "I": "q12_5_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_X90": {
            "length": 104,
            "waveforms": {
                "I": "q12_5_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_mX90": {
            "length": 104,
            "waveforms": {
                "I": "q12_5_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_Y180": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_Y90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_mY90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_6_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_6_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_6_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_6_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_6_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_grft": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_X180": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_X360": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_X90": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_mX90": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_Y180": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_Y90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_mY90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "stark_pulse": {
            "length": 1000,
            "waveforms": {
                "I": "stark_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
    },
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant",
            "sample": 0.4,
        },
        "q1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001754498242547914, 0.004769220690781325, 0.01160077380536972, 0.025250591495837534, 0.04918143661320847, 0.08571876843888207, 0.13368900544319495, 0.18657803709392473, 0.23300777060530184, 0.2603906268164547] + [0.2640323948139477] * 32 + [0.2603906268164547, 0.23300777060530184, 0.18657803709392473, 0.13368900544319495, 0.08571876843888207, 0.04918143661320847, 0.025250591495837534, 0.01160077380536972, 0.004769220690781325, 0.001754498242547914],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008360056467367242, 0.0022724989580135894, 0.0055276843103134144, 0.01203172312290646, 0.023434596699029586, 0.04084436946608459, 0.06370183836423844, 0.08890307712195691, 0.11102650731452524, 0.12407423905978995] + [0.12580951501286694] * 32 + [0.12407423905978995, 0.11102650731452524, 0.08890307712195691, 0.06370183836423844, 0.04084436946608459, 0.023434596699029586, 0.01203172312290646, 0.0055276843103134144, 0.0022724989580135894, 0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008360056467367242, -0.0022724989580135894, -0.0055276843103134144, -0.01203172312290646, -0.023434596699029586, -0.04084436946608459, -0.06370183836423844, -0.08890307712195691, -0.11102650731452524, -0.12407423905978995] + [-0.12580951501286694] * 32 + [-0.12407423905978995, -0.11102650731452524, -0.08890307712195691, -0.06370183836423844, -0.04084436946608459, -0.023434596699029586, -0.01203172312290646, -0.0055276843103134144, -0.0022724989580135894, -0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001754498242547914, 0.004769220690781325, 0.01160077380536972, 0.025250591495837534, 0.04918143661320847, 0.08571876843888207, 0.13368900544319495, 0.18657803709392473, 0.23300777060530184, 0.2603906268164547] + [0.2640323948139477] * 32 + [0.2603906268164547, 0.23300777060530184, 0.18657803709392473, 0.13368900544319495, 0.08571876843888207, 0.04918143661320847, 0.025250591495837534, 0.01160077380536972, 0.004769220690781325, 0.001754498242547914],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008360056467367242, 0.0022724989580135894, 0.0055276843103134144, 0.01203172312290646, 0.023434596699029586, 0.04084436946608459, 0.06370183836423844, 0.08890307712195691, 0.11102650731452524, 0.12407423905978995] + [0.12580951501286694] * 32 + [0.12407423905978995, 0.11102650731452524, 0.08890307712195691, 0.06370183836423844, 0.04084436946608459, 0.023434596699029586, 0.01203172312290646, 0.0055276843103134144, 0.0022724989580135894, 0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008360056467367242, -0.0022724989580135894, -0.0055276843103134144, -0.01203172312290646, -0.023434596699029586, -0.04084436946608459, -0.06370183836423844, -0.08890307712195691, -0.11102650731452524, -0.12407423905978995] + [-0.12580951501286694] * 32 + [-0.12407423905978995, -0.11102650731452524, -0.08890307712195691, -0.06370183836423844, -0.04084436946608459, -0.023434596699029586, -0.01203172312290646, -0.0055276843103134144, -0.0022724989580135894, -0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_ro_wf": {
            "type": "arbitrary",
            "samples": [0.00040251623963611874, 0.0004213313407659066, 0.00044092469546678196, 0.00046132329105599503, 0.00048255479927748914, 0.0005046475819741386, 0.0005276306962116111, 0.000551533898821395, 0.000576387650330002, 0.0006022231182408695, 0.0006290721796350132, 0.0006569674230560738, 0.0006859421496450338, 0.0007160303734895581, 0.0007472668211526478, 0.0007796869303450725, 0.0008133268477059036, 0.0008482234256553598, 0.000884414218284159, 0.0009219374762435797, 0.0009608321406005604, 0.001001137835622318, 0.0010428948604552203, 0.0010861441796629664, 0.0011309274125895375, 0.0011772868215128417, 0.0012252652985555777, 0.0012749063513204572, 0.0013262540872176981, 0.0013793531964535074, 0.0014342489336492182, 0.0014909870980617508, 0.001549614012377179, 0.0016101765000504122, 0.001672721861165288, 0.0017372978467908137, 0.0018039526318107697, 0.001872734786205532, 0.0019436932447666644, 0.002016877275226666, 0.002092336444788167, 0.0021701205850388917, 0.002250279755240846, 0.002332864203984379, 0.0024179243292001594, 0.0025055106365244446, 0.0025956736960156485, 0.002688464097222737, 0.0027839324026087842, 0.002882129099335756, 0.0029831045494195445, 0.0030869089382672345, 0.0031935922216116395, 0.0033032040708613304, 0.0034157938168875796, 0.003531410392272925, 0.0036501022720494903, 0.003771917412958515, 0.00389690319126617, 0.004025106339174149, 0.004156572879867184, 0.0042913480612432504, 0.0044294762883758535, 0.0045710010547615485, 0.0047159648724094515, 0.0048644092008333474, 0.005016374375010626, 0.005171899532376079, 0.005331022538922282, 0.0054937799144820065, 0.005660206757271772, 0.0058303366677793156, 0.006004201672081349, 0.006181832144681555, 0.006363256730962206, 0.006548502269346309, 0.006737593713270448, 0.006930554053071794, 0.007127404237895912, 0.007328163097735043, 0.007532847265709499, 0.007741471100707588, 0.00795404661050222, 0.008170583375464821, 0.008391088472999627, 0.00861556640282358, 0.008844019013219176, 0.009076445428389394, 0.009312841977045601, 0.00955320212236071, 0.009797516393421237, 0.010045772318312865, 0.010297954358975046, 0.01055404384796068, 0.010814018927237367, 0.01107785448916678, 0.011345522119798598, 0.011616990044615057, 0.011892223076861535, 0.012171182568597654, 0.012453826364602145, 0.012740108759263402, 0.013029980456585726, 0.013323388533439338, 0.013620276406179943, 0.013920583800760935, 0.014224246726458544, 0.014531197453326976, 0.014841364493497175, 0.015154672586429097, 0.015471042688223293, 0.01579039196509332, 0.01611263379109591, 0.016437677750210905, 0.01676542964285788, 0.017095791496930846, 0.0174286615834269, 0.017763934436738633, 0.018101500879673965, 0.018441248053260664, 0.018783059451386155, 0.01912681496031632, 0.019472390903129907, 0.019819660089097985, 0.020168491868030162, 0.020518752189601946, 0.020870303667669513, 0.02122300564957043, 0.021576714290400496, 0.02193128263224901, 0.022286560688365965, 0.022642395532226727, 0.022998631391450846, 0.02335510974652332, 0.023711669434257975, 0.02406814675593389, 0.024424375590027303, 0.02478018750945269, 0.025135411903218143, 0.025489876102391618, 0.025843405510266128, 0.026195823736603504, 0.02654695273582813, 0.026896612949033748, 0.02724462344965848, 0.02759080209267526, 0.027934965667137254, 0.028276930051910093, 0.02861651037441575, 0.02895352117220561, 0.029287776557173486, 0.029619090382212766, 0.029947276410115728, 0.030272148484506885, 0.030593520702596688, 0.03091120758953652, 0.031225024274151008, 0.031534786665818944, 0.031840311632269885, 0.032141417178059746, 0.03243792262348501, 0.0327296487836923, 0.03301641814773737, 0.03329805505734528, 0.033574385885121835, 0.033845239211964966, 0.03411044600342398, 0.034369839784753865, 0.03462325681441241, 0.034870536255747764, 0.03511152034662558, 0.035346054566745985, 0.03557398780240272, 0.03579517250843906, 0.036009464867158024, 0.03621672494394776, 0.03641681683938664, 0.03660960883759693, 0.03679497355062062, 0.03697278805859595, 0.037142934045519, 0.0373052979303805, 0.03745977099347446, 0.037606249497682154, 0.03774463480454201, 0.03787483348492375, 0.03799675742413297, 0.03811032392128052, 0.03821545578276005, 0.03831208140968567, 0.038400134879151185, 0.03847955601918161, 0.03855029047725805, 0.038612289782306276, 0.03866551140005032, 0.038709918781642524, 0.038745481405492124, 0.0387721748122255, 0.03878998063272192, 0.038798886609179815] + [0.0388] * 2640 + [0.038798886609179815, 0.03878998063272192, 0.0387721748122255, 0.038745481405492124, 0.038709918781642524, 0.03866551140005032, 0.038612289782306276, 0.03855029047725805, 0.03847955601918161, 0.038400134879151185, 0.03831208140968567, 0.03821545578276005, 0.03811032392128052, 0.03799675742413297, 0.03787483348492375, 0.03774463480454201, 0.037606249497682154, 0.03745977099347446, 0.0373052979303805, 0.037142934045519, 0.03697278805859595, 0.03679497355062062, 0.03660960883759693, 0.03641681683938664, 0.03621672494394776, 0.036009464867158024, 0.03579517250843906, 0.03557398780240272, 0.035346054566745985, 0.03511152034662558, 0.034870536255747764, 0.03462325681441241, 0.034369839784753865, 0.03411044600342398, 0.033845239211964966, 0.033574385885121835, 0.03329805505734528, 0.03301641814773737, 0.0327296487836923, 0.03243792262348501, 0.032141417178059746, 0.031840311632269885, 0.031534786665818944, 0.031225024274151008, 0.03091120758953652, 0.030593520702596688, 0.030272148484506885, 0.029947276410115728, 0.029619090382212766, 0.029287776557173486, 0.02895352117220561, 0.02861651037441575, 0.028276930051910093, 0.027934965667137254, 0.02759080209267526, 0.02724462344965848, 0.026896612949033748, 0.02654695273582813, 0.026195823736603504, 0.025843405510266128, 0.025489876102391618, 0.025135411903218143, 0.02478018750945269, 0.024424375590027303, 0.02406814675593389, 0.023711669434257975, 0.02335510974652332, 0.022998631391450846, 0.022642395532226727, 0.022286560688365965, 0.02193128263224901, 0.021576714290400496, 0.02122300564957043, 0.020870303667669513, 0.020518752189601946, 0.020168491868030162, 0.019819660089097985, 0.019472390903129907, 0.01912681496031632, 0.018783059451386155, 0.018441248053260664, 0.018101500879673965, 0.017763934436738633, 0.0174286615834269, 0.017095791496930846, 0.01676542964285788, 0.016437677750210905, 0.01611263379109591, 0.01579039196509332, 0.015471042688223293, 0.015154672586429097, 0.014841364493497175, 0.014531197453326976, 0.014224246726458544, 0.013920583800760935, 0.013620276406179943, 0.013323388533439338, 0.013029980456585726, 0.012740108759263402, 0.012453826364602145, 0.012171182568597654, 0.011892223076861535, 0.011616990044615057, 0.011345522119798598, 0.01107785448916678, 0.010814018927237367, 0.01055404384796068, 0.010297954358975046, 0.010045772318312865, 0.009797516393421237, 0.00955320212236071, 0.009312841977045601, 0.009076445428389394, 0.008844019013219176, 0.00861556640282358, 0.008391088472999627, 0.008170583375464821, 0.00795404661050222, 0.007741471100707588, 0.007532847265709499, 0.007328163097735043, 0.007127404237895912, 0.006930554053071794, 0.006737593713270448, 0.006548502269346309, 0.006363256730962206, 0.006181832144681555, 0.006004201672081349, 0.0058303366677793156, 0.005660206757271772, 0.0054937799144820065, 0.005331022538922282, 0.005171899532376079, 0.005016374375010626, 0.0048644092008333474, 0.0047159648724094515, 0.0045710010547615485, 0.0044294762883758535, 0.0042913480612432504, 0.004156572879867184, 0.004025106339174149, 0.00389690319126617, 0.003771917412958515, 0.0036501022720494903, 0.003531410392272925, 0.0034157938168875796, 0.0033032040708613304, 0.0031935922216116395, 0.0030869089382672345, 0.0029831045494195445, 0.002882129099335756, 0.0027839324026087842, 0.002688464097222737, 0.0025956736960156485, 0.0025055106365244446, 0.0024179243292001594, 0.002332864203984379, 0.002250279755240846, 0.0021701205850388917, 0.002092336444788167, 0.002016877275226666, 0.0019436932447666644, 0.001872734786205532, 0.0018039526318107697, 0.0017372978467908137, 0.001672721861165288, 0.0016101765000504122, 0.001549614012377179, 0.0014909870980617508, 0.0014342489336492182, 0.0013793531964535074, 0.0013262540872176981, 0.0012749063513204572, 0.0012252652985555777, 0.0011772868215128417, 0.0011309274125895375, 0.0010861441796629664, 0.0010428948604552203, 0.001001137835622318, 0.0009608321406005604, 0.0009219374762435797, 0.000884414218284159, 0.0008482234256553598, 0.0008133268477059036, 0.0007796869303450725, 0.0007472668211526478, 0.0007160303734895581, 0.0006859421496450338, 0.0006569674230560738, 0.0006290721796350132, 0.0006022231182408695, 0.000576387650330002, 0.000551533898821395, 0.0005276306962116111, 0.0005046475819741386, 0.00048255479927748914, 0.00046132329105599503, 0.00044092469546678196, 0.0004213313407659066, 0.00040251623963611874],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001754498242547914, 0.004769220690781325, 0.01160077380536972, 0.025250591495837534, 0.04918143661320847, 0.08571876843888207, 0.13368900544319495, 0.18657803709392473, 0.23300777060530184, 0.2603906268164547] + [0.2640323948139477] * 32 + [0.2603906268164547, 0.23300777060530184, 0.18657803709392473, 0.13368900544319495, 0.08571876843888207, 0.04918143661320847, 0.025250591495837534, 0.01160077380536972, 0.004769220690781325, 0.001754498242547914],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008006671084744846, -0.001947340025125666, -0.004179493628177615, -0.00788424947310757, -0.01299389476587147, -0.018529507730236556, -0.02247704328734932, -0.022406600636444715, -0.016789474717797813, -0.006254186050432826] + [0.0] * 32 + [0.006254186050432826, 0.016789474717797813, 0.022406600636444715, 0.02247704328734932, 0.018529507730236556, 0.01299389476587147, 0.00788424947310757, 0.004179493628177615, 0.001947340025125666, 0.0008006671084744846],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008360056467367242, 0.0022724989580135894, 0.0055276843103134144, 0.01203172312290646, 0.023434596699029586, 0.04084436946608459, 0.06370183836423844, 0.08890307712195691, 0.11102650731452524, 0.12407423905978995] + [0.12580951501286694] * 32 + [0.12407423905978995, 0.11102650731452524, 0.08890307712195691, 0.06370183836423844, 0.04084436946608459, 0.023434596699029586, 0.01203172312290646, 0.0055276843103134144, 0.0022724989580135894, 0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000381512051484859, -0.0009278933530063265, -0.001991498303573379, -0.00375678750765062, -0.006191496311558518, -0.00882917561161735, -0.01071014758206955, -0.010676582171458575, -0.008000062541777738, -0.002980074147188042] + [0.0] * 32 + [0.002980074147188042, 0.008000062541777738, 0.010676582171458575, 0.01071014758206955, 0.00882917561161735, 0.006191496311558518, 0.00375678750765062, 0.001991498303573379, 0.0009278933530063265, 0.000381512051484859],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008360056467367242, -0.0022724989580135894, -0.0055276843103134144, -0.01203172312290646, -0.023434596699029586, -0.04084436946608459, -0.06370183836423844, -0.08890307712195691, -0.11102650731452524, -0.12407423905978995] + [-0.12580951501286694] * 32 + [-0.12407423905978995, -0.11102650731452524, -0.08890307712195691, -0.06370183836423844, -0.04084436946608459, -0.023434596699029586, -0.01203172312290646, -0.0055276843103134144, -0.0022724989580135894, -0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000381512051484859, 0.0009278933530063265, 0.001991498303573379, 0.00375678750765062, 0.006191496311558518, 0.00882917561161735, 0.01071014758206955, 0.010676582171458575, 0.008000062541777738, 0.002980074147188042] + [0.0] * 32 + [-0.002980074147188042, -0.008000062541777738, -0.010676582171458575, -0.01071014758206955, -0.00882917561161735, -0.006191496311558518, -0.00375678750765062, -0.001991498303573379, -0.0009278933530063265, -0.000381512051484859],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008006671084744846, 0.001947340025125666, 0.004179493628177615, 0.00788424947310757, 0.01299389476587147, 0.018529507730236556, 0.02247704328734932, 0.022406600636444715, 0.016789474717797813, 0.006254186050432826] + [0.0] * 32 + [-0.006254186050432826, -0.016789474717797813, -0.022406600636444715, -0.02247704328734932, -0.018529507730236556, -0.01299389476587147, -0.00788424947310757, -0.004179493628177615, -0.001947340025125666, -0.0008006671084744846],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001754498242547914, 0.004769220690781325, 0.01160077380536972, 0.025250591495837534, 0.04918143661320847, 0.08571876843888207, 0.13368900544319495, 0.18657803709392473, 0.23300777060530184, 0.2603906268164547] + [0.2640323948139477] * 32 + [0.2603906268164547, 0.23300777060530184, 0.18657803709392473, 0.13368900544319495, 0.08571876843888207, 0.04918143661320847, 0.025250591495837534, 0.01160077380536972, 0.004769220690781325, 0.001754498242547914],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.000381512051484859, 0.0009278933530063265, 0.001991498303573379, 0.00375678750765062, 0.006191496311558518, 0.00882917561161735, 0.01071014758206955, 0.010676582171458575, 0.008000062541777738, 0.002980074147188042] + [0.0] * 32 + [-0.002980074147188042, -0.008000062541777738, -0.010676582171458575, -0.01071014758206955, -0.00882917561161735, -0.006191496311558518, -0.00375678750765062, -0.001991498303573379, -0.0009278933530063265, -0.000381512051484859],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008360056467367242, 0.0022724989580135894, 0.0055276843103134144, 0.01203172312290646, 0.023434596699029586, 0.04084436946608459, 0.06370183836423844, 0.08890307712195691, 0.11102650731452524, 0.12407423905978995] + [0.12580951501286694] * 32 + [0.12407423905978995, 0.11102650731452524, 0.08890307712195691, 0.06370183836423844, 0.04084436946608459, 0.023434596699029586, 0.01203172312290646, 0.0055276843103134144, 0.0022724989580135894, 0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 32 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 32 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.000381512051484859, -0.0009278933530063265, -0.001991498303573379, -0.00375678750765062, -0.006191496311558518, -0.00882917561161735, -0.01071014758206955, -0.010676582171458575, -0.008000062541777738, -0.002980074147188042] + [0.0] * 32 + [0.002980074147188042, 0.008000062541777738, 0.010676582171458575, 0.01071014758206955, 0.00882917561161735, 0.006191496311558518, 0.00375678750765062, 0.001991498303573379, 0.0009278933530063265, 0.000381512051484859],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008360056467367242, -0.0022724989580135894, -0.0055276843103134144, -0.01203172312290646, -0.023434596699029586, -0.04084436946608459, -0.06370183836423844, -0.08890307712195691, -0.11102650731452524, -0.12407423905978995] + [-0.12580951501286694] * 32 + [-0.12407423905978995, -0.11102650731452524, -0.08890307712195691, -0.06370183836423844, -0.04084436946608459, -0.023434596699029586, -0.01203172312290646, -0.0055276843103134144, -0.0022724989580135894, -0.0008360056467367242],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0011425919097940382, 0.0031058868257374506, 0.007554838173059075, 0.016444086896752877, 0.03202870782286673, 0.055823123079076255, 0.08706305446392269, 0.12150628057579745, 0.15174298107368572, 0.16957567489757952] + [0.17194732426739567] * 32 + [0.16957567489757952, 0.15174298107368572, 0.12150628057579745, 0.08706305446392269, 0.055823123079076255, 0.03202870782286673, 0.016444086896752877, 0.007554838173059075, 0.0031058868257374506, 0.0011425919097940382],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005687802792877164, 0.00154610509757366, 0.00376078539434138, 0.00818583805608474, 0.01594383543639708, 0.02778865425482748, 0.04333983814269958, 0.06048561661317156, 0.07553739389822868, 0.08441447808433584] + [0.08559508104447734] * 32 + [0.08441447808433584, 0.07553739389822868, 0.06048561661317156, 0.04333983814269958, 0.02778865425482748, 0.01594383543639708, 0.00818583805608474, 0.00376078539434138, 0.00154610509757366, 0.0005687802792877164],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005687802792877164, -0.00154610509757366, -0.00376078539434138, -0.00818583805608474, -0.01594383543639708, -0.02778865425482748, -0.04333983814269958, -0.06048561661317156, -0.07553739389822868, -0.08441447808433584] + [-0.08559508104447734] * 32 + [-0.08441447808433584, -0.07553739389822868, -0.06048561661317156, -0.04333983814269958, -0.02778865425482748, -0.01594383543639708, -0.00818583805608474, -0.00376078539434138, -0.00154610509757366, -0.0005687802792877164],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001142759621501325, 0.0031063427134237877, 0.007555947085871618, 0.016446500589572324, 0.03203340905453581, 0.055831316898056954, 0.08707583373654014, 0.1215241154874459, 0.15176525418292666, 0.1696005655218764] + [0.17197256300667702] * 32 + [0.1696005655218764, 0.15176525418292666, 0.1215241154874459, 0.08707583373654014, 0.055831316898056954, 0.03203340905453581, 0.016446500589572324, 0.007555947085871618, 0.0031063427134237877, 0.001142759621501325],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005691157027022902, 0.0015470168729463355, 0.003763003219966468, 0.008190665441723633, 0.015953237899735254, 0.0278050418927889, 0.04336539668793448, 0.06052128643646852, 0.07558194011671057, 0.0844642593329297] + [0.08564555852304008] * 32 + [0.0844642593329297, 0.07558194011671057, 0.06052128643646852, 0.04336539668793448, 0.0278050418927889, 0.015953237899735254, 0.008190665441723633, 0.003763003219966468, 0.0015470168729463355, 0.0005691157027022902],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005691157027022902, -0.0015470168729463355, -0.003763003219966468, -0.008190665441723633, -0.015953237899735254, -0.0278050418927889, -0.04336539668793448, -0.06052128643646852, -0.07558194011671057, -0.0844642593329297] + [-0.08564555852304008] * 32 + [-0.0844642593329297, -0.07558194011671057, -0.06052128643646852, -0.04336539668793448, -0.0278050418927889, -0.015953237899735254, -0.008190665441723633, -0.003763003219966468, -0.0015470168729463355, -0.0005691157027022902],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0029047563685080727, 0.0030405354488261295, 0.003181930792028323, 0.0033291371519504794, 0.0034823542215901273, 0.0036417866740401745, 0.0038076441994652345, 0.003980141537886355, 0.004159498507536096, 0.004345940028542356, 0.004539696141695971, 0.004741002022054141, 0.004950097987129109, 0.005167229499409181, 0.005392647162957252, 0.005626606713830419, 0.00586936900406322, 0.006121199978956203, 0.006382370647411455, 0.006653157045056759, 0.00693384018990095, 0.007224706030264148, 0.007526045384728393, 0.007838153873856458, 0.008161331843429652, 0.00849588427895865, 0.008842120711225818, 0.009200355112621855, 0.009570905784045243, 0.00995409523213871, 0.01035025003664384, 0.010759700707662117, 0.011182781532618816, 0.011619830412734932, 0.012071188688821665, 0.012537200956222365, 0.013018214868737511, 0.013514580931380126, 0.014026652281821287, 0.014554784460398616, 0.015099335168574398, 0.015660664015744577, 0.01623913225431538, 0.01683510250298005, 0.017448938458145477, 0.01808100459347537, 0.018731665847535606, 0.019401287299545524, 0.020090233833259263, 0.020798869789020916, 0.021527558604058566, 0.02227666244110375, 0.02304654180544482, 0.02383755515054568, 0.024650058472384592, 0.02548440489269121, 0.026340944231284975, 0.027220022567741857, 0.028121981792642463, 0.029047159148679422, 0.02999588676192813, 0.03096849116361108, 0.03196529280271234, 0.032986605549825604, 0.03403273619264552, 0.03510398392353962, 0.03620063981966431, 0.037322986316116025, 0.038471296672635026, 0.039645834434406224, 0.04084685288752825, 0.04207459450974763, 0.043329290417081896, 0.044611159806980286, 0.04592040939869633, 0.04725723287157129, 0.04862181030195168, 0.05001430759948717, 0.051434875943578734, 0.05288365122076834, 0.05436075346388297, 0.05586628629376609, 0.057400336364448995, 0.05896297281263273, 0.06055424671236844, 0.06217419053584025, 0.0638228176211693, 0.06550012164817087, 0.06720607612300948, 0.06894063387270614, 0.07070372655046253, 0.07249526415277324, 0.07431513454930445, 0.07616320302652035, 0.07803931184604285, 0.07994327981872933, 0.0818749018954538, 0.08383394877557256, 0.0858201665340523, 0.08783327626823048, 0.0898729737651701, 0.09193892919056063, 0.09403078680010317, 0.0961481646743045, 0.0982906544775872, 0.10045782124260468, 0.10264920318062866, 0.10486431151885445, 0.10710263036544351, 0.10936361660309657, 0.11164669981192066, 0.1139512822223229, 0.11627673869863024, 0.11862241675409929, 0.12098763659794344, 0.12337169121496486, 0.12577384647833845, 0.12819334129605198, 0.13062938779146158, 0.13308117151837592, 0.1355478517110341, 0.138028561569293, 0.14052240857928797, 0.14302847486977924, 0.14554581760434135, 0.14807346940949856, 0.15061043883885214, 0.15315571087318863, 0.15570824745649842, 0.15826698806777634, 0.16083085032841415, 0.16339873064493513, 0.16596950488675866, 0.16854202909862187, 0.1711151402472225, 0.17368765700158476, 0.17625838054658877, 0.17882609542904002, 0.1813895704355948, 0.18394755950179517, 0.186498802651405, 0.18904202696517988, 0.19157594757814111, 0.19409926870436722, 0.19661068468825704, 0.19910888108116165, 0.2015925357422276, 0.20406031996223775, 0.20651089960918578, 0.20894293629426727, 0.21135508855692203, 0.21374601306751478, 0.21611436584619595, 0.21845880349644142, 0.22077798445172866, 0.22307057023376867, 0.22533522672067735, 0.22757062542343565, 0.2297754447689579, 0.23194837138806, 0.2340881014065928, 0.23619334173798565, 0.2382628113754243, 0.24029524268187313, 0.24228938267613692, 0.24424399431314922, 0.24615785775666785, 0.24802977164255363, 0.24985855433081117, 0.2516430451445715, 0.2533821055942052, 0.2550746205847648, 0.2567194996049681, 0.25831567789595195, 0.25986211759804756, 0.26135780887384974, 0.2628017710058829, 0.2641930534671943, 0.2655307369632416, 0.2668139344434759, 0.2680417920810649, 0.2692134902192407, 0.27032824428280533, 0.2713853056533763, 0.27238396250700414, 0.2733235406128518, 0.2742034040916812, 0.27502295613295213, 0.27578163966940233, 0.2764789380080409, 0.27711437541655487, 0.2776875176641972, 0.2781979725162952, 0.2786453901815916, 0.27902946371170334, 0.27934992935205943, 0.27960656684375756, 0.27979919967585415, 0.2799276952876839, 0.2799919652208852] + [0.27999999999999997] * 9600 + [0.2799919652208852, 0.2799276952876839, 0.27979919967585415, 0.27960656684375756, 0.27934992935205943, 0.27902946371170334, 0.2786453901815916, 0.2781979725162952, 0.2776875176641972, 0.27711437541655487, 0.2764789380080409, 0.27578163966940233, 0.27502295613295213, 0.2742034040916812, 0.2733235406128518, 0.27238396250700414, 0.2713853056533763, 0.27032824428280533, 0.2692134902192407, 0.2680417920810649, 0.2668139344434759, 0.2655307369632416, 0.2641930534671943, 0.2628017710058829, 0.26135780887384974, 0.25986211759804756, 0.25831567789595195, 0.2567194996049681, 0.2550746205847648, 0.2533821055942052, 0.2516430451445715, 0.24985855433081117, 0.24802977164255363, 0.24615785775666785, 0.24424399431314922, 0.24228938267613692, 0.24029524268187313, 0.2382628113754243, 0.23619334173798565, 0.2340881014065928, 0.23194837138806, 0.2297754447689579, 0.22757062542343565, 0.22533522672067735, 0.22307057023376867, 0.22077798445172866, 0.21845880349644142, 0.21611436584619595, 0.21374601306751478, 0.21135508855692203, 0.20894293629426727, 0.20651089960918578, 0.20406031996223775, 0.2015925357422276, 0.19910888108116165, 0.19661068468825704, 0.19409926870436722, 0.19157594757814111, 0.18904202696517988, 0.186498802651405, 0.18394755950179517, 0.1813895704355948, 0.17882609542904002, 0.17625838054658877, 0.17368765700158476, 0.1711151402472225, 0.16854202909862187, 0.16596950488675866, 0.16339873064493513, 0.16083085032841415, 0.15826698806777634, 0.15570824745649842, 0.15315571087318863, 0.15061043883885214, 0.14807346940949856, 0.14554581760434135, 0.14302847486977924, 0.14052240857928797, 0.138028561569293, 0.1355478517110341, 0.13308117151837592, 0.13062938779146158, 0.12819334129605198, 0.12577384647833845, 0.12337169121496486, 0.12098763659794344, 0.11862241675409929, 0.11627673869863024, 0.1139512822223229, 0.11164669981192066, 0.10936361660309657, 0.10710263036544351, 0.10486431151885445, 0.10264920318062866, 0.10045782124260468, 0.0982906544775872, 0.0961481646743045, 0.09403078680010317, 0.09193892919056063, 0.0898729737651701, 0.08783327626823048, 0.0858201665340523, 0.08383394877557256, 0.0818749018954538, 0.07994327981872933, 0.07803931184604285, 0.07616320302652035, 0.07431513454930445, 0.07249526415277324, 0.07070372655046253, 0.06894063387270614, 0.06720607612300948, 0.06550012164817087, 0.0638228176211693, 0.06217419053584025, 0.06055424671236844, 0.05896297281263273, 0.057400336364448995, 0.05586628629376609, 0.05436075346388297, 0.05288365122076834, 0.051434875943578734, 0.05001430759948717, 0.04862181030195168, 0.04725723287157129, 0.04592040939869633, 0.044611159806980286, 0.043329290417081896, 0.04207459450974763, 0.04084685288752825, 0.039645834434406224, 0.038471296672635026, 0.037322986316116025, 0.03620063981966431, 0.03510398392353962, 0.03403273619264552, 0.032986605549825604, 0.03196529280271234, 0.03096849116361108, 0.02999588676192813, 0.029047159148679422, 0.028121981792642463, 0.027220022567741857, 0.026340944231284975, 0.02548440489269121, 0.024650058472384592, 0.02383755515054568, 0.02304654180544482, 0.02227666244110375, 0.021527558604058566, 0.020798869789020916, 0.020090233833259263, 0.019401287299545524, 0.018731665847535606, 0.01808100459347537, 0.017448938458145477, 0.01683510250298005, 0.01623913225431538, 0.015660664015744577, 0.015099335168574398, 0.014554784460398616, 0.014026652281821287, 0.013514580931380126, 0.013018214868737511, 0.012537200956222365, 0.012071188688821665, 0.011619830412734932, 0.011182781532618816, 0.010759700707662117, 0.01035025003664384, 0.00995409523213871, 0.009570905784045243, 0.009200355112621855, 0.008842120711225818, 0.00849588427895865, 0.008161331843429652, 0.007838153873856458, 0.007526045384728393, 0.007224706030264148, 0.00693384018990095, 0.006653157045056759, 0.006382370647411455, 0.006121199978956203, 0.00586936900406322, 0.005626606713830419, 0.005392647162957252, 0.005167229499409181, 0.004950097987129109, 0.004741002022054141, 0.004539696141695971, 0.004345940028542356, 0.004159498507536096, 0.003980141537886355, 0.0038076441994652345, 0.0036417866740401745, 0.0034823542215901273, 0.0033291371519504794, 0.003181930792028323, 0.0030405354488261295, 0.0029047563685080727],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0011425919097940382, 0.0031058868257374506, 0.007554838173059075, 0.016444086896752877, 0.03202870782286673, 0.055823123079076255, 0.08706305446392269, 0.12150628057579745, 0.15174298107368572, 0.16957567489757952] + [0.17194732426739567] * 32 + [0.16957567489757952, 0.15174298107368572, 0.12150628057579745, 0.08706305446392269, 0.055823123079076255, 0.03202870782286673, 0.016444086896752877, 0.007554838173059075, 0.0031058868257374506, 0.0011425919097940382],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0006442181330182332, -0.0015668331345949302, -0.0033628277640082283, -0.006343680690833834, -0.010454910084484717, -0.01490887379957899, -0.018085067700526924, -0.01802838942241321, -0.013508840244061574, -0.005032128856442101] + [0.0] * 32 + [0.005032128856442101, 0.013508840244061574, 0.01802838942241321, 0.018085067700526924, 0.01490887379957899, 0.010454910084484717, 0.006343680690833834, 0.0033628277640082283, 0.0015668331345949302, 0.0006442181330182332],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005687802792877164, 0.00154610509757366, 0.00376078539434138, 0.00818583805608474, 0.01594383543639708, 0.02778865425482748, 0.04333983814269958, 0.06048561661317156, 0.07553739389822868, 0.08441447808433584] + [0.08559508104447734] * 32 + [0.08441447808433584, 0.07553739389822868, 0.06048561661317156, 0.04333983814269958, 0.02778865425482748, 0.01594383543639708, 0.00818583805608474, 0.00376078539434138, 0.00154610509757366, 0.0005687802792877164],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00032069067396632616, -0.0007799668282727434, -0.0016740098528737779, -0.0031578732915192465, -0.005204436183040273, -0.007421611627828192, -0.009002715466011987, -0.008974501117057884, -0.006724677341935242, -0.0025049850535829947] + [0.0] * 32 + [0.0025049850535829947, 0.006724677341935242, 0.008974501117057884, 0.009002715466011987, 0.007421611627828192, 0.005204436183040273, 0.0031578732915192465, 0.0016740098528737779, 0.0007799668282727434, 0.00032069067396632616],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005687802792877164, -0.00154610509757366, -0.00376078539434138, -0.00818583805608474, -0.01594383543639708, -0.02778865425482748, -0.04333983814269958, -0.06048561661317156, -0.07553739389822868, -0.08441447808433584] + [-0.08559508104447734] * 32 + [-0.08441447808433584, -0.07553739389822868, -0.06048561661317156, -0.04333983814269958, -0.02778865425482748, -0.01594383543639708, -0.00818583805608474, -0.00376078539434138, -0.00154610509757366, -0.0005687802792877164],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00032069067396632616, 0.0007799668282727434, 0.0016740098528737779, 0.0031578732915192465, 0.005204436183040273, 0.007421611627828192, 0.009002715466011987, 0.008974501117057884, 0.006724677341935242, 0.0025049850535829947] + [0.0] * 32 + [-0.0025049850535829947, -0.006724677341935242, -0.008974501117057884, -0.009002715466011987, -0.007421611627828192, -0.005204436183040273, -0.0031578732915192465, -0.0016740098528737779, -0.0007799668282727434, -0.00032069067396632616],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006443126925210857, 0.001567063117196578, 0.00336332136595025, 0.006344611827760344, 0.010456444675098188, 0.014911062151043075, 0.018087722259477017, 0.01803103566202312, 0.013510823096067943, 0.0050328674814179705] + [0.0] * 32 + [-0.0050328674814179705, -0.013510823096067943, -0.01803103566202312, -0.018087722259477017, -0.014911062151043075, -0.010456444675098188, -0.006344611827760344, -0.00336332136595025, -0.001567063117196578, -0.0006443126925210857],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001142759621501325, 0.0031063427134237877, 0.007555947085871618, 0.016446500589572324, 0.03203340905453581, 0.055831316898056954, 0.08707583373654014, 0.1215241154874459, 0.15176525418292666, 0.1696005655218764] + [0.17197256300667702] * 32 + [0.1696005655218764, 0.15176525418292666, 0.1215241154874459, 0.08707583373654014, 0.055831316898056954, 0.03203340905453581, 0.016446500589572324, 0.007555947085871618, 0.0031063427134237877, 0.001142759621501325],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00032087979297203156, 0.0007804267934760396, 0.001674997056757823, 0.0031597355653722697, 0.005207505364267218, 0.007425988330756366, 0.009008024583912186, 0.008979793596277713, 0.006728643045947982, 0.002506462303534735] + [0.0] * 32 + [-0.002506462303534735, -0.006728643045947982, -0.008979793596277713, -0.009008024583912186, -0.007425988330756366, -0.005207505364267218, -0.0031597355653722697, -0.001674997056757823, -0.0007804267934760396, -0.00032087979297203156],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005691157027022902, 0.0015470168729463355, 0.003763003219966468, 0.008190665441723633, 0.015953237899735254, 0.0278050418927889, 0.04336539668793448, 0.06052128643646852, 0.07558194011671057, 0.0844642593329297] + [0.08564555852304008] * 32 + [0.0844642593329297, 0.07558194011671057, 0.06052128643646852, 0.04336539668793448, 0.0278050418927889, 0.015953237899735254, 0.008190665441723633, 0.003763003219966468, 0.0015470168729463355, 0.0005691157027022902],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00034956037273596835, 0.0008501821766146529, 0.001824710088687164, 0.0034421561163089443, 0.0056729577743041834, 0.008089731125756503, 0.009813171474595064, 0.009782417171032325, 0.0073300563720878125, 0.002730492590253645] + [0.0] * 32 + [-0.002730492590253645, -0.0073300563720878125, -0.009782417171032325, -0.009813171474595064, -0.008089731125756503, -0.0056729577743041834, -0.0034421561163089443, -0.001824710088687164, -0.0008501821766146529, -0.00034956037273596835],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00034956037273596835, -0.0008501821766146529, -0.001824710088687164, -0.0034421561163089443, -0.0056729577743041834, -0.008089731125756503, -0.009813171474595064, -0.009782417171032325, -0.0073300563720878125, -0.002730492590253645] + [0.0] * 32 + [0.002730492590253645, 0.0073300563720878125, 0.009782417171032325, 0.009813171474595064, 0.008089731125756503, 0.0056729577743041834, 0.0034421561163089443, 0.001824710088687164, 0.0008501821766146529, 0.00034956037273596835],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00032087979297203156, -0.0007804267934760396, -0.001674997056757823, -0.0031597355653722697, -0.005207505364267218, -0.007425988330756366, -0.009008024583912186, -0.008979793596277713, -0.006728643045947982, -0.002506462303534735] + [0.0] * 32 + [0.002506462303534735, 0.006728643045947982, 0.008979793596277713, 0.009008024583912186, 0.007425988330756366, 0.005207505364267218, 0.0031597355653722697, 0.001674997056757823, 0.0007804267934760396, 0.00032087979297203156],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005691157027022902, -0.0015470168729463355, -0.003763003219966468, -0.008190665441723633, -0.015953237899735254, -0.0278050418927889, -0.04336539668793448, -0.06052128643646852, -0.07558194011671057, -0.0844642593329297] + [-0.08564555852304008] * 32 + [-0.0844642593329297, -0.07558194011671057, -0.06052128643646852, -0.04336539668793448, -0.0278050418927889, -0.015953237899735254, -0.008190665441723633, -0.003763003219966468, -0.0015470168729463355, -0.0005691157027022902],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 84 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005297769779599651, 0.0014400831323245211, 0.0035028948673558203, 0.007624505815941894, 0.014850509523929386, 0.025883086683548395, 0.04036787018225523, 0.05633790120061767, 0.0703575241963199, 0.07862587491885455] + [0.07972551970467169] * 84 + [0.07862587491885455, 0.0703575241963199, 0.05633790120061767, 0.04036787018225523, 0.025883086683548395, 0.014850509523929386, 0.007624505815941894, 0.0035028948673558203, 0.0014400831323245211, 0.0005297769779599651],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002658773462345805, 0.000722729558868374, 0.0017579857755571989, 0.0038264844586092008, 0.007452974037599812, 0.012989855516714248, 0.020259283894384607, 0.028274108326349662, 0.035310088205392824, 0.03945969688848365] + [0.040011571827594065] * 84 + [0.03945969688848365, 0.035310088205392824, 0.028274108326349662, 0.020259283894384607, 0.012989855516714248, 0.007452974037599812, 0.0038264844586092008, 0.0017579857755571989, 0.000722729558868374, 0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002658773462345805, -0.000722729558868374, -0.0017579857755571989, -0.0038264844586092008, -0.007452974037599812, -0.012989855516714248, -0.020259283894384607, -0.028274108326349662, -0.035310088205392824, -0.03945969688848365] + [-0.040011571827594065] * 84 + [-0.03945969688848365, -0.035310088205392824, -0.028274108326349662, -0.020259283894384607, -0.012989855516714248, -0.007452974037599812, -0.0038264844586092008, -0.0017579857755571989, -0.000722729558868374, -0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005304889551832756, 0.0014420184870729228, 0.003507602473508908, 0.007634752532401437, 0.014870467402386671, 0.02591787144950523, 0.04042212132060027, 0.056413614763367065, 0.07045207899352757, 0.07873154170777515] + [0.07983266432685761] * 84 + [0.07873154170777515, 0.07045207899352757, 0.056413614763367065, 0.04042212132060027, 0.02591787144950523, 0.014870467402386671, 0.007634752532401437, 0.003507602473508908, 0.0014420184870729228, 0.0005304889551832756],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002658773462345805, 0.000722729558868374, 0.0017579857755571989, 0.0038264844586092008, 0.007452974037599812, 0.012989855516714248, 0.020259283894384607, 0.028274108326349662, 0.035310088205392824, 0.03945969688848365] + [0.040011571827594065] * 84 + [0.03945969688848365, 0.035310088205392824, 0.028274108326349662, 0.020259283894384607, 0.012989855516714248, 0.007452974037599812, 0.0038264844586092008, 0.0017579857755571989, 0.000722729558868374, 0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002658773462345805, -0.000722729558868374, -0.0017579857755571989, -0.0038264844586092008, -0.007452974037599812, -0.012989855516714248, -0.020259283894384607, -0.028274108326349662, -0.035310088205392824, -0.03945969688848365] + [-0.040011571827594065] * 84 + [-0.03945969688848365, -0.035310088205392824, -0.028274108326349662, -0.020259283894384607, -0.012989855516714248, -0.007452974037599812, -0.0038264844586092008, -0.0017579857755571989, -0.000722729558868374, -0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_ro_wf": {
            "type": "arbitrary",
            "samples": [0.00038176797986106103, 0.00039961323041714847, 0.00041819661838086536, 0.00043754373997063444, 0.0004576808405518453, 0.0004786348200167087, 0.0005004332376440023, 0.0005231043164079211, 0.0005466769467047441, 0.0005711806894655669, 0.000596645778622899, 0.0006231031228985443, 0.0006505843068798259, 0.000679121591350921, 0.0007087479128458104, 0.0007394968823891409, 0.0007714027833911662, 0.0008045005686628154, 0.0008388258565169343, 0.0008744149259217456, 0.0009113047106726964, 0.0009495327925490024, 0.000989137393421446, 0.0010301573662782775, 0.0010726321851364685, 0.0011166019338059942, 0.0011621072934753932, 0.0012091895290874438, 0.0012578904744745178, 0.001308252516223945, 0.0013603185762446192, 0.0014141320930070214, 0.0014697370014299018, 0.0015271777113880197, 0.0015864990848165619, 0.0016477464113892253, 0.0017109653827483589, 0.0017762020652671022, 0.0018435028713250836, 0.0019129145290809613, 0.001984484050726921, 0.0020582586992121447, 0.0021342859534243075, 0.0022126134718202357, 0.00229328905449912, 0.0023763606037139062, 0.0024618760828189652, 0.0025498834736545546, 0.002640430732371218, 0.002733565743699892, 0.0028293362736762687, 0.002927789920830779, 0.003028974065858462, 0.003132935819786004, 0.0032397219706562608, 0.003349378928753702, 0.0034619526703974545, 0.003577488680331787, 0.0036960318927472956, 0.0038176266309692957, 0.003942316545853412, 0.004070144552931742, 0.00420115276835648, 0.004335382443691365, 0.004472873899604841, 0.00461366645852235, 0.004757798376298738, 0.00490530677297525, 0.005056227562689175, 0.005210595382807676, 0.0053684435223608565, 0.005529803849852547, 0.005694706740530764, 0.005863181003203124, 0.006035253806685803, 0.006210950605977941, 0.006390295068256507, 0.006573308998789743, 0.006760012266870349, 0.006950422731872411, 0.007144556169538905, 0.007342426198609258, 0.007544044207899011, 0.0077494192839460165, 0.007958558139339853, 0.008171465041853291, 0.008388141744496537, 0.008608587416616745, 0.008832798576166962, 0.009060769023269952, 0.009292489775203647, 0.009527949002935913, 0.009767131969337157, 0.010010020969199819, 0.010256595271194203, 0.010506831061890142, 0.010760701391973928, 0.011018176124789537, 0.01127922188733259, 0.011543802023824578, 0.011811876551993786, 0.012083402122187968, 0.012358331979442132, 0.012636615928622877, 0.012918200302768605, 0.01320302793474233, 0.013491038132311195, 0.013782166656763729, 0.014076345705172577, 0.01437350389640698, 0.014673566260995289, 0.014976454234933868, 0.015282085657534262, 0.015590374773395907, 0.015901232238586853, 0.01621456513110967, 0.016530276965724483, 0.016848267713195406, 0.017168433824020665, 0.017490668256700835, 0.017814860510593052, 0.018140896663392796, 0.01846865941327785, 0.018798028125742418, 0.019128878885142007, 0.01946108455096267, 0.01979451481882057, 0.020129036286190508, 0.020464512522854077, 0.020800804146050605, 0.021137768900305862, 0.02147526174190576, 0.021813134927973998, 0.022151238110104592, 0.0224894184324921, 0.022827520634494, 0.02316538715755167, 0.023502858256388117, 0.023839772114392463, 0.02417596496309308, 0.024511271205613232, 0.024845523543995073, 0.025178553110269977, 0.025510189601145407, 0.025840261416170927, 0.02616859579923839, 0.0264950189832642, 0.026819356337894108, 0.02714143252006442, 0.027461071627246557, 0.02777809735319547, 0.02809233314601623, 0.028403602368357185, 0.028711728459532303, 0.029016535099370053, 0.02931784637358103, 0.02961548694043188, 0.029909282198508687, 0.030199058455348756, 0.03048464309671646, 0.030765864756295058, 0.03104255348556383, 0.0313145409236272, 0.031581660466760475, 0.03184374743743514, 0.03210063925258533, 0.032352175590876345, 0.03259819855873562, 0.03283855285490662, 0.03307308593328654, 0.03330164816380983, 0.03352409299114052, 0.033740277090938665, 0.033950060523467974, 0.034153306884314824, 0.034349883451991685, 0.03453966133220176, 0.03472251559854554, 0.034898325429454605, 0.03506697424114255, 0.035228349816368534, 0.035382344428814494, 0.035528854962882994, 0.035667783028729465, 0.03579903507234912, 0.03592252248054624, 0.03603816168062096, 0.03614587423461657, 0.0362455869279786, 0.03633723185248538, 0.036420746483318646, 0.03649607375015163, 0.03656316210214166, 0.03662196556672347, 0.03667244380210958, 0.03671456214341352, 0.03674829164232243, 0.036773609100255115, 0.036790497094952745, 0.0367989440004592] + [0.0368] * 3600 + [0.0367989440004592, 0.036790497094952745, 0.036773609100255115, 0.03674829164232243, 0.03671456214341352, 0.03667244380210958, 0.03662196556672347, 0.03656316210214166, 0.03649607375015163, 0.036420746483318646, 0.03633723185248538, 0.0362455869279786, 0.03614587423461657, 0.03603816168062096, 0.03592252248054624, 0.03579903507234912, 0.035667783028729465, 0.035528854962882994, 0.035382344428814494, 0.035228349816368534, 0.03506697424114255, 0.034898325429454605, 0.03472251559854554, 0.03453966133220176, 0.034349883451991685, 0.034153306884314824, 0.033950060523467974, 0.033740277090938665, 0.03352409299114052, 0.03330164816380983, 0.03307308593328654, 0.03283855285490662, 0.03259819855873562, 0.032352175590876345, 0.03210063925258533, 0.03184374743743514, 0.031581660466760475, 0.0313145409236272, 0.03104255348556383, 0.030765864756295058, 0.03048464309671646, 0.030199058455348756, 0.029909282198508687, 0.02961548694043188, 0.02931784637358103, 0.029016535099370053, 0.028711728459532303, 0.028403602368357185, 0.02809233314601623, 0.02777809735319547, 0.027461071627246557, 0.02714143252006442, 0.026819356337894108, 0.0264950189832642, 0.02616859579923839, 0.025840261416170927, 0.025510189601145407, 0.025178553110269977, 0.024845523543995073, 0.024511271205613232, 0.02417596496309308, 0.023839772114392463, 0.023502858256388117, 0.02316538715755167, 0.022827520634494, 0.0224894184324921, 0.022151238110104592, 0.021813134927973998, 0.02147526174190576, 0.021137768900305862, 0.020800804146050605, 0.020464512522854077, 0.020129036286190508, 0.01979451481882057, 0.01946108455096267, 0.019128878885142007, 0.018798028125742418, 0.01846865941327785, 0.018140896663392796, 0.017814860510593052, 0.017490668256700835, 0.017168433824020665, 0.016848267713195406, 0.016530276965724483, 0.01621456513110967, 0.015901232238586853, 0.015590374773395907, 0.015282085657534262, 0.014976454234933868, 0.014673566260995289, 0.01437350389640698, 0.014076345705172577, 0.013782166656763729, 0.013491038132311195, 0.01320302793474233, 0.012918200302768605, 0.012636615928622877, 0.012358331979442132, 0.012083402122187968, 0.011811876551993786, 0.011543802023824578, 0.01127922188733259, 0.011018176124789537, 0.010760701391973928, 0.010506831061890142, 0.010256595271194203, 0.010010020969199819, 0.009767131969337157, 0.009527949002935913, 0.009292489775203647, 0.009060769023269952, 0.008832798576166962, 0.008608587416616745, 0.008388141744496537, 0.008171465041853291, 0.007958558139339853, 0.0077494192839460165, 0.007544044207899011, 0.007342426198609258, 0.007144556169538905, 0.006950422731872411, 0.006760012266870349, 0.006573308998789743, 0.006390295068256507, 0.006210950605977941, 0.006035253806685803, 0.005863181003203124, 0.005694706740530764, 0.005529803849852547, 0.0053684435223608565, 0.005210595382807676, 0.005056227562689175, 0.00490530677297525, 0.004757798376298738, 0.00461366645852235, 0.004472873899604841, 0.004335382443691365, 0.00420115276835648, 0.004070144552931742, 0.003942316545853412, 0.0038176266309692957, 0.0036960318927472956, 0.003577488680331787, 0.0034619526703974545, 0.003349378928753702, 0.0032397219706562608, 0.003132935819786004, 0.003028974065858462, 0.002927789920830779, 0.0028293362736762687, 0.002733565743699892, 0.002640430732371218, 0.0025498834736545546, 0.0024618760828189652, 0.0023763606037139062, 0.00229328905449912, 0.0022126134718202357, 0.0021342859534243075, 0.0020582586992121447, 0.001984484050726921, 0.0019129145290809613, 0.0018435028713250836, 0.0017762020652671022, 0.0017109653827483589, 0.0016477464113892253, 0.0015864990848165619, 0.0015271777113880197, 0.0014697370014299018, 0.0014141320930070214, 0.0013603185762446192, 0.001308252516223945, 0.0012578904744745178, 0.0012091895290874438, 0.0011621072934753932, 0.0011166019338059942, 0.0010726321851364685, 0.0010301573662782775, 0.000989137393421446, 0.0009495327925490024, 0.0009113047106726964, 0.0008744149259217456, 0.0008388258565169343, 0.0008045005686628154, 0.0007714027833911662, 0.0007394968823891409, 0.0007087479128458104, 0.000679121591350921, 0.0006505843068798259, 0.0006231031228985443, 0.000596645778622899, 0.0005711806894655669, 0.0005466769467047441, 0.0005231043164079211, 0.0005004332376440023, 0.0004786348200167087, 0.0004576808405518453, 0.00043754373997063444, 0.00041819661838086536, 0.00039961323041714847, 0.00038176797986106103],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005297769779599651, 0.0014400831323245211, 0.0035028948673558203, 0.007624505815941894, 0.014850509523929386, 0.025883086683548395, 0.04036787018225523, 0.05633790120061767, 0.0703575241963199, 0.07862587491885455] + [0.07972551970467169] * 84 + [0.07862587491885455, 0.0703575241963199, 0.05633790120061767, 0.04036787018225523, 0.025883086683548395, 0.014850509523929386, 0.007624505815941894, 0.0035028948673558203, 0.0014400831323245211, 0.0005297769779599651],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0015778262083211557, -0.0038375051199620613, -0.008236275118899891, -0.015537013223027658, -0.025606281927606427, -0.03651497933986679, -0.04429414872795296, -0.04415533165953026, -0.03308600160203912, -0.012324745899567523] + [0.0] * 84 + [0.012324745899567523, 0.03308600160203912, 0.04415533165953026, 0.04429414872795296, 0.03651497933986679, 0.025606281927606427, 0.015537013223027658, 0.008236275118899891, 0.0038375051199620613, 0.0015778262083211557],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002658773462345805, 0.000722729558868374, 0.0017579857755571989, 0.0038264844586092008, 0.007452974037599812, 0.012989855516714248, 0.020259283894384607, 0.028274108326349662, 0.035310088205392824, 0.03945969688848365] + [0.040011571827594065] * 84 + [0.03945969688848365, 0.035310088205392824, 0.028274108326349662, 0.020259283894384607, 0.012989855516714248, 0.007452974037599812, 0.0038264844586092008, 0.0017579857755571989, 0.000722729558868374, 0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0007918582017346574, -0.001925915469913515, -0.004133511010432188, -0.0077975072832673215, -0.012850936467762062, -0.01832564684497857, -0.022229751777544996, -0.022160084133800988, -0.01660475760448769, -0.006185377751617155] + [0.0] * 84 + [0.006185377751617155, 0.01660475760448769, 0.022160084133800988, 0.022229751777544996, 0.01832564684497857, 0.012850936467762062, 0.0077975072832673215, 0.004133511010432188, 0.001925915469913515, 0.0007918582017346574],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002658773462345805, -0.000722729558868374, -0.0017579857755571989, -0.0038264844586092008, -0.007452974037599812, -0.012989855516714248, -0.020259283894384607, -0.028274108326349662, -0.035310088205392824, -0.03945969688848365] + [-0.040011571827594065] * 84 + [-0.03945969688848365, -0.035310088205392824, -0.028274108326349662, -0.020259283894384607, -0.012989855516714248, -0.007452974037599812, -0.0038264844586092008, -0.0017579857755571989, -0.000722729558868374, -0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0007918582017346574, 0.001925915469913515, 0.004133511010432188, 0.0077975072832673215, 0.012850936467762062, 0.01832564684497857, 0.022229751777544996, 0.022160084133800988, 0.01660475760448769, 0.006185377751617155] + [0.0] * 84 + [-0.006185377751617155, -0.01660475760448769, -0.022160084133800988, -0.022229751777544996, -0.01832564684497857, -0.012850936467762062, -0.0077975072832673215, -0.004133511010432188, -0.001925915469913515, -0.0007918582017346574],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001579946678574493, 0.00384266241511345, 0.008247344003607104, 0.015557893706690171, 0.025640694690456798, 0.03656405250589932, 0.044353676465722296, 0.04421467283843608, 0.03313046650053617, 0.012341309356887565] + [0.0] * 84 + [-0.012341309356887565, -0.03313046650053617, -0.04421467283843608, -0.044353676465722296, -0.03656405250589932, -0.025640694690456798, -0.015557893706690171, -0.008247344003607104, -0.00384266241511345, -0.001579946678574493],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005304889551832756, 0.0014420184870729228, 0.003507602473508908, 0.007634752532401437, 0.014870467402386671, 0.02591787144950523, 0.04042212132060027, 0.056413614763367065, 0.07045207899352757, 0.07873154170777515] + [0.07983266432685761] * 84 + [0.07873154170777515, 0.07045207899352757, 0.056413614763367065, 0.04042212132060027, 0.02591787144950523, 0.014870467402386671, 0.007634752532401437, 0.003507602473508908, 0.0014420184870729228, 0.0005304889551832756],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007918582017346574, 0.001925915469913515, 0.004133511010432188, 0.0077975072832673215, 0.012850936467762062, 0.01832564684497857, 0.022229751777544996, 0.022160084133800988, 0.01660475760448769, 0.006185377751617155] + [0.0] * 84 + [-0.006185377751617155, -0.01660475760448769, -0.022160084133800988, -0.022229751777544996, -0.01832564684497857, -0.012850936467762062, -0.0077975072832673215, -0.004133511010432188, -0.001925915469913515, -0.0007918582017346574],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002658773462345805, 0.000722729558868374, 0.0017579857755571989, 0.0038264844586092008, 0.007452974037599812, 0.012989855516714248, 0.020259283894384607, 0.028274108326349662, 0.035310088205392824, 0.03945969688848365] + [0.040011571827594065] * 84 + [0.03945969688848365, 0.035310088205392824, 0.028274108326349662, 0.020259283894384607, 0.012989855516714248, 0.007452974037599812, 0.0038264844586092008, 0.0017579857755571989, 0.000722729558868374, 0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0018464879486740189, 0.004490929938680866, 0.009638693202589267, 0.018182552377067635, 0.029966349107601292, 0.04273250687658816, 0.051836261428287955, 0.05167380751380678, 0.03871966564237693, 0.014423321563555132] + [0.0] * 84 + [-0.014423321563555132, -0.03871966564237693, -0.05167380751380678, -0.051836261428287955, -0.04273250687658816, -0.029966349107601292, -0.018182552377067635, -0.009638693202589267, -0.004490929938680866, -0.0018464879486740189],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0018464879486740189, -0.004490929938680866, -0.009638693202589267, -0.018182552377067635, -0.029966349107601292, -0.04273250687658816, -0.051836261428287955, -0.05167380751380678, -0.03871966564237693, -0.014423321563555132] + [0.0] * 84 + [0.014423321563555132, 0.03871966564237693, 0.05167380751380678, 0.051836261428287955, 0.04273250687658816, 0.029966349107601292, 0.018182552377067635, 0.009638693202589267, 0.004490929938680866, 0.0018464879486740189],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0007918582017346574, -0.001925915469913515, -0.004133511010432188, -0.0077975072832673215, -0.012850936467762062, -0.01832564684497857, -0.022229751777544996, -0.022160084133800988, -0.01660475760448769, -0.006185377751617155] + [0.0] * 84 + [0.006185377751617155, 0.01660475760448769, 0.022160084133800988, 0.022229751777544996, 0.01832564684497857, 0.012850936467762062, 0.0077975072832673215, 0.004133511010432188, 0.001925915469913515, 0.0007918582017346574],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002658773462345805, -0.000722729558868374, -0.0017579857755571989, -0.0038264844586092008, -0.007452974037599812, -0.012989855516714248, -0.020259283894384607, -0.028274108326349662, -0.035310088205392824, -0.03945969688848365] + [-0.040011571827594065] * 84 + [-0.03945969688848365, -0.035310088205392824, -0.028274108326349662, -0.020259283894384607, -0.012989855516714248, -0.007452974037599812, -0.0038264844586092008, -0.0017579857755571989, -0.000722729558868374, -0.0002658773462345805],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 52 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005036741853813904, 0.001369128385586146, 0.0033303027352868946, 0.007248836615301946, 0.01411880583366716, 0.024607793737457053, 0.038378893337198995, 0.05356206040244866, 0.0668909185549978, 0.074751877010869] + [0.07579734088481482] * 52 + [0.074751877010869, 0.0668909185549978, 0.05356206040244866, 0.038378893337198995, 0.024607793737457053, 0.01411880583366716, 0.007248836615301946, 0.0033303027352868946, 0.001369128385586146, 0.0005036741853813904],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 52 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 52 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00024954327146837384, 0.0006783289402467032, 0.001649984580635748, 0.0035914058250820498, 0.006995103380754364, 0.012191828628688103, 0.01901466240809702, 0.026537099115557586, 0.03314082621704963, 0.03703550525141325] + [0.03755347596120631] * 52 + [0.03703550525141325, 0.03314082621704963, 0.026537099115557586, 0.01901466240809702, 0.012191828628688103, 0.006995103380754364, 0.0035914058250820498, 0.001649984580635748, 0.0006783289402467032, 0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00024954327146837384, -0.0006783289402467032, -0.001649984580635748, -0.0035914058250820498, -0.006995103380754364, -0.012191828628688103, -0.01901466240809702, -0.026537099115557586, -0.03314082621704963, -0.03703550525141325] + [-0.03755347596120631] * 52 + [-0.03703550525141325, -0.03314082621704963, -0.026537099115557586, -0.01901466240809702, -0.012191828628688103, -0.006995103380754364, -0.0035914058250820498, -0.001649984580635748, -0.0006783289402467032, -0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005036741853813904, 0.001369128385586146, 0.0033303027352868946, 0.007248836615301946, 0.01411880583366716, 0.024607793737457053, 0.038378893337198995, 0.05356206040244866, 0.0668909185549978, 0.074751877010869] + [0.07579734088481482] * 52 + [0.074751877010869, 0.0668909185549978, 0.05356206040244866, 0.038378893337198995, 0.024607793737457053, 0.01411880583366716, 0.007248836615301946, 0.0033303027352868946, 0.001369128385586146, 0.0005036741853813904],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00024954327146837384, 0.0006783289402467032, 0.001649984580635748, 0.0035914058250820498, 0.006995103380754364, 0.012191828628688103, 0.01901466240809702, 0.026537099115557586, 0.03314082621704963, 0.03703550525141325] + [0.03755347596120631] * 52 + [0.03703550525141325, 0.03314082621704963, 0.026537099115557586, 0.01901466240809702, 0.012191828628688103, 0.006995103380754364, 0.0035914058250820498, 0.001649984580635748, 0.0006783289402467032, 0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00024954327146837384, -0.0006783289402467032, -0.001649984580635748, -0.0035914058250820498, -0.006995103380754364, -0.012191828628688103, -0.01901466240809702, -0.026537099115557586, -0.03314082621704963, -0.03703550525141325] + [-0.03755347596120631] * 52 + [-0.03703550525141325, -0.03314082621704963, -0.026537099115557586, -0.01901466240809702, -0.012191828628688103, -0.006995103380754364, -0.0035914058250820498, -0.001649984580635748, -0.0006783289402467032, -0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0009544199496526527, 0.0009990330760428713, 0.0010454915459521636, 0.0010938593499265864, 0.0011442021013796135, 0.001196587050041772, 0.0012510830941100059, 0.0013077607910198027, 0.0013666923667618605, 0.0014279517236639174, 0.0014916144465572478, 0.0015577578072463608, 0.0016264607671995649, 0.001697803978377303, 0.001771869782114526, 0.0018487422059728525, 0.001928506958477916, 0.0020112514216570386, 0.0020970646412923357, 0.0021860373148043645, 0.0022782617766817412, 0.0023738319813725066, 0.0024728434835536153, 0.002575393415695694, 0.002681580462841172, 0.002791504834514986, 0.0029052682336884834, 0.0030229738227186102, 0.0031447261861862947, 0.003270631290559863, 0.0034007964406115483, 0.003535330232517554, 0.003674342503574755, 0.00381794427847005, 0.003966247712041405, 0.0041193660284730635, 0.004277413456870898, 0.004440505163167756, 0.00460875717831271, 0.004782286322702404, 0.004961210126817303, 0.005145646748030363, 0.00533571488356077, 0.005531533679550589, 0.005733222636247801, 0.0059409015092847664, 0.006154690207047414, 0.006374708684136388, 0.006601076830928045, 0.0068339143592497315, 0.007073340684190673, 0.0073194748020769486, 0.007572435164646156, 0.00783233954946501, 0.008099304926640653, 0.008373447321884256, 0.008654881675993637, 0.008943721700829469, 0.00924007973186824, 0.009544066577423242, 0.00985579136463353, 0.010175361382329356, 0.0105028819208912, 0.010838456109228414, 0.011182184749012102, 0.011534166146305877, 0.011894495940746848, 0.012263266932438125, 0.01264056890672294, 0.013026488457019193, 0.013421108805902143, 0.013824509624631368, 0.014236766851326911, 0.014657952508007811, 0.015088134516714511, 0.015527376514944857, 0.01597573767064127, 0.01643327249697436, 0.016900030667175873, 0.01737605682968103, 0.017861390423847268, 0.01835606549652315, 0.018860110519747533, 0.019373548209865043, 0.019896395348349635, 0.020428662604633233, 0.020970354361241346, 0.021521468541541865, 0.022081996440417407, 0.022651922558174883, 0.02323122443800912, 0.023819872507339787, 0.024417829923342897, 0.02502505242299955, 0.025641488177985512, 0.026267077654725357, 0.02690175347993482, 0.027545440311973847, 0.028198054718331478, 0.02885950505956145, 0.029529691379984468, 0.030208505305469927, 0.030895829948605333, 0.0315915398215572, 0.032295500756921516, 0.03300756983685583, 0.033727595330777994, 0.03445541664190933, 0.03519086426293145, 0.03593375974101745, 0.03668391565248823, 0.037441135587334674, 0.03820521414383566, 0.038975936933489774, 0.039753080596467136, 0.040536412827774176, 0.04132569241431121, 0.04212066928298852, 0.04292108456005167, 0.0437266706417521, 0.04453715127648264, 0.04535224165848199, 0.04617164853319463, 0.04699507031435605, 0.04782219721285503, 0.048652711377406684, 0.04948628704705143, 0.05032259071547628, 0.0511612813071352, 0.05200201036512652, 0.05284442225076467, 0.053688154354764414, 0.054532837319935, 0.05537809527526149, 0.05622354608123026, 0.05706880158623501, 0.05791346789387918, 0.05875714564097031, 0.05959943028598117, 0.06043991240773271, 0.06127817801403309, 0.06211380885998769, 0.06294638277567495, 0.06377547400286353, 0.06460065354042732, 0.065421489498096, 0.0662375474581605, 0.06704839084473528, 0.06785358130016106, 0.0686526790681164, 0.06944524338298869, 0.07023083286504059, 0.07100900592089297, 0.07177932114883076, 0.07254133774842515, 0.07329461593395258, 0.07403871735107972, 0.07477320549627173, 0.0754976461383719, 0.07621160774179116, 0.07691466189073766, 0.07760638371390959, 0.078286352309068, 0.0789541511669012, 0.07960936859358786, 0.08025159813146333, 0.08088043897719088, 0.08149549639683906, 0.08209638213726655, 0.08268271483321636, 0.08325412040952458, 0.08381023247785133, 0.08435069272734667, 0.08487515130866995, 0.08538326721078707, 0.08587470862997923, 0.08634915333050441, 0.08680628899636386, 0.08724581357363653, 0.08766743560285638, 0.08807087454092134, 0.08845586107203625, 0.0888221374072075, 0.08916945757182367, 0.0894975876808728, 0.08980630620136561, 0.09009540420155242, 0.09036468558654144, 0.0906139673199465, 0.09084307963121346, 0.09105186620829663, 0.09124018437537909, 0.09140790525535415, 0.0915549139168087, 0.09168110950527397, 0.09178640535853383, 0.09187072910580608, 0.0919340227506378, 0.09197624273738188, 0.09199736000114803] + [0.09200000000000001] * 2800 + [0.09199736000114803, 0.09197624273738188, 0.0919340227506378, 0.09187072910580608, 0.09178640535853383, 0.09168110950527397, 0.0915549139168087, 0.09140790525535415, 0.09124018437537909, 0.09105186620829663, 0.09084307963121346, 0.0906139673199465, 0.09036468558654144, 0.09009540420155242, 0.08980630620136561, 0.0894975876808728, 0.08916945757182367, 0.0888221374072075, 0.08845586107203625, 0.08807087454092134, 0.08766743560285638, 0.08724581357363653, 0.08680628899636386, 0.08634915333050441, 0.08587470862997923, 0.08538326721078707, 0.08487515130866995, 0.08435069272734667, 0.08381023247785133, 0.08325412040952458, 0.08268271483321636, 0.08209638213726655, 0.08149549639683906, 0.08088043897719088, 0.08025159813146333, 0.07960936859358786, 0.0789541511669012, 0.078286352309068, 0.07760638371390959, 0.07691466189073766, 0.07621160774179116, 0.0754976461383719, 0.07477320549627173, 0.07403871735107972, 0.07329461593395258, 0.07254133774842515, 0.07177932114883076, 0.07100900592089297, 0.07023083286504059, 0.06944524338298869, 0.0686526790681164, 0.06785358130016106, 0.06704839084473528, 0.0662375474581605, 0.065421489498096, 0.06460065354042732, 0.06377547400286353, 0.06294638277567495, 0.06211380885998769, 0.06127817801403309, 0.06043991240773271, 0.05959943028598117, 0.05875714564097031, 0.05791346789387918, 0.05706880158623501, 0.05622354608123026, 0.05537809527526149, 0.054532837319935, 0.053688154354764414, 0.05284442225076467, 0.05200201036512652, 0.0511612813071352, 0.05032259071547628, 0.04948628704705143, 0.048652711377406684, 0.04782219721285503, 0.04699507031435605, 0.04617164853319463, 0.04535224165848199, 0.04453715127648264, 0.0437266706417521, 0.04292108456005167, 0.04212066928298852, 0.04132569241431121, 0.040536412827774176, 0.039753080596467136, 0.038975936933489774, 0.03820521414383566, 0.037441135587334674, 0.03668391565248823, 0.03593375974101745, 0.03519086426293145, 0.03445541664190933, 0.033727595330777994, 0.03300756983685583, 0.032295500756921516, 0.0315915398215572, 0.030895829948605333, 0.030208505305469927, 0.029529691379984468, 0.02885950505956145, 0.028198054718331478, 0.027545440311973847, 0.02690175347993482, 0.026267077654725357, 0.025641488177985512, 0.02502505242299955, 0.024417829923342897, 0.023819872507339787, 0.02323122443800912, 0.022651922558174883, 0.022081996440417407, 0.021521468541541865, 0.020970354361241346, 0.020428662604633233, 0.019896395348349635, 0.019373548209865043, 0.018860110519747533, 0.01835606549652315, 0.017861390423847268, 0.01737605682968103, 0.016900030667175873, 0.01643327249697436, 0.01597573767064127, 0.015527376514944857, 0.015088134516714511, 0.014657952508007811, 0.014236766851326911, 0.013824509624631368, 0.013421108805902143, 0.013026488457019193, 0.01264056890672294, 0.012263266932438125, 0.011894495940746848, 0.011534166146305877, 0.011182184749012102, 0.010838456109228414, 0.0105028819208912, 0.010175361382329356, 0.00985579136463353, 0.009544066577423242, 0.00924007973186824, 0.008943721700829469, 0.008654881675993637, 0.008373447321884256, 0.008099304926640653, 0.00783233954946501, 0.007572435164646156, 0.0073194748020769486, 0.007073340684190673, 0.0068339143592497315, 0.006601076830928045, 0.006374708684136388, 0.006154690207047414, 0.0059409015092847664, 0.005733222636247801, 0.005531533679550589, 0.00533571488356077, 0.005145646748030363, 0.004961210126817303, 0.004782286322702404, 0.00460875717831271, 0.004440505163167756, 0.004277413456870898, 0.0041193660284730635, 0.003966247712041405, 0.00381794427847005, 0.003674342503574755, 0.003535330232517554, 0.0034007964406115483, 0.003270631290559863, 0.0031447261861862947, 0.0030229738227186102, 0.0029052682336884834, 0.002791504834514986, 0.002681580462841172, 0.002575393415695694, 0.0024728434835536153, 0.0023738319813725066, 0.0022782617766817412, 0.0021860373148043645, 0.0020970646412923357, 0.0020112514216570386, 0.001928506958477916, 0.0018487422059728525, 0.001771869782114526, 0.001697803978377303, 0.0016264607671995649, 0.0015577578072463608, 0.0014916144465572478, 0.0014279517236639174, 0.0013666923667618605, 0.0013077607910198027, 0.0012510830941100059, 0.001196587050041772, 0.0011442021013796135, 0.0010938593499265864, 0.0010454915459521636, 0.0009990330760428713, 0.0009544199496526527],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005036741853813904, 0.001369128385586146, 0.0033303027352868946, 0.007248836615301946, 0.01411880583366716, 0.024607793737457053, 0.038378893337198995, 0.05356206040244866, 0.0668909185549978, 0.074751877010869] + [0.07579734088481482] * 52 + [0.074751877010869, 0.0668909185549978, 0.05356206040244866, 0.038378893337198995, 0.024607793737457053, 0.01411880583366716, 0.007248836615301946, 0.0033303027352868946, 0.001369128385586146, 0.0005036741853813904],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000229852241423118, -0.0005590344162393543, -0.0011998319504851734, -0.0022633781182614457, -0.0037302342073751572, -0.005319375354854596, -0.006452617730239048, -0.006432395341894583, -0.004819853788618043, -0.0017954261724427933] + [0.0] * 52 + [0.0017954261724427933, 0.004819853788618043, 0.006432395341894583, 0.006452617730239048, 0.005319375354854596, 0.0037302342073751572, 0.0022633781182614457, 0.0011998319504851734, 0.0005590344162393543, 0.000229852241423118],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00024954327146837384, 0.0006783289402467032, 0.001649984580635748, 0.0035914058250820498, 0.006995103380754364, 0.012191828628688103, 0.01901466240809702, 0.026537099115557586, 0.03314082621704963, 0.03703550525141325] + [0.03755347596120631] * 52 + [0.03703550525141325, 0.03314082621704963, 0.026537099115557586, 0.01901466240809702, 0.012191828628688103, 0.006995103380754364, 0.0035914058250820498, 0.001649984580635748, 0.0006783289402467032, 0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00011387933299704621, -0.00027697126662575906, -0.0005944517285705875, -0.0011213812353182428, -0.001848128958101703, -0.00263546230230862, -0.003196922504017968, -0.003186903406174865, -0.002387976428651453, -0.0008895363982413645] + [0.0] * 52 + [0.0008895363982413645, 0.002387976428651453, 0.003186903406174865, 0.003196922504017968, 0.00263546230230862, 0.001848128958101703, 0.0011213812353182428, 0.0005944517285705875, 0.00027697126662575906, 0.00011387933299704621],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00024954327146837384, -0.0006783289402467032, -0.001649984580635748, -0.0035914058250820498, -0.006995103380754364, -0.012191828628688103, -0.01901466240809702, -0.026537099115557586, -0.03314082621704963, -0.03703550525141325] + [-0.03755347596120631] * 52 + [-0.03703550525141325, -0.03314082621704963, -0.026537099115557586, -0.01901466240809702, -0.012191828628688103, -0.006995103380754364, -0.0035914058250820498, -0.001649984580635748, -0.0006783289402467032, -0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00011387933299704621, 0.00027697126662575906, 0.0005944517285705875, 0.0011213812353182428, 0.001848128958101703, 0.00263546230230862, 0.003196922504017968, 0.003186903406174865, 0.002387976428651453, 0.0008895363982413645] + [0.0] * 52 + [-0.0008895363982413645, -0.002387976428651453, -0.003186903406174865, -0.003196922504017968, -0.00263546230230862, -0.001848128958101703, -0.0011213812353182428, -0.0005944517285705875, -0.00027697126662575906, -0.00011387933299704621],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.000229852241423118, 0.0005590344162393543, 0.0011998319504851734, 0.0022633781182614457, 0.0037302342073751572, 0.005319375354854596, 0.006452617730239048, 0.006432395341894583, 0.004819853788618043, 0.0017954261724427933] + [0.0] * 52 + [-0.0017954261724427933, -0.004819853788618043, -0.006432395341894583, -0.006452617730239048, -0.005319375354854596, -0.0037302342073751572, -0.0022633781182614457, -0.0011998319504851734, -0.0005590344162393543, -0.000229852241423118],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005036741853813904, 0.001369128385586146, 0.0033303027352868946, 0.007248836615301946, 0.01411880583366716, 0.024607793737457053, 0.038378893337198995, 0.05356206040244866, 0.0668909185549978, 0.074751877010869] + [0.07579734088481482] * 52 + [0.074751877010869, 0.0668909185549978, 0.05356206040244866, 0.038378893337198995, 0.024607793737457053, 0.01411880583366716, 0.007248836615301946, 0.0033303027352868946, 0.001369128385586146, 0.0005036741853813904],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00011387933299704621, 0.00027697126662575906, 0.0005944517285705875, 0.0011213812353182428, 0.001848128958101703, 0.00263546230230862, 0.003196922504017968, 0.003186903406174865, 0.002387976428651453, 0.0008895363982413645] + [0.0] * 52 + [-0.0008895363982413645, -0.002387976428651453, -0.003186903406174865, -0.003196922504017968, -0.00263546230230862, -0.001848128958101703, -0.0011213812353182428, -0.0005944517285705875, -0.00027697126662575906, -0.00011387933299704621],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00024954327146837384, 0.0006783289402467032, 0.001649984580635748, 0.0035914058250820498, 0.006995103380754364, 0.012191828628688103, 0.01901466240809702, 0.026537099115557586, 0.03314082621704963, 0.03703550525141325] + [0.03755347596120631] * 52 + [0.03703550525141325, 0.03314082621704963, 0.026537099115557586, 0.01901466240809702, 0.012191828628688103, 0.006995103380754364, 0.0035914058250820498, 0.001649984580635748, 0.0006783289402467032, 0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 52 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 52 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 52 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 52 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00011387933299704621, -0.00027697126662575906, -0.0005944517285705875, -0.0011213812353182428, -0.001848128958101703, -0.00263546230230862, -0.003196922504017968, -0.003186903406174865, -0.002387976428651453, -0.0008895363982413645] + [0.0] * 52 + [0.0008895363982413645, 0.002387976428651453, 0.003186903406174865, 0.003196922504017968, 0.00263546230230862, 0.001848128958101703, 0.0011213812353182428, 0.0005944517285705875, 0.00027697126662575906, 0.00011387933299704621],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00024954327146837384, -0.0006783289402467032, -0.001649984580635748, -0.0035914058250820498, -0.006995103380754364, -0.012191828628688103, -0.01901466240809702, -0.026537099115557586, -0.03314082621704963, -0.03703550525141325] + [-0.03755347596120631] * 52 + [-0.03703550525141325, -0.03314082621704963, -0.026537099115557586, -0.01901466240809702, -0.012191828628688103, -0.006995103380754364, -0.0035914058250820498, -0.001649984580635748, -0.0006783289402467032, -0.00024954327146837384],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 16 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004584594824264715, 0.0012462220801646164, 0.0030313423094871675, 0.006598110404107627, 0.012851364240717448, 0.022398758379862677, 0.034933629886450615, 0.048753807922889233, 0.060886137884025485, 0.06804142010744486] + [0.06899303295649696] * 16 + [0.06804142010744486, 0.060886137884025485, 0.048753807922889233, 0.034933629886450615, 0.022398758379862677, 0.012851364240717448, 0.006598110404107627, 0.0030313423094871675, 0.0012462220801646164, 0.0004584594824264715],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009237862108423386, 0.002511111270313765, 0.006108090972458691, 0.013295053636299391, 0.025895228545068077, 0.045133026852869136, 0.0703905291978525, 0.09823789715690813, 0.12268428675750831, 0.13710202988651043] + [0.13901950975487745] * 16 + [0.13710202988651043, 0.12268428675750831, 0.09823789715690813, 0.0703905291978525, 0.045133026852869136, 0.025895228545068077, 0.013295053636299391, 0.006108090972458691, 0.002511111270313765, 0.0009237862108423386],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009241585176275647, 0.0025121233050826573, 0.006110552671591168, 0.01330041184431402, 0.02590566490921722, 0.045151216485857695, 0.07041889817687431, 0.09827748925651797, 0.12273373130632745, 0.13715728511266118] + [0.13907553776888446] * 16 + [0.13715728511266118, 0.12273373130632745, 0.09827748925651797, 0.07041889817687431, 0.045151216485857695, 0.02590566490921722, 0.01330041184431402, 0.006110552671591168, 0.0025121233050826573, 0.0009241585176275647],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00022789192203926555, 0.000619474470531941, 0.0015068254704029846, 0.0032798014207515514, 0.006388180875097287, 0.011134017932105219, 0.017364875989686557, 0.024234636691285665, 0.030265398622578776, 0.033822160083805515] + [0.03429518963062599] * 16 + [0.033822160083805515, 0.030265398622578776, 0.024234636691285665, 0.017364875989686557, 0.011134017932105219, 0.006388180875097287, 0.0032798014207515514, 0.0015068254704029846, 0.000619474470531941, 0.00022789192203926555],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00022789192203926555, -0.000619474470531941, -0.0015068254704029846, -0.0032798014207515514, -0.006388180875097287, -0.011134017932105219, -0.017364875989686557, -0.024234636691285665, -0.030265398622578776, -0.033822160083805515] + [-0.03429518963062599] * 16 + [-0.033822160083805515, -0.030265398622578776, -0.024234636691285665, -0.017364875989686557, -0.011134017932105219, -0.006388180875097287, -0.0032798014207515514, -0.0015068254704029846, -0.000619474470531941, -0.00022789192203926555],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0004562520807894206, 0.00124022174040651, 0.0030167469303251783, 0.006566341664958893, 0.012789487186036074, 0.022290912304449576, 0.034765430613111666, 0.04851906692712695, 0.060592981856959424, 0.06771381265708194] + [0.06866084365791984] * 16 + [0.06771381265708194, 0.060592981856959424, 0.04851906692712695, 0.034765430613111666, 0.022290912304449576, 0.012789487186036074, 0.006566341664958893, 0.0030167469303251783, 0.00124022174040651, 0.0004562520807894206],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00022879494998169543, 0.0006219291549784388, 0.001512796307332889, 0.003292797723130578, 0.006413494215648757, 0.01117813678113785, 0.01743368478332521, 0.02433066709864296, 0.0303853260881967, 0.03395618131349943] + [0.03443108525277117] * 16 + [0.03395618131349943, 0.0303853260881967, 0.02433066709864296, 0.01743368478332521, 0.01117813678113785, 0.006413494215648757, 0.003292797723130578, 0.001512796307332889, 0.0006219291549784388, 0.00022879494998169543],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00022879494998169543, -0.0006219291549784388, -0.001512796307332889, -0.003292797723130578, -0.006413494215648757, -0.01117813678113785, -0.01743368478332521, -0.02433066709864296, -0.0303853260881967, -0.03395618131349943] + [-0.03443108525277117] * 16 + [-0.03395618131349943, -0.0303853260881967, -0.02433066709864296, -0.01743368478332521, -0.01117813678113785, -0.006413494215648757, -0.003292797723130578, -0.001512796307332889, -0.0006219291549784388, -0.00022879494998169543],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0002116322497055882, 0.00022152472555733233, 0.00023182638627634928, 0.0002425514210706778, 0.00025371437900156645, 0.0002653301719657842, 0.00027741407738961, 0.0002899817406174345, 0.00030304917697762993, 0.000316632773508086, 0.00033074929032356367, 0.00034541586160680176, 0.0003606499962051209, 0.00037646957781409756, 0.0003928928647297427, 0.00040993848915050205, 0.00042762545601032043, 0.00044597314132395206, 0.0004650012900256918, 0.00048473001328270686, 0.0005051797852642122, 0.0005263714393478166, 0.0005483261637444973, 0.0005710654965238277, 0.0005946113200213033, 0.0006189858546098447, 0.0006442116518178811, 0.0006703115867767352, 0.0006973088499804392, 0.0007252269383415348, 0.0007540896455269085, 0.0007839210515582401, 0.0008147455116622282, 0.0008465876443564023, 0.0008794723187570072, 0.000913424641096201, 0.0009484699404365903, 0.0009846337535719808, 0.0010219418091041226, 0.001060420010686185, 0.0011000944194247064, 0.0011409912354328196, 0.0011831367785286922, 0.001226557468074261, 0.0012712798019505992, 0.0013173303346674917, 0.0013647356546061657, 0.0014135223603954597, 0.0014637170364231753, 0.0015153462274858098, 0.00156843641258141, 0.0016230139778518448, 0.0016791051886824084, 0.0017367361609683285, 0.001795932831559449, 0.0018567209278960743, 0.0019191259368507628, 0.0019831730727926213, 0.0020488872448925226, 0.0021162930236895013, 0.0021854146069404785, 0.002256275784777379, 0.002328899904197614, 0.002403309832915866, 0.002479527922607031, 0.002557575971572173, 0.0026374751868612576, 0.0027192461458884535, 0.002802908757577695, 0.0028884822230781683, 0.0029759849960913445, 0.0030654347428530422, 0.003156848301815967, 0.003250241643079993, 0.0033456298276193044, 0.0034430269663573375, 0.0035424461791421944, 0.003643899553676923, 0.003747398104460737, 0.003852951731798837, 0.003960569180940046, 0.004070258001402959, 0.004182024506552713, 0.004295873733491814, 0.004411809403329701, 0.0045298338818969336, 0.004649948140970907, 0.004772151720081022, 0.004896442688962121, 0.0050228176107257345, 0.005151271505819414, 0.005281797816844909, 0.005414388374306468, 0.0055490333633607695, 0.005685721291640265, 0.005824438958221709, 0.005965171423811634, 0.0061079019822202875, 0.006252612133195241, 0.006399281556685365, 0.006547888088605252, 0.006698407698169418, 0.00685081446686466, 0.0070050805691279, 0.00716117625479564, 0.0073190698333897705, 0.007478727660302946, 0.007640114124945111, 0.007803191640910885, 0.007967920638225608, 0.00813425955772565, 0.008302164847626385, 0.008471590962328777, 0.00864249036351295, 0.008814813523564452, 0.008988508931376012, 0.009163523100564659, 0.009339800580140932, 0.009517283967663631, 0.009695913924910246, 0.00987562919608963, 0.01005636662861992, 0.010238061196490983, 0.010420646026226776, 0.010604052425459157, 0.010788209914120613, 0.01097304625825923, 0.011158487506475174, 0.011344458028973457, 0.011530880559223706, 0.011717676238213034, 0.011904764661273846, 0.012092063927463847, 0.012279490691471025, 0.012466960218011925, 0.012654386438686892, 0.01284168201125147, 0.013028758381258632, 0.013215525846021911, 0.013401893620845078, 0.01358776990745951, 0.013773061964605966, 0.013957676180693141, 0.014141518148461043, 0.014324492741573014, 0.014506504193056066, 0.014687456175505155, 0.01486725188296304, 0.015045794114383539, 0.015222985358582332, 0.01539872788057575, 0.01557292380920465, 0.015745475225937135, 0.015916284254740735, 0.016085253152911663, 0.016252284402746005, 0.016417280803935067, 0.0165801455665646, 0.016740782404595506, 0.016899095629701516, 0.01705499024533748, 0.017208372040910386, 0.01735914768592377, 0.017507224823965047, 0.017652512166404264, 0.017794919585672305, 0.017934358207985803, 0.018070740505386054, 0.0182039803869591, 0.018333993289104497, 0.018460696264720668, 0.018584008071175728, 0.018703849256933393, 0.018820142246705075, 0.01893281142500061, 0.019041783217951913, 0.01914698617328576, 0.01924835103832416, 0.019345810835893318, 0.019439300938024675, 0.019528759137334734, 0.019614125715973253, 0.019695343512032965, 0.01977235798331742, 0.01984511726836745, 0.019913572244650634, 0.01997767658382249, 0.02003738680397223, 0.020092662318770747, 0.020143465483442983, 0.02018976163749186, 0.020231519144105797, 0.020268709426187224, 0.020301306998944536, 0.02032928949899553, 0.02035263770993576, 0.02037133558433091, 0.020385370262097947, 0.020394732085245545, 0.02039941460895021] + [0.0204] * 1360 + [0.02039941460895021, 0.020394732085245545, 0.020385370262097947, 0.02037133558433091, 0.02035263770993576, 0.02032928949899553, 0.020301306998944536, 0.020268709426187224, 0.020231519144105797, 0.02018976163749186, 0.020143465483442983, 0.020092662318770747, 0.02003738680397223, 0.01997767658382249, 0.019913572244650634, 0.01984511726836745, 0.01977235798331742, 0.019695343512032965, 0.019614125715973253, 0.019528759137334734, 0.019439300938024675, 0.019345810835893318, 0.01924835103832416, 0.01914698617328576, 0.019041783217951913, 0.01893281142500061, 0.018820142246705075, 0.018703849256933393, 0.018584008071175728, 0.018460696264720668, 0.018333993289104497, 0.0182039803869591, 0.018070740505386054, 0.017934358207985803, 0.017794919585672305, 0.017652512166404264, 0.017507224823965047, 0.01735914768592377, 0.017208372040910386, 0.01705499024533748, 0.016899095629701516, 0.016740782404595506, 0.0165801455665646, 0.016417280803935067, 0.016252284402746005, 0.016085253152911663, 0.015916284254740735, 0.015745475225937135, 0.01557292380920465, 0.01539872788057575, 0.015222985358582332, 0.015045794114383539, 0.01486725188296304, 0.014687456175505155, 0.014506504193056066, 0.014324492741573014, 0.014141518148461043, 0.013957676180693141, 0.013773061964605966, 0.01358776990745951, 0.013401893620845078, 0.013215525846021911, 0.013028758381258632, 0.01284168201125147, 0.012654386438686892, 0.012466960218011925, 0.012279490691471025, 0.012092063927463847, 0.011904764661273846, 0.011717676238213034, 0.011530880559223706, 0.011344458028973457, 0.011158487506475174, 0.01097304625825923, 0.010788209914120613, 0.010604052425459157, 0.010420646026226776, 0.010238061196490983, 0.01005636662861992, 0.00987562919608963, 0.009695913924910246, 0.009517283967663631, 0.009339800580140932, 0.009163523100564659, 0.008988508931376012, 0.008814813523564452, 0.00864249036351295, 0.008471590962328777, 0.008302164847626385, 0.00813425955772565, 0.007967920638225608, 0.007803191640910885, 0.007640114124945111, 0.007478727660302946, 0.0073190698333897705, 0.00716117625479564, 0.0070050805691279, 0.00685081446686466, 0.006698407698169418, 0.006547888088605252, 0.006399281556685365, 0.006252612133195241, 0.0061079019822202875, 0.005965171423811634, 0.005824438958221709, 0.005685721291640265, 0.0055490333633607695, 0.005414388374306468, 0.005281797816844909, 0.005151271505819414, 0.0050228176107257345, 0.004896442688962121, 0.004772151720081022, 0.004649948140970907, 0.0045298338818969336, 0.004411809403329701, 0.004295873733491814, 0.004182024506552713, 0.004070258001402959, 0.003960569180940046, 0.003852951731798837, 0.003747398104460737, 0.003643899553676923, 0.0035424461791421944, 0.0034430269663573375, 0.0033456298276193044, 0.003250241643079993, 0.003156848301815967, 0.0030654347428530422, 0.0029759849960913445, 0.0028884822230781683, 0.002802908757577695, 0.0027192461458884535, 0.0026374751868612576, 0.002557575971572173, 0.002479527922607031, 0.002403309832915866, 0.002328899904197614, 0.002256275784777379, 0.0021854146069404785, 0.0021162930236895013, 0.0020488872448925226, 0.0019831730727926213, 0.0019191259368507628, 0.0018567209278960743, 0.001795932831559449, 0.0017367361609683285, 0.0016791051886824084, 0.0016230139778518448, 0.00156843641258141, 0.0015153462274858098, 0.0014637170364231753, 0.0014135223603954597, 0.0013647356546061657, 0.0013173303346674917, 0.0012712798019505992, 0.001226557468074261, 0.0011831367785286922, 0.0011409912354328196, 0.0011000944194247064, 0.001060420010686185, 0.0010219418091041226, 0.0009846337535719808, 0.0009484699404365903, 0.000913424641096201, 0.0008794723187570072, 0.0008465876443564023, 0.0008147455116622282, 0.0007839210515582401, 0.0007540896455269085, 0.0007252269383415348, 0.0006973088499804392, 0.0006703115867767352, 0.0006442116518178811, 0.0006189858546098447, 0.0005946113200213033, 0.0005710654965238277, 0.0005483261637444973, 0.0005263714393478166, 0.0005051797852642122, 0.00048473001328270686, 0.0004650012900256918, 0.00044597314132395206, 0.00042762545601032043, 0.00040993848915050205, 0.0003928928647297427, 0.00037646957781409756, 0.0003606499962051209, 0.00034541586160680176, 0.00033074929032356367, 0.000316632773508086, 0.00030304917697762993, 0.0002899817406174345, 0.00027741407738961, 0.0002653301719657842, 0.00025371437900156645, 0.0002425514210706778, 0.00023182638627634928, 0.00022152472555733233, 0.0002116322497055882],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004584594824264715, 0.0012462220801646164, 0.0030313423094871675, 0.006598110404107627, 0.012851364240717448, 0.022398758379862677, 0.034933629886450615, 0.048753807922889233, 0.060886137884025485, 0.06804142010744486] + [0.06899303295649696] * 16 + [0.06804142010744486, 0.060886137884025485, 0.048753807922889233, 0.034933629886450615, 0.022398758379862677, 0.012851364240717448, 0.006598110404107627, 0.0030313423094871675, 0.0012462220801646164, 0.0004584594824264715],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002492222566622028, -0.0006061451387395355, -0.0013009437039374983, -0.002454116604739071, -0.004044586997649687, -0.00576764760596688, -0.006996390125030008, -0.0069744635637439285, -0.005226030560085027, -0.001946729601574247] + [0.0] * 16 + [0.001946729601574247, 0.005226030560085027, 0.0069744635637439285, 0.006996390125030008, 0.00576764760596688, 0.004044586997649687, 0.002454116604739071, 0.0013009437039374983, 0.0006061451387395355, 0.0002492222566622028],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00022789192203926555, 0.000619474470531941, 0.0015068254704029846, 0.0032798014207515514, 0.006388180875097287, 0.011134017932105219, 0.017364875989686557, 0.024234636691285665, 0.030265398622578776, 0.033822160083805515] + [0.03429518963062599] * 16 + [0.033822160083805515, 0.030265398622578776, 0.024234636691285665, 0.017364875989686557, 0.011134017932105219, 0.006388180875097287, 0.0032798014207515514, 0.0015068254704029846, 0.000619474470531941, 0.00022789192203926555],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0001238838790837346, -0.00030130379236787715, -0.0006466756006137288, -0.001219897005952234, -0.0020104910904470996, -0.002866993374446708, -0.003477779071098921, -0.003466879773807152, -0.002597765330690322, -0.0009676840977209827] + [0.0] * 16 + [0.0009676840977209827, 0.002597765330690322, 0.003466879773807152, 0.003477779071098921, 0.002866993374446708, 0.0020104910904470996, 0.001219897005952234, 0.0006466756006137288, 0.00030130379236787715, 0.0001238838790837346],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00022789192203926555, -0.000619474470531941, -0.0015068254704029846, -0.0032798014207515514, -0.006388180875097287, -0.011134017932105219, -0.017364875989686557, -0.024234636691285665, -0.030265398622578776, -0.033822160083805515] + [-0.03429518963062599] * 16 + [-0.033822160083805515, -0.030265398622578776, -0.024234636691285665, -0.017364875989686557, -0.011134017932105219, -0.006388180875097287, -0.0032798014207515514, -0.0015068254704029846, -0.000619474470531941, -0.00022789192203926555],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0001238838790837346, 0.00030130379236787715, 0.0006466756006137288, 0.001219897005952234, 0.0020104910904470996, 0.002866993374446708, 0.003477779071098921, 0.003466879773807152, 0.002597765330690322, 0.0009676840977209827] + [0.0] * 16 + [-0.0009676840977209827, -0.002597765330690322, -0.003466879773807152, -0.003477779071098921, -0.002866993374446708, -0.0020104910904470996, -0.001219897005952234, -0.0006466756006137288, -0.00030130379236787715, -0.0001238838790837346],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002480222954040475, 0.000603226656686416, 0.0012946798892017146, 0.002442300465650523, 0.004025113023826409, 0.005739877398881272, 0.00696270373919347, 0.006940882750436988, 0.00520086814365391, 0.0019373564415151143] + [0.0] * 16 + [-0.0019373564415151143, -0.00520086814365391, -0.006940882750436988, -0.00696270373919347, -0.005739877398881272, -0.004025113023826409, -0.002442300465650523, -0.0012946798892017146, -0.000603226656686416, -0.0002480222954040475],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0004562520807894206, 0.00124022174040651, 0.0030167469303251783, 0.006566341664958893, 0.012789487186036074, 0.022290912304449576, 0.034765430613111666, 0.04851906692712695, 0.060592981856959424, 0.06771381265708194] + [0.06866084365791984] * 16 + [0.06771381265708194, 0.060592981856959424, 0.04851906692712695, 0.034765430613111666, 0.022290912304449576, 0.012789487186036074, 0.006566341664958893, 0.0030167469303251783, 0.00124022174040651, 0.0004562520807894206],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0001243747723257072, 0.0003024977168441533, 0.0006492380702783674, 0.0012247308810339125, 0.002018457716102077, 0.0028783539137090023, 0.003491559865304777, 0.0034806173792509007, 0.0026080590465030517, 0.0009715185722906277] + [0.0] * 16 + [-0.0009715185722906277, -0.0026080590465030517, -0.0034806173792509007, -0.003491559865304777, -0.0028783539137090023, -0.002018457716102077, -0.0012247308810339125, -0.0006492380702783674, -0.0003024977168441533, -0.0001243747723257072],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00022879494998169543, 0.0006219291549784388, 0.001512796307332889, 0.003292797723130578, 0.006413494215648757, 0.01117813678113785, 0.01743368478332521, 0.02433066709864296, 0.0303853260881967, 0.03395618131349943] + [0.03443108525277117] * 16 + [0.03395618131349943, 0.0303853260881967, 0.02433066709864296, 0.01743368478332521, 0.01117813678113785, 0.006413494215648757, 0.003292797723130578, 0.001512796307332889, 0.0006219291549784388, 0.00022879494998169543],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005023799923555449, 0.0012218619406013165, 0.0026224306640677134, 0.004946986266958927, 0.008153042236972684, 0.011626372375411373, 0.014103260537813954, 0.01405906117199963, 0.01053458558632632, 0.003924200091337616] + [0.0] * 16 + [-0.003924200091337616, -0.01053458558632632, -0.01405906117199963, -0.014103260537813954, -0.011626372375411373, -0.008153042236972684, -0.004946986266958927, -0.0026224306640677134, -0.0012218619406013165, -0.0005023799923555449],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009241585176275647, 0.0025121233050826573, 0.006110552671591168, 0.01330041184431402, 0.02590566490921722, 0.045151216485857695, 0.07041889817687431, 0.09827748925651797, 0.12273373130632745, 0.13715728511266118] + [0.13907553776888446] * 16 + [0.13715728511266118, 0.12273373130632745, 0.09827748925651797, 0.07041889817687431, 0.045151216485857695, 0.02590566490921722, 0.01330041184431402, 0.006110552671591168, 0.0025121233050826573, 0.0009241585176275647],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009237862108423386, 0.002511111270313765, 0.006108090972458691, 0.013295053636299391, 0.025895228545068077, 0.045133026852869136, 0.0703905291978525, 0.09823789715690813, 0.12268428675750831, 0.13710202988651043] + [0.13901950975487745] * 16 + [0.13710202988651043, 0.12268428675750831, 0.09823789715690813, 0.0703905291978525, 0.045133026852869136, 0.025895228545068077, 0.013295053636299391, 0.006108090972458691, 0.002511111270313765, 0.0009237862108423386],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005021776033969969, -0.0012213697009233627, -0.0026213741908421855, -0.004944993322546817, -0.008149757699864426, -0.011621688571453107, -0.014097578893927232, -0.014053397334283041, -0.010530341619930378, -0.003922619186879429] + [0.0] * 16 + [0.003922619186879429, 0.010530341619930378, 0.014053397334283041, 0.014097578893927232, 0.011621688571453107, 0.008149757699864426, 0.004944993322546817, 0.0026213741908421855, 0.0012213697009233627, 0.0005021776033969969],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0001243747723257072, -0.0003024977168441533, -0.0006492380702783674, -0.0012247308810339125, -0.002018457716102077, -0.0028783539137090023, -0.003491559865304777, -0.0034806173792509007, -0.0026080590465030517, -0.0009715185722906277] + [0.0] * 16 + [0.0009715185722906277, 0.0026080590465030517, 0.0034806173792509007, 0.003491559865304777, 0.0028783539137090023, 0.002018457716102077, 0.0012247308810339125, 0.0006492380702783674, 0.0003024977168441533, 0.0001243747723257072],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00022879494998169543, -0.0006219291549784388, -0.001512796307332889, -0.003292797723130578, -0.006413494215648757, -0.01117813678113785, -0.01743368478332521, -0.02433066709864296, -0.0303853260881967, -0.03395618131349943] + [-0.03443108525277117] * 16 + [-0.03395618131349943, -0.0303853260881967, -0.02433066709864296, -0.01743368478332521, -0.01117813678113785, -0.006413494215648757, -0.003292797723130578, -0.001512796307332889, -0.0006219291549784388, -0.00022879494998169543],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0013108726096250905, 0.003563321194168571, 0.008667513174496726, 0.018865968609154488, 0.036745889277519136, 0.06404474108457679, 0.09988568309364833, 0.13940170041370717, 0.17409165589856954, 0.1945507451754984] + [0.1972716905733063] * 32 + [0.1945507451754984, 0.17409165589856954, 0.13940170041370717, 0.09988568309364833, 0.06404474108457679, 0.036745889277519136, 0.018865968609154488, 0.008667513174496726, 0.003563321194168571, 0.0013108726096250905],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006375492758954594, 0.0017330386114138498, 0.004215487231665607, 0.009175555685211025, 0.017871542153678276, 0.03114847163910304, 0.04857988828288349, 0.06779869569688633, 0.08467032444084573, 0.09462070211920537] + [0.09594404716081062] * 32 + [0.09462070211920537, 0.08467032444084573, 0.06779869569688633, 0.04857988828288349, 0.03114847163910304, 0.017871542153678276, 0.009175555685211025, 0.004215487231665607, 0.0017330386114138498, 0.0006375492758954594],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006375492758954594, -0.0017330386114138498, -0.004215487231665607, -0.009175555685211025, -0.017871542153678276, -0.03114847163910304, -0.04857988828288349, -0.06779869569688633, -0.08467032444084573, -0.09462070211920537] + [-0.09594404716081062] * 32 + [-0.09462070211920537, -0.08467032444084573, -0.06779869569688633, -0.04857988828288349, -0.03114847163910304, -0.017871542153678276, -0.009175555685211025, -0.004215487231665607, -0.0017330386114138498, -0.0006375492758954594],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0013091869210360456, 0.0035587390175085298, 0.0086563673713528, 0.018841708320418402, 0.03669863668730205, 0.06396238411987869, 0.0997572372363136, 0.13922243977926, 0.17386778645798365, 0.1943005668067351] + [0.19701801326301746] * 32 + [0.1943005668067351, 0.17386778645798365, 0.13922243977926, 0.0997572372363136, 0.06396238411987869, 0.03669863668730205, 0.018841708320418402, 0.0086563673713528, 0.0035587390175085298, 0.0013091869210360456],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006407333543414328, 0.0017416938339939274, 0.00423654041538191, 0.00922138067504585, 0.01796079704631055, 0.03130403479464389, 0.04882250823562685, 0.06813729911750878, 0.08509318893973015, 0.0950932612602027] + [0.0964232154135784] * 32 + [0.0950932612602027, 0.08509318893973015, 0.06813729911750878, 0.04882250823562685, 0.03130403479464389, 0.01796079704631055, 0.00922138067504585, 0.00423654041538191, 0.0017416938339939274, 0.0006407333543414328],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0006407333543414328, -0.0017416938339939274, -0.00423654041538191, -0.00922138067504585, -0.01796079704631055, -0.03130403479464389, -0.04882250823562685, -0.06813729911750878, -0.08509318893973015, -0.0950932612602027] + [-0.0964232154135784] * 32 + [-0.0950932612602027, -0.08509318893973015, -0.06813729911750878, -0.04882250823562685, -0.03130403479464389, -0.01796079704631055, -0.00922138067504585, -0.00423654041538191, -0.0017416938339939274, -0.0006407333543414328],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0003942169357260957, 0.0004126440966264034, 0.0004318334646324154, 0.0004518114706218509, 0.0004726052157872317, 0.0004942424771911667, 0.0005167517127845677, 0.0005401620658560055, 0.0005645033688798989, 0.0005898061467307485, 0.0006161016192301677, 0.0006434217029930621, 0.0006717990125389507, 0.0007012668606341033, 0.000731859257829913, 0.0007636109111626999, 0.0007965572219800087, 0.0008307342828583421, 0.0008661788735772692, 0.0009029284561148462, 0.0009410211686294149, 0.000980495818392992, 0.0010213918736417106, 0.0010637494543090911, 0.0011076093216083101, 0.001153012866430103, 0.0012000020965235042, 0.001248619622427252, 0.0012989086421204262, 0.0013509129243616826, 0.0014046767906873787, 0.0014602450960398592, 0.0015176632079982684, 0.0015769769845854554, 0.0016382327506257977, 0.0017014772726301785, 0.0017667577321858056, 0.0018341216978301604, 0.0019036170953900323, 0.0019752921767683842, 0.002049195487163669, 0.0021253758307081933, 0.002203882234514231, 0.002284763911118722, 0.002368070219319744, 0.0024538506234002295, 0.0025421546507369756, 0.0026330318477954646, 0.002726531734513758, 0.0028227037570814108, 0.0029215972391222348, 0.0030232613312926528, 0.003127744959310369, 0.0032350967704312004, 0.0033453650783950525, 0.0034585978068652364, 0.0035748424313886765, 0.0036941459199078246, 0.003816554671858621, 0.003942114455892209, 0.004070870346261676, 0.004202866657918648, 0.004338146880368105, 0.004476753610333476, 0.004618728483287608, 0.004764112103908949, 0.004912943975525872, 0.005065262428615747, 0.00522110454842904, 0.005380506101812275, 0.0055435014633074065, 0.005710123540608609, 0.005880403699461116, 0.006054371688090183, 0.006232055561251646, 0.006413481603998962, 0.006598674255264872, 0.006787656031358974, 0.006980447449485687, 0.007177066951389991, 0.007377530827241263, 0.007581853139868257, 0.007790045649460937, 0.008002117738857301, 0.008218076339535718, 0.008437925858435466, 0.008661668105730122, 0.008889302223680336, 0.009120824616694147, 0.009356228882724409, 0.009595505746134202, 0.009838642992162087, 0.010085625403119892, 0.010336434696456337, 0.010591049464820102, 0.010849445118256126, 0.011111593828668732, 0.01137746447668485, 0.01164702260104996, 0.011920230350688425, 0.012197046439558802, 0.012477426104433231, 0.01276132106572829, 0.013048679491512756, 0.013339445964815408, 0.013633561454353495, 0.013930963288799607, 0.014231585134701678, 0.014535356978167338, 0.014842205110420252, 0.015152052117332095, 0.01546481687302954, 0.01578041453767125, 0.01609875655948491, 0.01641975068114947, 0.016743300950602377, 0.017069307736345934, 0.017397667747321346, 0.017728274057412646, 0.018061016134636735, 0.018395779875068918, 0.018732447641546912, 0.019070898307189086, 0.01941100730375576, 0.019752646674874905, 0.020095685134146238, 0.02043998812812994, 0.020785417904218464, 0.021131833583381932, 0.02147909123776965, 0.02182704397314193, 0.022175542016098344, 0.022524432806060108, 0.022873561091955832, 0.023222769033551627, 0.023571896307357936, 0.023920780217037054, 0.024269255808226867, 0.024617155987687874, 0.024964311646672205, 0.025310551788404974, 0.025655703659560134, 0.025999592885604873, 0.026342043609878414, 0.026682878636263462, 0.027021919575300517, 0.027358986993588037, 0.027693900566303702, 0.028026479232675223, 0.028356541354221994, 0.028683904875582283, 0.029008387487734155, 0.029329806793412315, 0.029647980474517055, 0.02996272646130604, 0.030273863103154327, 0.030581209340663364, 0.030884584878894845, 0.03118381036150144, 0.031478707545522434, 0.03176909947660903, 0.032054810664440915, 0.0323356672580933, 0.03261149722111136, 0.032882130506047165, 0.033147399228213116, 0.03340713783840493, 0.03366118329434657, 0.0339093752306101, 0.03415155612676328, 0.03438757147349929, 0.034617269936503804, 0.034840503517817104, 0.03505712771445063, 0.03526700167402075, 0.03546998834716533, 0.03566595463651269, 0.03585477154197638, 0.03603631430215422, 0.03621046253161459, 0.03637710035385882, 0.0365361165297541, 0.03668740458123788, 0.036830862910101084, 0.036966394911664854, 0.037093909083172755, 0.03721331912672817, 0.03732454404661494, 0.03742750824084747, 0.037522141586805564, 0.03760837952081817, 0.03768616311156962, 0.0377554391272115, 0.03781616009607316, 0.037868284360874034, 0.03791177612635093, 0.03794660550022425, 0.03797274852743736, 0.037990187217614255, 0.037998909565691574] + [0.038000000000000006] * 640 + [0.037998909565691574, 0.037990187217614255, 0.03797274852743736, 0.03794660550022425, 0.03791177612635093, 0.037868284360874034, 0.03781616009607316, 0.0377554391272115, 0.03768616311156962, 0.03760837952081817, 0.037522141586805564, 0.03742750824084747, 0.03732454404661494, 0.03721331912672817, 0.037093909083172755, 0.036966394911664854, 0.036830862910101084, 0.03668740458123788, 0.0365361165297541, 0.03637710035385882, 0.03621046253161459, 0.03603631430215422, 0.03585477154197638, 0.03566595463651269, 0.03546998834716533, 0.03526700167402075, 0.03505712771445063, 0.034840503517817104, 0.034617269936503804, 0.03438757147349929, 0.03415155612676328, 0.0339093752306101, 0.03366118329434657, 0.03340713783840493, 0.033147399228213116, 0.032882130506047165, 0.03261149722111136, 0.0323356672580933, 0.032054810664440915, 0.03176909947660903, 0.031478707545522434, 0.03118381036150144, 0.030884584878894845, 0.030581209340663364, 0.030273863103154327, 0.02996272646130604, 0.029647980474517055, 0.029329806793412315, 0.029008387487734155, 0.028683904875582283, 0.028356541354221994, 0.028026479232675223, 0.027693900566303702, 0.027358986993588037, 0.027021919575300517, 0.026682878636263462, 0.026342043609878414, 0.025999592885604873, 0.025655703659560134, 0.025310551788404974, 0.024964311646672205, 0.024617155987687874, 0.024269255808226867, 0.023920780217037054, 0.023571896307357936, 0.023222769033551627, 0.022873561091955832, 0.022524432806060108, 0.022175542016098344, 0.02182704397314193, 0.02147909123776965, 0.021131833583381932, 0.020785417904218464, 0.02043998812812994, 0.020095685134146238, 0.019752646674874905, 0.01941100730375576, 0.019070898307189086, 0.018732447641546912, 0.018395779875068918, 0.018061016134636735, 0.017728274057412646, 0.017397667747321346, 0.017069307736345934, 0.016743300950602377, 0.01641975068114947, 0.01609875655948491, 0.01578041453767125, 0.01546481687302954, 0.015152052117332095, 0.014842205110420252, 0.014535356978167338, 0.014231585134701678, 0.013930963288799607, 0.013633561454353495, 0.013339445964815408, 0.013048679491512756, 0.01276132106572829, 0.012477426104433231, 0.012197046439558802, 0.011920230350688425, 0.01164702260104996, 0.01137746447668485, 0.011111593828668732, 0.010849445118256126, 0.010591049464820102, 0.010336434696456337, 0.010085625403119892, 0.009838642992162087, 0.009595505746134202, 0.009356228882724409, 0.009120824616694147, 0.008889302223680336, 0.008661668105730122, 0.008437925858435466, 0.008218076339535718, 0.008002117738857301, 0.007790045649460937, 0.007581853139868257, 0.007377530827241263, 0.007177066951389991, 0.006980447449485687, 0.006787656031358974, 0.006598674255264872, 0.006413481603998962, 0.006232055561251646, 0.006054371688090183, 0.005880403699461116, 0.005710123540608609, 0.0055435014633074065, 0.005380506101812275, 0.00522110454842904, 0.005065262428615747, 0.004912943975525872, 0.004764112103908949, 0.004618728483287608, 0.004476753610333476, 0.004338146880368105, 0.004202866657918648, 0.004070870346261676, 0.003942114455892209, 0.003816554671858621, 0.0036941459199078246, 0.0035748424313886765, 0.0034585978068652364, 0.0033453650783950525, 0.0032350967704312004, 0.003127744959310369, 0.0030232613312926528, 0.0029215972391222348, 0.0028227037570814108, 0.002726531734513758, 0.0026330318477954646, 0.0025421546507369756, 0.0024538506234002295, 0.002368070219319744, 0.002284763911118722, 0.002203882234514231, 0.0021253758307081933, 0.002049195487163669, 0.0019752921767683842, 0.0019036170953900323, 0.0018341216978301604, 0.0017667577321858056, 0.0017014772726301785, 0.0016382327506257977, 0.0015769769845854554, 0.0015176632079982684, 0.0014602450960398592, 0.0014046767906873787, 0.0013509129243616826, 0.0012989086421204262, 0.001248619622427252, 0.0012000020965235042, 0.001153012866430103, 0.0011076093216083101, 0.0010637494543090911, 0.0010213918736417106, 0.000980495818392992, 0.0009410211686294149, 0.0009029284561148462, 0.0008661788735772692, 0.0008307342828583421, 0.0007965572219800087, 0.0007636109111626999, 0.000731859257829913, 0.0007012668606341033, 0.0006717990125389507, 0.0006434217029930621, 0.0006161016192301677, 0.0005898061467307485, 0.0005645033688798989, 0.0005401620658560055, 0.0005167517127845677, 0.0004942424771911667, 0.0004726052157872317, 0.0004518114706218509, 0.0004318334646324154, 0.0004126440966264034, 0.0003942169357260957],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0013108726096250905, 0.003563321194168571, 0.008667513174496726, 0.018865968609154488, 0.036745889277519136, 0.06404474108457679, 0.09988568309364833, 0.13940170041370717, 0.17409165589856954, 0.1945507451754984] + [0.1972716905733063] * 32 + [0.1945507451754984, 0.17409165589856954, 0.13940170041370717, 0.09988568309364833, 0.06404474108457679, 0.036745889277519136, 0.018865968609154488, 0.008667513174496726, 0.003563321194168571, 0.0013108726096250905],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.001128538420722338, -0.002744771220528726, -0.005890986514419745, -0.011112831231339746, -0.018314864346118134, -0.026117297899854855, -0.03168134005447432, -0.03158205130242999, -0.023664725429875674, -0.00881526064147552] + [0.0] * 32 + [0.00881526064147552, 0.023664725429875674, 0.03158205130242999, 0.03168134005447432, 0.026117297899854855, 0.018314864346118134, 0.011112831231339746, 0.005890986514419745, 0.002744771220528726, 0.001128538420722338],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006375492758954594, 0.0017330386114138498, 0.004215487231665607, 0.009175555685211025, 0.017871542153678276, 0.03114847163910304, 0.04857988828288349, 0.06779869569688633, 0.08467032444084573, 0.09462070211920537] + [0.09594404716081062] * 32 + [0.09462070211920537, 0.08467032444084573, 0.06779869569688633, 0.04857988828288349, 0.03114847163910304, 0.017871542153678276, 0.009175555685211025, 0.004215487231665607, 0.0017330386114138498, 0.0006375492758954594],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005488701553978678, -0.0013349328464855672, -0.0028651099725490355, -0.00540477957405442, -0.00890752344373928, -0.012702274990062283, -0.015408373981438723, -0.015360084413477932, -0.011509454428525369, -0.004287344931564196] + [0.0] * 32 + [0.004287344931564196, 0.011509454428525369, 0.015360084413477932, 0.015408373981438723, 0.012702274990062283, 0.00890752344373928, 0.00540477957405442, 0.0028651099725490355, 0.0013349328464855672, 0.0005488701553978678],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006375492758954594, -0.0017330386114138498, -0.004215487231665607, -0.009175555685211025, -0.017871542153678276, -0.03114847163910304, -0.04857988828288349, -0.06779869569688633, -0.08467032444084573, -0.09462070211920537] + [-0.09594404716081062] * 32 + [-0.09462070211920537, -0.08467032444084573, -0.06779869569688633, -0.04857988828288349, -0.03114847163910304, -0.017871542153678276, -0.009175555685211025, -0.004215487231665607, -0.0017330386114138498, -0.0006375492758954594],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005488701553978678, 0.0013349328464855672, 0.0028651099725490355, 0.00540477957405442, 0.00890752344373928, 0.012702274990062283, 0.015408373981438723, 0.015360084413477932, 0.011509454428525369, 0.004287344931564196] + [0.0] * 32 + [-0.004287344931564196, -0.011509454428525369, -0.015360084413477932, -0.015408373981438723, -0.012702274990062283, -0.00890752344373928, -0.00540477957405442, -0.0028651099725490355, -0.0013349328464855672, -0.0005488701553978678],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0011270872008828645, 0.002741241640696169, 0.005883411126336524, 0.011098540923752948, 0.01829131273811941, 0.026083712919344002, 0.031640600112985466, 0.03154143903918775, 0.023634294282465072, 0.008803924845637174] + [0.0] * 32 + [-0.008803924845637174, -0.023634294282465072, -0.03154143903918775, -0.031640600112985466, -0.026083712919344002, -0.01829131273811941, -0.011098540923752948, -0.005883411126336524, -0.002741241640696169, -0.0011270872008828645],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0013091869210360456, 0.0035587390175085298, 0.0086563673713528, 0.018841708320418402, 0.03669863668730205, 0.06396238411987869, 0.0997572372363136, 0.13922243977926, 0.17386778645798365, 0.1943005668067351] + [0.19701801326301746] * 32 + [0.1943005668067351, 0.17386778645798365, 0.13922243977926, 0.0997572372363136, 0.06396238411987869, 0.03669863668730205, 0.018841708320418402, 0.0086563673713528, 0.0035587390175085298, 0.0013091869210360456],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005516113484279842, 0.0013415998306137297, 0.0028794190389284514, 0.005431772377273924, 0.008952009814403536, 0.01276571328658278, 0.015485327204251009, 0.015436796466268823, 0.011566935484745388, 0.004308756990369962] + [0.0] * 32 + [-0.004308756990369962, -0.011566935484745388, -0.015436796466268823, -0.015485327204251009, -0.01276571328658278, -0.008952009814403536, -0.005431772377273924, -0.0028794190389284514, -0.0013415998306137297, -0.0005516113484279842],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006407333543414328, 0.0017416938339939274, 0.00423654041538191, 0.00922138067504585, 0.01796079704631055, 0.03130403479464389, 0.04882250823562685, 0.06813729911750878, 0.08509318893973015, 0.0950932612602027] + [0.0964232154135784] * 32 + [0.0950932612602027, 0.08509318893973015, 0.06813729911750878, 0.04882250823562685, 0.03130403479464389, 0.01796079704631055, 0.00922138067504585, 0.00423654041538191, 0.0017416938339939274, 0.0006407333543414328],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005337479912314077, 0.0012981535217997109, 0.0027861720617631197, 0.005255870103939153, 0.008662108329603272, 0.012352308999384576, 0.014983851061775466, 0.014936891941038026, 0.011192352364179408, 0.004169222397016189] + [0.0] * 32 + [-0.004169222397016189, -0.011192352364179408, -0.014936891941038026, -0.014983851061775466, -0.012352308999384576, -0.008662108329603272, -0.005255870103939153, -0.0027861720617631197, -0.0012981535217997109, -0.0005337479912314077],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005337479912314077, -0.0012981535217997109, -0.0027861720617631197, -0.005255870103939153, -0.008662108329603272, -0.012352308999384576, -0.014983851061775466, -0.014936891941038026, -0.011192352364179408, -0.004169222397016189] + [0.0] * 32 + [0.004169222397016189, 0.011192352364179408, 0.014936891941038026, 0.014983851061775466, 0.012352308999384576, 0.008662108329603272, 0.005255870103939153, 0.0027861720617631197, 0.0012981535217997109, 0.0005337479912314077],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005516113484279842, -0.0013415998306137297, -0.0028794190389284514, -0.005431772377273924, -0.008952009814403536, -0.01276571328658278, -0.015485327204251009, -0.015436796466268823, -0.011566935484745388, -0.004308756990369962] + [0.0] * 32 + [0.004308756990369962, 0.011566935484745388, 0.015436796466268823, 0.015485327204251009, 0.01276571328658278, 0.008952009814403536, 0.005431772377273924, 0.0028794190389284514, 0.0013415998306137297, 0.0005516113484279842],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0006407333543414328, -0.0017416938339939274, -0.00423654041538191, -0.00922138067504585, -0.01796079704631055, -0.03130403479464389, -0.04882250823562685, -0.06813729911750878, -0.08509318893973015, -0.0950932612602027] + [-0.0964232154135784] * 32 + [-0.0950932612602027, -0.08509318893973015, -0.06813729911750878, -0.04882250823562685, -0.03130403479464389, -0.01796079704631055, -0.00922138067504585, -0.00423654041538191, -0.0017416938339939274, -0.0006407333543414328],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 480 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 480 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 480 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 480 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 480 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 480 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 480 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 480 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 480 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_ro_wf": {
            "type": "arbitrary",
            "samples": [0.00016598607820046132, 0.00017374488279006456, 0.00018182461668733276, 0.00019023640868288456, 0.00019899166980515015, 0.0002081020956594386, 0.00021757966854087058, 0.00022743665930779176, 0.00023768562900206266, 0.0002483394302024204, 0.00025941120809691267, 0.00027091440126023666, 0.00028286274212166343, 0.0002952702571090961, 0.00030815126645470015, 0.00032152038364745256, 0.0003353925145178984, 0.00034978285594035454, 0.0003647068941377975, 0.00038018040257467204, 0.0003962194394229115, 0.0004128403445865228, 0.0004300597362701939, 0.00044789450707751193, 0.00046636181962455154, 0.0004854791016547801, 0.0005052640406414754, 0.0005257345778641061, 0.0005469089019454425, 0.0005688054418364979, 0.000591442859236791, 0.0006148400404378353, 0.0006390160875782182, 0.0006639903092991391, 0.0006897822107898095, 0.0007164114832127066, 0.0007438979924992865, 0.0007722617675074359, 0.0008015229875326451, 0.0008317019691656353, 0.0008628191524899657, 0.000894895086613976, 0.0009279504145323077, 0.000962005857313146, 0.000997082197608313, 0.001033200262484307, 0.0010703809055734633, 0.0011086449885454586, 0.0011480133619005295, 0.0011885068450869097, 0.0012301462059462038, 0.001272952139491643, 0.0013169452460254183, 0.0013621460086026104, 0.0014085747698505482, 0.0014562517081537836, 0.0015051968132162846, 0.0015554298610138207, 0.001606970388150998, 0.0016598376656388244, 0.001714050672110179, 0.001769628066492062, 0.0018265881601549911, 0.0018849488885614631, 0.0019447277824368872, 0.0020059419384879785, 0.0020686079896951037, 0.0021327420752066304, 0.0021983598098648588, 0.002265476253394642, 0.0023341058792873287, 0.002404262543414151, 0.00247595945240468, 0.0025492091318274454, 0.002624023394211219, 0.002700413306946931, 0.0027783891601115248, 0.00285796043425641, 0.0029391357682044994, 0.0030219229269010483, 0.003106328769364742, 0.0031923592167866343, 0.003280019220825657, 0.003369312732150442, 0.003460242669278197, 0.0035528108877623007, 0.0036470181497811035, 0.0037428640941811935, 0.003840347207029114, 0.003939464792726066, 0.004040212945740716, 0.0041425865230156145, 0.004246579117103112, 0.004352183030086878, 0.004459389248345306, 0.004568187418213105, 0.00467856582259736, 0.004790511358604147, 0.004904009516231561, 0.0050190443581845995, 0.0051355985008668635, 0.005253653096603464, 0.005373187817148753, 0.005494180838531686, 0.005616608827290697, 0.005740446928148839, 0.005865668753178781, 0.005992246372505969, 0.006120150306596773, 0.006249349520176947, 0.006379811417824038, 0.0065115018412755955, 0.006644385068493157, 0.00677842381451996, 0.006913579234168197, 0.007049810926569421, 0.00718707694161934, 0.0073253337883458286, 0.0074645364452263765, 0.007604638372478625, 0.007745591526344806, 0.007887346375388172, 0.008029851918816456, 0.00817305570684453, 0.008316903863105221, 0.008461341109114204, 0.008606310790791553, 0.008751754907039352, 0.00889761414037134, 0.00904382788958722, 0.00919033430448081, 0.009337070322567722, 0.009483971707814782, 0.009630973091349823, 0.009778008014127, 0.00992500897151913, 0.010071907459805074, 0.010218634024516574, 0.01036511831060542, 0.010511289114388296, 0.010657074437223146, 0.010802401540867423, 0.010947197004465208, 0.0110913867831067, 0.011234896267900403, 0.011377650347494953, 0.011519573470984435, 0.011660589712127873, 0.011800622834810618, 0.011939596359672417, 0.012077433631824118, 0.012214057889572274, 0.012349392334068341, 0.012483360199796654, 0.012615884825813068, 0.012746889727643925, 0.012876298669752994, 0.013004035738482038, 0.013130025415369024, 0.013254192650746286, 0.013376462937519592, 0.013496762385027752, 0.013615017792881389, 0.013731156724678468, 0.01384510758149354, 0.0139567996750371, 0.014066163300381022, 0.014173129808145923, 0.014277631676046355, 0.014379602579689801, 0.014478977462526013, 0.014575692604843706, 0.014669685691712463, 0.014760895879768685, 0.014849263862745576, 0.014934731935648558, 0.015017244057479026, 0.015096745912411105, 0.015173184969328091, 0.015246510539627195, 0.01531667383320371, 0.015383628012528041, 0.015447328244731736, 0.015507731751621507, 0.015564797857543096, 0.015618488035020103, 0.01566876594809607, 0.015715597493311553, 0.015758950838251566, 0.01579879645760234, 0.01583510716666028, 0.01586785815223984, 0.015897027000931156, 0.01592259372466238, 0.015944540783525907, 0.015962853105831967, 0.015977518105357576, 0.015988525695763096, 0.015995868302153368, 0.01599954086976487] + [0.016] * 3600 + [0.01599954086976487, 0.015995868302153368, 0.015988525695763096, 0.015977518105357576, 0.015962853105831967, 0.015944540783525907, 0.01592259372466238, 0.015897027000931156, 0.01586785815223984, 0.01583510716666028, 0.01579879645760234, 0.015758950838251566, 0.015715597493311553, 0.01566876594809607, 0.015618488035020103, 0.015564797857543096, 0.015507731751621507, 0.015447328244731736, 0.015383628012528041, 0.01531667383320371, 0.015246510539627195, 0.015173184969328091, 0.015096745912411105, 0.015017244057479026, 0.014934731935648558, 0.014849263862745576, 0.014760895879768685, 0.014669685691712463, 0.014575692604843706, 0.014478977462526013, 0.014379602579689801, 0.014277631676046355, 0.014173129808145923, 0.014066163300381022, 0.0139567996750371, 0.01384510758149354, 0.013731156724678468, 0.013615017792881389, 0.013496762385027752, 0.013376462937519592, 0.013254192650746286, 0.013130025415369024, 0.013004035738482038, 0.012876298669752994, 0.012746889727643925, 0.012615884825813068, 0.012483360199796654, 0.012349392334068341, 0.012214057889572274, 0.012077433631824118, 0.011939596359672417, 0.011800622834810618, 0.011660589712127873, 0.011519573470984435, 0.011377650347494953, 0.011234896267900403, 0.0110913867831067, 0.010947197004465208, 0.010802401540867423, 0.010657074437223146, 0.010511289114388296, 0.01036511831060542, 0.010218634024516574, 0.010071907459805074, 0.00992500897151913, 0.009778008014127, 0.009630973091349823, 0.009483971707814782, 0.009337070322567722, 0.00919033430448081, 0.00904382788958722, 0.00889761414037134, 0.008751754907039352, 0.008606310790791553, 0.008461341109114204, 0.008316903863105221, 0.00817305570684453, 0.008029851918816456, 0.007887346375388172, 0.007745591526344806, 0.007604638372478625, 0.0074645364452263765, 0.0073253337883458286, 0.00718707694161934, 0.007049810926569421, 0.006913579234168197, 0.00677842381451996, 0.006644385068493157, 0.0065115018412755955, 0.006379811417824038, 0.006249349520176947, 0.006120150306596773, 0.005992246372505969, 0.005865668753178781, 0.005740446928148839, 0.005616608827290697, 0.005494180838531686, 0.005373187817148753, 0.005253653096603464, 0.0051355985008668635, 0.0050190443581845995, 0.004904009516231561, 0.004790511358604147, 0.00467856582259736, 0.004568187418213105, 0.004459389248345306, 0.004352183030086878, 0.004246579117103112, 0.0041425865230156145, 0.004040212945740716, 0.003939464792726066, 0.003840347207029114, 0.0037428640941811935, 0.0036470181497811035, 0.0035528108877623007, 0.003460242669278197, 0.003369312732150442, 0.003280019220825657, 0.0031923592167866343, 0.003106328769364742, 0.0030219229269010483, 0.0029391357682044994, 0.00285796043425641, 0.0027783891601115248, 0.002700413306946931, 0.002624023394211219, 0.0025492091318274454, 0.00247595945240468, 0.002404262543414151, 0.0023341058792873287, 0.002265476253394642, 0.0021983598098648588, 0.0021327420752066304, 0.0020686079896951037, 0.0020059419384879785, 0.0019447277824368872, 0.0018849488885614631, 0.0018265881601549911, 0.001769628066492062, 0.001714050672110179, 0.0016598376656388244, 0.001606970388150998, 0.0015554298610138207, 0.0015051968132162846, 0.0014562517081537836, 0.0014085747698505482, 0.0013621460086026104, 0.0013169452460254183, 0.001272952139491643, 0.0012301462059462038, 0.0011885068450869097, 0.0011480133619005295, 0.0011086449885454586, 0.0010703809055734633, 0.001033200262484307, 0.000997082197608313, 0.000962005857313146, 0.0009279504145323077, 0.000894895086613976, 0.0008628191524899657, 0.0008317019691656353, 0.0008015229875326451, 0.0007722617675074359, 0.0007438979924992865, 0.0007164114832127066, 0.0006897822107898095, 0.0006639903092991391, 0.0006390160875782182, 0.0006148400404378353, 0.000591442859236791, 0.0005688054418364979, 0.0005469089019454425, 0.0005257345778641061, 0.0005052640406414754, 0.0004854791016547801, 0.00046636181962455154, 0.00044789450707751193, 0.0004300597362701939, 0.0004128403445865228, 0.0003962194394229115, 0.00038018040257467204, 0.0003647068941377975, 0.00034978285594035454, 0.0003353925145178984, 0.00032152038364745256, 0.00030815126645470015, 0.0002952702571090961, 0.00028286274212166343, 0.00027091440126023666, 0.00025941120809691267, 0.0002483394302024204, 0.00023768562900206266, 0.00022743665930779176, 0.00021757966854087058, 0.0002081020956594386, 0.00019899166980515015, 0.00019023640868288456, 0.00018182461668733276, 0.00017374488279006456, 0.00016598607820046132],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 480 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005584056695718085, -0.0013581246177154947, -0.0029148854913752247, -0.0054986767403123705, -0.009062273734344742, -0.01292295145063834, -0.015676063465103366, -0.0156269349630974, -0.011709408032776217, -0.004361828920102192] + [0.0] * 480 + [0.004361828920102192, 0.011709408032776217, 0.0156269349630974, 0.015676063465103366, 0.01292295145063834, 0.009062273734344742, 0.0054986767403123705, 0.0029148854913752247, 0.0013581246177154947, 0.0005584056695718085],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 480 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002721764704218791, -0.0006619731585575026, -0.001420765024350152, -0.0026801490542112897, -0.004417107155989697, -0.006298867480993105, -0.007640781346852948, -0.007616835275024287, -0.005707365671151718, -0.0021260299899315835] + [0.0] * 480 + [0.0021260299899315835, 0.005707365671151718, 0.007616835275024287, 0.007640781346852948, 0.006298867480993105, 0.004417107155989697, 0.0026801490542112897, 0.001420765024350152, 0.0006619731585575026, 0.0002721764704218791],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 480 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002721764704218791, 0.0006619731585575026, 0.001420765024350152, 0.0026801490542112897, 0.004417107155989697, 0.006298867480993105, 0.007640781346852948, 0.007616835275024287, 0.005707365671151718, 0.0021260299899315835] + [0.0] * 480 + [-0.0021260299899315835, -0.005707365671151718, -0.007616835275024287, -0.007640781346852948, -0.006298867480993105, -0.004417107155989697, -0.0026801490542112897, -0.001420765024350152, -0.0006619731585575026, -0.0002721764704218791],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005584056695718085, 0.0013581246177154947, 0.0029148854913752247, 0.0054986767403123705, 0.009062273734344742, 0.01292295145063834, 0.015676063465103366, 0.0156269349630974, 0.011709408032776217, 0.004361828920102192] + [0.0] * 480 + [-0.004361828920102192, -0.011709408032776217, -0.0156269349630974, -0.015676063465103366, -0.01292295145063834, -0.009062273734344742, -0.0054986767403123705, -0.0029148854913752247, -0.0013581246177154947, -0.0005584056695718085],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 480 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002721764704218791, 0.0006619731585575026, 0.001420765024350152, 0.0026801490542112897, 0.004417107155989697, 0.006298867480993105, 0.007640781346852948, 0.007616835275024287, 0.005707365671151718, 0.0021260299899315835] + [0.0] * 480 + [-0.0021260299899315835, -0.005707365671151718, -0.007616835275024287, -0.007640781346852948, -0.006298867480993105, -0.004417107155989697, -0.0026801490542112897, -0.001420765024350152, -0.0006619731585575026, -0.0002721764704218791],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 480 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 480 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 480 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 480 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 480 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002721764704218791, -0.0006619731585575026, -0.001420765024350152, -0.0026801490542112897, -0.004417107155989697, -0.006298867480993105, -0.007640781346852948, -0.007616835275024287, -0.005707365671151718, -0.0021260299899315835] + [0.0] * 480 + [0.0021260299899315835, 0.005707365671151718, 0.007616835275024287, 0.007640781346852948, 0.006298867480993105, 0.004417107155989697, 0.0026801490542112897, 0.001420765024350152, 0.0006619731585575026, 0.0002721764704218791],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 480 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 280 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0004149651955011534, 0.0004343622069751615, 0.000454561541718332, 0.0004755910217072115, 0.0004974791745128755, 0.0005202552391485965, 0.0005439491713521765, 0.0005685916482694795, 0.0005942140725051567, 0.000620848575506051, 0.0006485280202422817, 0.0006772860031505917, 0.0007071568553041587, 0.0007381756427727404, 0.0007703781661367505, 0.0008038009591186315, 0.0008384812862947461, 0.0008744571398508864, 0.000911767235344494, 0.0009504510064366802, 0.000990548598557279, 0.0010321008614663071, 0.0010751493406754849, 0.00111973626769378, 0.001165904549061379, 0.0012136977541369505, 0.0012631601016036885, 0.0013143364446602654, 0.0013672722548636065, 0.0014220136045912449, 0.0014786071480919778, 0.0015371001010945887, 0.0015975402189455457, 0.0016599757732478479, 0.001724455526974524, 0.001791028708031767, 0.0018597449812482166, 0.0019306544187685899, 0.002003807468831613, 0.002079254922914089, 0.0021570478812249147, 0.0022372377165349403, 0.0023198760363307694, 0.0024050146432828654, 0.002492705494020783, 0.0025830006562107682, 0.0026759522639336585, 0.002771612471363647, 0.002870033404751324, 0.002971267112717275, 0.00307536551486551, 0.003182380348729108, 0.0032923631150635463, 0.003405365021506527, 0.0035214369246263713, 0.0036406292703844594, 0.003762992033040712, 0.0038885746525345525, 0.004017425970377496, 0.004149594164097062, 0.004285126680275449, 0.004424070166230155, 0.004566470400387479, 0.004712372221403659, 0.0048618194560922185, 0.005014854846219947, 0.00517151997423776, 0.005331855188016576, 0.005495899524662148, 0.005663690633486606, 0.005835264698218323, 0.006010656358535378, 0.006189898631011701, 0.006373022829568614, 0.006560058485528049, 0.006751033267367329, 0.006945972900278813, 0.007144901085641026, 0.00734783942051125, 0.007554807317252622, 0.007765821923411856, 0.007980898041966587, 0.008200048052064144, 0.008423281830376106, 0.008650606673195494, 0.008882027219405753, 0.00911754537445276, 0.009357160235452985, 0.009600868017572787, 0.009848661981815167, 0.010100532364351792, 0.010356466307539038, 0.01061644779275778, 0.010880457575217196, 0.011148473120863266, 0.011420468545532764, 0.011696414556493402, 0.01197627839651037, 0.012260023790578905, 0.0125476108954615, 0.01283899625216716, 0.013134132741508665, 0.013432969542871884, 0.013735452096329218, 0.014041522068226746, 0.0143511173203721, 0.014664171882946955, 0.014980615931264925, 0.015300375766491934, 0.015623373800442372, 0.0159495285445601, 0.01627875460318899, 0.016610962671232896, 0.016946059536299903, 0.017283948085420497, 0.017624527316423555, 0.017967692354048354, 0.018313334470864574, 0.018661341113065943, 0.019011595931196563, 0.019363978815862017, 0.019718365938470435, 0.020074629797041145, 0.02043263926711133, 0.020792259657763056, 0.021153352772785516, 0.021515776976978884, 0.021879387267598385, 0.02224403535092835, 0.022609569723968055, 0.022975835761202032, 0.02334267580641931, 0.023709929269536956, 0.02407743272837456, 0.024445020035317504, 0.02481252242879783, 0.02517976864951269, 0.025546585061291437, 0.025912795776513554, 0.026278222785970744, 0.026642686093057866, 0.027006003852168566, 0.027367992511163026, 0.027728466957766755, 0.028087240669751014, 0.028444125868737388, 0.028798933677461093, 0.029151474280319688, 0.02950155708702655, 0.029848990899181048, 0.0301935840795603, 0.03053514472393069, 0.030873480835170858, 0.03120840049949164, 0.031539712064532675, 0.03186722431910982, 0.03219074667438249, 0.032510089346205105, 0.032825063538422565, 0.03313548162686572, 0.03344115734379898, 0.03374190596256939, 0.03403754448220348, 0.034327891811696175, 0.03461276895373386, 0.034891999187592754, 0.03516540825095256, 0.035432824520364815, 0.03569407919011589, 0.03594900644922451, 0.03619744365631504, 0.036439231512109274, 0.03667421422928117, 0.03690223969942172, 0.03712315965686395, 0.037336829839121406, 0.03754311014369757, 0.03774186478102777, 0.037932962423320234, 0.038116276349067994, 0.038291684583009286, 0.03845907003132011, 0.03861832061182935, 0.03876932937905377, 0.03891199464385774, 0.039046220087550265, 0.03917191487024018, 0.03928899373327889, 0.03939737709562892, 0.03949699114400586, 0.03958776791665071, 0.03966964538059961, 0.039742567502327894, 0.03980648431165596, 0.039861351958814774, 0.039907132764579925, 0.03994379526339395, 0.039971314239407744, 0.03998967075538343, 0.03999885217441219] + [0.04000000000000001] * 1600 + [0.03999885217441219, 0.03998967075538343, 0.039971314239407744, 0.03994379526339395, 0.039907132764579925, 0.039861351958814774, 0.03980648431165596, 0.039742567502327894, 0.03966964538059961, 0.03958776791665071, 0.03949699114400586, 0.03939737709562892, 0.03928899373327889, 0.03917191487024018, 0.039046220087550265, 0.03891199464385774, 0.03876932937905377, 0.03861832061182935, 0.03845907003132011, 0.038291684583009286, 0.038116276349067994, 0.037932962423320234, 0.03774186478102777, 0.03754311014369757, 0.037336829839121406, 0.03712315965686395, 0.03690223969942172, 0.03667421422928117, 0.036439231512109274, 0.03619744365631504, 0.03594900644922451, 0.03569407919011589, 0.035432824520364815, 0.03516540825095256, 0.034891999187592754, 0.03461276895373386, 0.034327891811696175, 0.03403754448220348, 0.03374190596256939, 0.03344115734379898, 0.03313548162686572, 0.032825063538422565, 0.032510089346205105, 0.03219074667438249, 0.03186722431910982, 0.031539712064532675, 0.03120840049949164, 0.030873480835170858, 0.03053514472393069, 0.0301935840795603, 0.029848990899181048, 0.02950155708702655, 0.029151474280319688, 0.028798933677461093, 0.028444125868737388, 0.028087240669751014, 0.027728466957766755, 0.027367992511163026, 0.027006003852168566, 0.026642686093057866, 0.026278222785970744, 0.025912795776513554, 0.025546585061291437, 0.02517976864951269, 0.02481252242879783, 0.024445020035317504, 0.02407743272837456, 0.023709929269536956, 0.02334267580641931, 0.022975835761202032, 0.022609569723968055, 0.02224403535092835, 0.021879387267598385, 0.021515776976978884, 0.021153352772785516, 0.020792259657763056, 0.02043263926711133, 0.020074629797041145, 0.019718365938470435, 0.019363978815862017, 0.019011595931196563, 0.018661341113065943, 0.018313334470864574, 0.017967692354048354, 0.017624527316423555, 0.017283948085420497, 0.016946059536299903, 0.016610962671232896, 0.01627875460318899, 0.0159495285445601, 0.015623373800442372, 0.015300375766491934, 0.014980615931264925, 0.014664171882946955, 0.0143511173203721, 0.014041522068226746, 0.013735452096329218, 0.013432969542871884, 0.013134132741508665, 0.01283899625216716, 0.0125476108954615, 0.012260023790578905, 0.01197627839651037, 0.011696414556493402, 0.011420468545532764, 0.011148473120863266, 0.010880457575217196, 0.01061644779275778, 0.010356466307539038, 0.010100532364351792, 0.009848661981815167, 0.009600868017572787, 0.009357160235452985, 0.00911754537445276, 0.008882027219405753, 0.008650606673195494, 0.008423281830376106, 0.008200048052064144, 0.007980898041966587, 0.007765821923411856, 0.007554807317252622, 0.00734783942051125, 0.007144901085641026, 0.006945972900278813, 0.006751033267367329, 0.006560058485528049, 0.006373022829568614, 0.006189898631011701, 0.006010656358535378, 0.005835264698218323, 0.005663690633486606, 0.005495899524662148, 0.005331855188016576, 0.00517151997423776, 0.005014854846219947, 0.0048618194560922185, 0.004712372221403659, 0.004566470400387479, 0.004424070166230155, 0.004285126680275449, 0.004149594164097062, 0.004017425970377496, 0.0038885746525345525, 0.003762992033040712, 0.0036406292703844594, 0.0035214369246263713, 0.003405365021506527, 0.0032923631150635463, 0.003182380348729108, 0.00307536551486551, 0.002971267112717275, 0.002870033404751324, 0.002771612471363647, 0.0026759522639336585, 0.0025830006562107682, 0.002492705494020783, 0.0024050146432828654, 0.0023198760363307694, 0.0022372377165349403, 0.0021570478812249147, 0.002079254922914089, 0.002003807468831613, 0.0019306544187685899, 0.0018597449812482166, 0.001791028708031767, 0.001724455526974524, 0.0016599757732478479, 0.0015975402189455457, 0.0015371001010945887, 0.0014786071480919778, 0.0014220136045912449, 0.0013672722548636065, 0.0013143364446602654, 0.0012631601016036885, 0.0012136977541369505, 0.001165904549061379, 0.00111973626769378, 0.0010751493406754849, 0.0010321008614663071, 0.000990548598557279, 0.0009504510064366802, 0.000911767235344494, 0.0008744571398508864, 0.0008384812862947461, 0.0008038009591186315, 0.0007703781661367505, 0.0007381756427727404, 0.0007071568553041587, 0.0006772860031505917, 0.0006485280202422817, 0.000620848575506051, 0.0005942140725051567, 0.0005685916482694795, 0.0005439491713521765, 0.0005202552391485965, 0.0004974791745128755, 0.0004755910217072115, 0.000454561541718332, 0.0004343622069751615, 0.0004149651955011534],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0004454716972071287, -0.0010834526070203215, -0.002325368558673589, -0.004386604566136695, -0.0072294868784010405, -0.010309367238437193, -0.012505679970407689, -0.012466487393465151, -0.00934125520905161, -0.003479676940699813] + [0.0] * 280 + [0.003479676940699813, 0.00934125520905161, 0.012466487393465151, 0.012505679970407689, 0.010309367238437193, 0.0072294868784010405, 0.004386604566136695, 0.002325368558673589, 0.0010834526070203215, 0.0004454716972071287],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00020222042215584682, -0.0004918297726906548, -0.0010555934631785654, -0.001991284817321347, -0.0032818019588810336, -0.004679903590254542, -0.005676912582363025, -0.005659121240052427, -0.0042404322961097215, -0.0015795879835371531] + [0.0] * 280 + [0.0015795879835371531, 0.0042404322961097215, 0.005659121240052427, 0.005676912582363025, 0.004679903590254542, 0.0032818019588810336, 0.001991284817321347, 0.0010555934631785654, 0.0004918297726906548, 0.00020222042215584682],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00020222042215584682, 0.0004918297726906548, 0.0010555934631785654, 0.001991284817321347, 0.0032818019588810336, 0.004679903590254542, 0.005676912582363025, 0.005659121240052427, 0.0042404322961097215, 0.0015795879835371531] + [0.0] * 280 + [-0.0015795879835371531, -0.0042404322961097215, -0.005659121240052427, -0.005676912582363025, -0.004679903590254542, -0.0032818019588810336, -0.001991284817321347, -0.0010555934631785654, -0.0004918297726906548, -0.00020222042215584682],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004454716972071287, 0.0010834526070203215, 0.002325368558673589, 0.004386604566136695, 0.0072294868784010405, 0.010309367238437193, 0.012505679970407689, 0.012466487393465151, 0.00934125520905161, 0.003479676940699813] + [0.0] * 280 + [-0.003479676940699813, -0.00934125520905161, -0.012466487393465151, -0.012505679970407689, -0.010309367238437193, -0.0072294868784010405, -0.004386604566136695, -0.002325368558673589, -0.0010834526070203215, -0.0004454716972071287],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00020222042215584682, 0.0004918297726906548, 0.0010555934631785654, 0.001991284817321347, 0.0032818019588810336, 0.004679903590254542, 0.005676912582363025, 0.005659121240052427, 0.0042404322961097215, 0.0015795879835371531] + [0.0] * 280 + [-0.0015795879835371531, -0.0042404322961097215, -0.005659121240052427, -0.005676912582363025, -0.004679903590254542, -0.0032818019588810336, -0.001991284817321347, -0.0010555934631785654, -0.0004918297726906548, -0.00020222042215584682],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00028293028954752596, 0.0006881280263979384, 0.0014769001122518525, 0.0027860429917514725, 0.0045916291172029, 0.006547738669167547, 0.007942672176928421, 0.007917779984647775, 0.005932866347298917, 0.002210030425134476] + [0.0] * 280 + [-0.002210030425134476, -0.005932866347298917, -0.007917779984647775, -0.007942672176928421, -0.006547738669167547, -0.0045916291172029, -0.0027860429917514725, -0.0014769001122518525, -0.0006881280263979384, -0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00028293028954752596, -0.0006881280263979384, -0.0014769001122518525, -0.0027860429917514725, -0.0045916291172029, -0.006547738669167547, -0.007942672176928421, -0.007917779984647775, -0.005932866347298917, -0.002210030425134476] + [0.0] * 280 + [0.002210030425134476, 0.005932866347298917, 0.007917779984647775, 0.007942672176928421, 0.006547738669167547, 0.0045916291172029, 0.0027860429917514725, 0.0014769001122518525, 0.0006881280263979384, 0.00028293028954752596],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00020222042215584682, -0.0004918297726906548, -0.0010555934631785654, -0.001991284817321347, -0.0032818019588810336, -0.004679903590254542, -0.005676912582363025, -0.005659121240052427, -0.0042404322961097215, -0.0015795879835371531] + [0.0] * 280 + [0.0015795879835371531, 0.0042404322961097215, 0.005659121240052427, 0.005676912582363025, 0.004679903590254542, 0.0032818019588810336, 0.001991284817321347, 0.0010555934631785654, 0.0004918297726906548, 0.00020222042215584682],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "rise_wf": {
            "type": "arbitrary",
            "samples": [0.0032754804057496334, 0.005968314427627137, 0.010448563941567294, 0.01757477344936297, 0.028402141495854794, 0.04410021012179409, 0.06578978263086196, 0.09429843062234541, 0.1298609869433399, 0.17182294328429568, 0.21842977065588376, 0.26679072434338974, 0.3130818152967473, 0.3529987610338382, 0.38239899273324, 0.39800499167707293],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "fall_wf": {
            "type": "arbitrary",
            "samples": [0.39800499167707293, 0.38239899273324, 0.3529987610338382, 0.3130818152967473, 0.26679072434338974, 0.21842977065588376, 0.17182294328429568, 0.1298609869433399, 0.09429843062234541, 0.06578978263086196, 0.04410021012179409, 0.028402141495854794, 0.01757477344936297, 0.010448563941567294, 0.005968314427627137, 0.0032754804057496334],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0015648193824325564, 0.004253620092086923, 0.010346613784859734, 0.02252074925603363, 0.04386442995603347, 0.07645170969029776, 0.11923588286520037, 0.1664070796427832, 0.20781729320576267, 0.23223978797175873] + [0.23548784431664505] * 32 + [0.23223978797175873, 0.20781729320576267, 0.1664070796427832, 0.11923588286520037, 0.07645170969029776, 0.04386442995603347, 0.02252074925603363, 0.010346613784859734, 0.004253620092086923, 0.0015648193824325564],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007723712416023449, 0.0020995227108720053, 0.005106932483779149, 0.011115902103447699, 0.021650820923916358, 0.03773541061609538, 0.05885303308870271, 0.08213602423259626, 0.10257548096717262, 0.11463005596618349] + [0.11623324758053732] * 32 + [0.11463005596618349, 0.10257548096717262, 0.08213602423259626, 0.05885303308870271, 0.03773541061609538, 0.021650820923916358, 0.011115902103447699, 0.005106932483779149, 0.0020995227108720053, 0.0007723712416023449],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0007723712416023449, -0.0020995227108720053, -0.005106932483779149, -0.011115902103447699, -0.021650820923916358, -0.03773541061609538, -0.05885303308870271, -0.08213602423259626, -0.10257548096717262, -0.11463005596618349] + [-0.11623324758053732] * 32 + [-0.11463005596618349, -0.10257548096717262, -0.08213602423259626, -0.05885303308870271, -0.03773541061609538, -0.021650820923916358, -0.011115902103447699, -0.005106932483779149, -0.0020995227108720053, -0.0007723712416023449],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0015648193824325564, 0.004253620092086923, 0.010346613784859734, 0.02252074925603363, 0.04386442995603347, 0.07645170969029776, 0.11923588286520037, 0.1664070796427832, 0.20781729320576267, 0.23223978797175873] + [0.23548784431664505] * 32 + [0.23223978797175873, 0.20781729320576267, 0.1664070796427832, 0.11923588286520037, 0.07645170969029776, 0.04386442995603347, 0.02252074925603363, 0.010346613784859734, 0.004253620092086923, 0.0015648193824325564],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0007723712416023449, 0.0020995227108720053, 0.005106932483779149, 0.011115902103447699, 0.021650820923916358, 0.03773541061609538, 0.05885303308870271, 0.08213602423259626, 0.10257548096717262, 0.11463005596618349] + [0.11623324758053732] * 32 + [0.11463005596618349, 0.10257548096717262, 0.08213602423259626, 0.05885303308870271, 0.03773541061609538, 0.021650820923916358, 0.011115902103447699, 0.005106932483779149, 0.0020995227108720053, 0.0007723712416023449],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0007723712416023449, -0.0020995227108720053, -0.005106932483779149, -0.011115902103447699, -0.021650820923916358, -0.03773541061609538, -0.05885303308870271, -0.08213602423259626, -0.10257548096717262, -0.11463005596618349] + [-0.11623324758053732] * 32 + [-0.11463005596618349, -0.10257548096717262, -0.08213602423259626, -0.05885303308870271, -0.03773541061609538, -0.021650820923916358, -0.011115902103447699, -0.005106932483779149, -0.0020995227108720053, -0.0007723712416023449],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001135946761023375, 0.0030878234385867498, 0.007510900330363067, 0.016348450473205704, 0.03184243350515918, 0.055498463894529455, 0.08655670837098965, 0.1207996176771063, 0.15086046591188984, 0.1685894473758188] + [0.17094730357699864] * 32 + [0.1685894473758188, 0.15086046591188984, 0.1207996176771063, 0.08655670837098965, 0.055498463894529455, 0.03184243350515918, 0.016348450473205704, 0.007510900330363067, 0.0030878234385867498, 0.001135946761023375],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005662189655832061, 0.0015391427250737064, 0.0037438499422502635, 0.008148975844156069, 0.01587203765139504, 0.02766351724926547, 0.04314467152840492, 0.06021323966129995, 0.07519723624994168, 0.08403434542599673] + [0.08520963193152209] * 32 + [0.08403434542599673, 0.07519723624994168, 0.06021323966129995, 0.04314467152840492, 0.02766351724926547, 0.01587203765139504, 0.008148975844156069, 0.0037438499422502635, 0.0015391427250737064, 0.0005662189655832061],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005662189655832061, -0.0015391427250737064, -0.0037438499422502635, -0.008148975844156069, -0.01587203765139504, -0.02766351724926547, -0.04314467152840492, -0.06021323966129995, -0.07519723624994168, -0.08403434542599673] + [-0.08520963193152209] * 32 + [-0.08403434542599673, -0.07519723624994168, -0.06021323966129995, -0.04314467152840492, -0.02766351724926547, -0.01587203765139504, -0.008148975844156069, -0.0037438499422502635, -0.0015391427250737064, -0.0005662189655832061],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001135946761023375, 0.0030878234385867498, 0.007510900330363067, 0.016348450473205704, 0.03184243350515918, 0.055498463894529455, 0.08655670837098965, 0.1207996176771063, 0.15086046591188984, 0.1685894473758188] + [0.17094730357699864] * 32 + [0.1685894473758188, 0.15086046591188984, 0.1207996176771063, 0.08655670837098965, 0.055498463894529455, 0.03184243350515918, 0.016348450473205704, 0.007510900330363067, 0.0030878234385867498, 0.001135946761023375],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005662189655832061, 0.0015391427250737064, 0.0037438499422502635, 0.008148975844156069, 0.01587203765139504, 0.02766351724926547, 0.04314467152840492, 0.06021323966129995, 0.07519723624994168, 0.08403434542599673] + [0.08520963193152209] * 32 + [0.08403434542599673, 0.07519723624994168, 0.06021323966129995, 0.04314467152840492, 0.02766351724926547, 0.01587203765139504, 0.008148975844156069, 0.0037438499422502635, 0.0015391427250737064, 0.0005662189655832061],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005662189655832061, -0.0015391427250737064, -0.0037438499422502635, -0.008148975844156069, -0.01587203765139504, -0.02766351724926547, -0.04314467152840492, -0.06021323966129995, -0.07519723624994168, -0.08403434542599673] + [-0.08520963193152209] * 32 + [-0.08403434542599673, -0.07519723624994168, -0.06021323966129995, -0.04314467152840492, -0.02766351724926547, -0.01587203765139504, -0.008148975844156069, -0.0037438499422502635, -0.0015391427250737064, -0.0005662189655832061],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 84 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005136476804361093, 0.0013962391559596142, 0.003396247663228654, 0.007392374319304851, 0.014398379105928448, 0.025095064509458653, 0.03913885228290969, 0.05462266854963783, 0.06821545784006897, 0.07623207491923373] + [0.07729824052671945] * 84 + [0.07623207491923373, 0.06821545784006897, 0.05462266854963783, 0.03913885228290969, 0.025095064509458653, 0.014398379105928448, 0.007392374319304851, 0.003396247663228654, 0.0013962391559596142, 0.0005136476804361093],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002553521424438162, 0.0006941190886631113, 0.001688392939570792, 0.003675006608768168, 0.007157935472998664, 0.01247563014752701, 0.019457285925534668, 0.02715482999612888, 0.033912278728598505, 0.037897618143697916] + [0.038427646181282436] * 84 + [0.037897618143697916, 0.033912278728598505, 0.02715482999612888, 0.019457285925534668, 0.01247563014752701, 0.007157935472998664, 0.003675006608768168, 0.001688392939570792, 0.0006941190886631113, 0.0002553521424438162],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002553521424438162, -0.0006941190886631113, -0.001688392939570792, -0.003675006608768168, -0.007157935472998664, -0.01247563014752701, -0.019457285925534668, -0.02715482999612888, -0.033912278728598505, -0.037897618143697916] + [-0.038427646181282436] * 84 + [-0.037897618143697916, -0.033912278728598505, -0.02715482999612888, -0.019457285925534668, -0.01247563014752701, -0.007157935472998664, -0.003675006608768168, -0.001688392939570792, -0.0006941190886631113, -0.0002553521424438162],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005136476804361093, 0.0013962391559596142, 0.003396247663228654, 0.007392374319304851, 0.014398379105928448, 0.025095064509458653, 0.03913885228290969, 0.05462266854963783, 0.06821545784006897, 0.07623207491923373] + [0.07729824052671945] * 84 + [0.07623207491923373, 0.06821545784006897, 0.05462266854963783, 0.03913885228290969, 0.025095064509458653, 0.014398379105928448, 0.007392374319304851, 0.003396247663228654, 0.0013962391559596142, 0.0005136476804361093],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002553521424438162, 0.0006941190886631113, 0.001688392939570792, 0.003675006608768168, 0.007157935472998664, 0.01247563014752701, 0.019457285925534668, 0.02715482999612888, 0.033912278728598505, 0.037897618143697916] + [0.038427646181282436] * 84 + [0.037897618143697916, 0.033912278728598505, 0.02715482999612888, 0.019457285925534668, 0.01247563014752701, 0.007157935472998664, 0.003675006608768168, 0.001688392939570792, 0.0006941190886631113, 0.0002553521424438162],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002553521424438162, -0.0006941190886631113, -0.001688392939570792, -0.003675006608768168, -0.007157935472998664, -0.01247563014752701, -0.019457285925534668, -0.02715482999612888, -0.033912278728598505, -0.037897618143697916] + [-0.038427646181282436] * 84 + [-0.037897618143697916, -0.033912278728598505, -0.02715482999612888, -0.019457285925534668, -0.01247563014752701, -0.007157935472998664, -0.003675006608768168, -0.001688392939570792, -0.0006941190886631113, -0.0002553521424438162],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005045155839941109, 0.0013714155441455946, 0.003335866077984888, 0.007260945953538794, 0.014142391603965713, 0.024648901588750105, 0.03844300610801177, 0.05365153698200165, 0.0670026612801747, 0.07487675163704735] + [0.0759239619809905] * 32 + [0.07487675163704735, 0.0670026612801747, 0.05365153698200165, 0.03844300610801177, 0.024648901588750105, 0.014142391603965713, 0.007260945953538794, 0.003335866077984888, 0.0013714155441455946, 0.0005045155839941109],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00022595032861955896, 0.0006141966724208969, 0.0014939876199350922, 0.0032518581711642393, 0.006333754856658392, 0.011039158334808279, 0.01721693073276873, 0.024028162452498593, 0.03000754350299156, 0.03353400207069409] + [0.03400300150075038] * 32 + [0.03353400207069409, 0.03000754350299156, 0.024028162452498593, 0.01721693073276873, 0.011039158334808279, 0.006333754856658392, 0.0032518581711642393, 0.0014939876199350922, 0.0006141966724208969, 0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00022595032861955896, -0.0006141966724208969, -0.0014939876199350922, -0.0032518581711642393, -0.006333754856658392, -0.011039158334808279, -0.01721693073276873, -0.024028162452498593, -0.03000754350299156, -0.03353400207069409] + [-0.03400300150075038] * 32 + [-0.03353400207069409, -0.03000754350299156, -0.024028162452498593, -0.01721693073276873, -0.011039158334808279, -0.006333754856658392, -0.0032518581711642393, -0.0014939876199350922, -0.0006141966724208969, -0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005045155839941109, 0.0013714155441455946, 0.003335866077984888, 0.007260945953538794, 0.014142391603965713, 0.024648901588750105, 0.03844300610801177, 0.05365153698200165, 0.0670026612801747, 0.07487675163704735] + [0.0759239619809905] * 32 + [0.07487675163704735, 0.0670026612801747, 0.05365153698200165, 0.03844300610801177, 0.024648901588750105, 0.014142391603965713, 0.007260945953538794, 0.003335866077984888, 0.0013714155441455946, 0.0005045155839941109],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00022595032861955896, 0.0006141966724208969, 0.0014939876199350922, 0.0032518581711642393, 0.006333754856658392, 0.011039158334808279, 0.01721693073276873, 0.024028162452498593, 0.03000754350299156, 0.03353400207069409] + [0.03400300150075038] * 32 + [0.03353400207069409, 0.03000754350299156, 0.024028162452498593, 0.01721693073276873, 0.011039158334808279, 0.006333754856658392, 0.0032518581711642393, 0.0014939876199350922, 0.0006141966724208969, 0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00022595032861955896, -0.0006141966724208969, -0.0014939876199350922, -0.0032518581711642393, -0.006333754856658392, -0.011039158334808279, -0.01721693073276873, -0.024028162452498593, -0.03000754350299156, -0.03353400207069409] + [-0.03400300150075038] * 32 + [-0.03353400207069409, -0.03000754350299156, -0.024028162452498593, -0.01721693073276873, -0.011039158334808279, -0.006333754856658392, -0.0032518581711642393, -0.0014939876199350922, -0.0006141966724208969, -0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 84 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0001241310711956625, 0.0003374232351783254, 0.0008207568661156978, 0.001786483961449053, 0.0034795956255125296, 0.006064618527311404, 0.009458521559216294, 0.013200430210986913, 0.016485342339326647, 0.018422684418935128] + [0.018680340170085043] * 84 + [0.018422684418935128, 0.016485342339326647, 0.013200430210986913, 0.009458521559216294, 0.006064618527311404, 0.0034795956255125296, 0.001786483961449053, 0.0008207568661156978, 0.0003374232351783254, 0.0001241310711956625],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002308102618338501, 0.0006274073405648289, 0.0015261215853965336, 0.003321801922212349, 0.006469986681533849, 0.01127659800828397, 0.0175872472267855, 0.024544980752762718, 0.03065297145275578, 0.034255280112054566] + [0.0347343671835918] * 84 + [0.034255280112054566, 0.03065297145275578, 0.024544980752762718, 0.0175872472267855, 0.01127659800828397, 0.006469986681533849, 0.003321801922212349, 0.0015261215853965336, 0.0006274073405648289, 0.0002308102618338501],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [5.831587440376806e-05, 0.00015851898170246266, 0.0003855856060807585, 0.0008392771714343294, 0.0016346887166827247, 0.0028491136742709, 0.004443544633745687, 0.006201466102280098, 0.007744693927984771, 0.008654843146092307] + [0.008775887943971985] * 84 + [0.008654843146092307, 0.007744693927984771, 0.006201466102280098, 0.004443544633745687, 0.0028491136742709, 0.0016346887166827247, 0.0008392771714343294, 0.0003855856060807585, 0.00015851898170246266, 5.831587440376806e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-5.831587440376806e-05, -0.00015851898170246266, -0.0003855856060807585, -0.0008392771714343294, -0.0016346887166827247, -0.0028491136742709, -0.004443544633745687, -0.006201466102280098, -0.007744693927984771, -0.008654843146092307] + [-0.008775887943971985] * 84 + [-0.008654843146092307, -0.007744693927984771, -0.006201466102280098, -0.004443544633745687, -0.0028491136742709, -0.0016346887166827247, -0.0008392771714343294, -0.0003855856060807585, -0.00015851898170246266, -5.831587440376806e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0001241310711956625, 0.0003374232351783254, 0.0008207568661156978, 0.001786483961449053, 0.0034795956255125296, 0.006064618527311404, 0.009458521559216294, 0.013200430210986913, 0.016485342339326647, 0.018422684418935128] + [0.018680340170085043] * 84 + [0.018422684418935128, 0.016485342339326647, 0.013200430210986913, 0.009458521559216294, 0.006064618527311404, 0.0034795956255125296, 0.001786483961449053, 0.0008207568661156978, 0.0003374232351783254, 0.0001241310711956625],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [5.831587440376806e-05, 0.00015851898170246266, 0.0003855856060807585, 0.0008392771714343294, 0.0016346887166827247, 0.0028491136742709, 0.004443544633745687, 0.006201466102280098, 0.007744693927984771, 0.008654843146092307] + [0.008775887943971985] * 84 + [0.008654843146092307, 0.007744693927984771, 0.006201466102280098, 0.004443544633745687, 0.0028491136742709, 0.0016346887166827247, 0.0008392771714343294, 0.0003855856060807585, 0.00015851898170246266, 5.831587440376806e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-5.831587440376806e-05, -0.00015851898170246266, -0.0003855856060807585, -0.0008392771714343294, -0.0016346887166827247, -0.0028491136742709, -0.004443544633745687, -0.006201466102280098, -0.007744693927984771, -0.008654843146092307] + [-0.008775887943971985] * 84 + [-0.008654843146092307, -0.007744693927984771, -0.006201466102280098, -0.004443544633745687, -0.0028491136742709, -0.0016346887166827247, -0.0008392771714343294, -0.0003855856060807585, -0.00015851898170246266, -5.831587440376806e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003100814903685395, 0.0008428888806102992, 0.0020502643683321443, 0.004462666792043051, 0.008692088024746518, 0.015149518435244825, 0.023627544929034936, 0.032974895277240984, 0.04118066067243132, 0.04602017356483014] + [0.04666380193723544] * 32 + [0.04602017356483014, 0.04118066067243132, 0.032974895277240984, 0.023627544929034936, 0.015149518435244825, 0.008692088024746518, 0.004462666792043051, 0.0020502643683321443, 0.0008428888806102992, 0.0003100814903685395],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00015482992756182996, 0.0004208713785929527, 0.0010237382542704469, 0.0022282993264879933, 0.004340134451859872, 0.007564459391425662, 0.011797708613559749, 0.01646502872862917, 0.020562332505828746, 0.02297879867307429] + [0.02330017527042556] * 32 + [0.02297879867307429, 0.020562332505828746, 0.01646502872862917, 0.011797708613559749, 0.007564459391425662, 0.004340134451859872, 0.0022282993264879933, 0.0010237382542704469, 0.0004208713785929527, 0.00015482992756182996],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00015482992756182996, -0.0004208713785929527, -0.0010237382542704469, -0.0022282993264879933, -0.004340134451859872, -0.007564459391425662, -0.011797708613559749, -0.01646502872862917, -0.020562332505828746, -0.02297879867307429] + [-0.02330017527042556] * 32 + [-0.02297879867307429, -0.020562332505828746, -0.01646502872862917, -0.011797708613559749, -0.007564459391425662, -0.004340134451859872, -0.0022282993264879933, -0.0010237382542704469, -0.0004208713785929527, -0.00015482992756182996],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0003100814903685395, 0.0008428888806102992, 0.0020502643683321443, 0.004462666792043051, 0.008692088024746518, 0.015149518435244825, 0.023627544929034936, 0.032974895277240984, 0.04118066067243132, 0.04602017356483014] + [0.04666380193723544] * 32 + [0.04602017356483014, 0.04118066067243132, 0.032974895277240984, 0.023627544929034936, 0.015149518435244825, 0.008692088024746518, 0.004462666792043051, 0.0020502643683321443, 0.0008428888806102992, 0.0003100814903685395],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00015482992756182996, 0.0004208713785929527, 0.0010237382542704469, 0.0022282993264879933, 0.004340134451859872, 0.007564459391425662, 0.011797708613559749, 0.01646502872862917, 0.020562332505828746, 0.02297879867307429] + [0.02330017527042556] * 32 + [0.02297879867307429, 0.020562332505828746, 0.01646502872862917, 0.011797708613559749, 0.007564459391425662, 0.004340134451859872, 0.0022282993264879933, 0.0010237382542704469, 0.0004208713785929527, 0.00015482992756182996],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00015482992756182996, -0.0004208713785929527, -0.0010237382542704469, -0.0022282993264879933, -0.004340134451859872, -0.007564459391425662, -0.011797708613559749, -0.01646502872862917, -0.020562332505828746, -0.02297879867307429] + [-0.02330017527042556] * 32 + [-0.02297879867307429, -0.020562332505828746, -0.01646502872862917, -0.011797708613559749, -0.007564459391425662, -0.004340134451859872, -0.0022282993264879933, -0.0010237382542704469, -0.0004208713785929527, -0.00015482992756182996],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 84 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 84 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 84 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 84 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0012236318384043507, 0.003326176191058481, 0.008090675632574724, 0.017610406749669433, 0.034300388703150185, 0.05978245612734586, 0.09323812332085506, 0.1301242833982944, 0.16250556415161435, 0.18160306671608326] + [0.1841429286331537] * 84 + [0.18160306671608326, 0.16250556415161435, 0.1301242833982944, 0.09323812332085506, 0.05978245612734586, 0.034300388703150185, 0.017610406749669433, 0.008090675632574724, 0.003326176191058481, 0.0012236318384043507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 84 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 84 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 32 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 32 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 32 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 32 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 32 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 32 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "stark_wf": {
            "type": "constant",
            "sample": 0.0,
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
    },
    "integration_weights": {
        "integW_cos_rr1": {
            "cosine": [(-0.9740589738999803, 3040)],
            "sine": [(-0.22629431138435055, 3040)],
        },
        "integW_sin_rr1": {
            "cosine": [(0.22629431138435055, 3040)],
            "sine": [(-0.9740589738999803, 3040)],
        },
        "integW_minus_sin_rr1": {
            "cosine": [(-0.22629431138435055, 3040)],
            "sine": [(0.9740589738999803, 3040)],
        },
        "integW_cos_rr2": {
            "cosine": [(-0.31412402771819214, 10000)],
            "sine": [(0.9493819543313957, 10000)],
        },
        "integW_sin_rr2": {
            "cosine": [(-0.9493819543313957, 10000)],
            "sine": [(-0.31412402771819214, 10000)],
        },
        "integW_minus_sin_rr2": {
            "cosine": [(0.9493819543313957, 10000)],
            "sine": [(0.31412402771819214, 10000)],
        },
        "integW_cos_rr3": {
            "cosine": [(0.5459374486282426, 4000)],
            "sine": [(0.8378259378804676, 4000)],
        },
        "integW_sin_rr3": {
            "cosine": [(-0.8378259378804676, 4000)],
            "sine": [(0.5459374486282426, 4000)],
        },
        "integW_minus_sin_rr3": {
            "cosine": [(0.8378259378804676, 4000)],
            "sine": [(-0.5459374486282426, 4000)],
        },
        "integW_cos_rr4": {
            "cosine": [(-0.999764306047515, 3200)],
            "sine": [(0.021710190080485362, 3200)],
        },
        "integW_sin_rr4": {
            "cosine": [(-0.021710190080485362, 3200)],
            "sine": [(-0.999764306047515, 3200)],
        },
        "integW_minus_sin_rr4": {
            "cosine": [(0.021710190080485362, 3200)],
            "sine": [(0.999764306047515, 3200)],
        },
        "integW_cos_rr5": {
            "cosine": [(-0.9996569764968893, 1760)],
            "sine": [(0.026190252787966134, 1760)],
        },
        "integW_sin_rr5": {
            "cosine": [(-0.026190252787966134, 1760)],
            "sine": [(-0.9996569764968893, 1760)],
        },
        "integW_minus_sin_rr5": {
            "cosine": [(0.026190252787966134, 1760)],
            "sine": [(0.9996569764968893, 1760)],
        },
        "integW_cos_rr6": {
            "cosine": [(-0.2144083768151524, 1040)],
            "sine": [(-0.9767441056650875, 1040)],
        },
        "integW_sin_rr6": {
            "cosine": [(0.9767441056650875, 1040)],
            "sine": [(-0.2144083768151524, 1040)],
        },
        "integW_minus_sin_rr6": {
            "cosine": [(-0.9767441056650875, 1040)],
            "sine": [(0.2144083768151524, 1040)],
        },
        "integW_cos_rr7": {
            "cosine": [(0.8232967711436545, 4000)],
            "sine": [(-0.5676111579456776, 4000)],
        },
        "integW_sin_rr7": {
            "cosine": [(0.5676111579456776, 4000)],
            "sine": [(0.8232967711436545, 4000)],
        },
        "integW_minus_sin_rr7": {
            "cosine": [(-0.5676111579456776, 4000)],
            "sine": [(-0.8232967711436545, 4000)],
        },
        "integW_cos_rr8": {
            "cosine": [(0.8416630519706616, 2000)],
            "sine": [(-0.5400030619796812, 2000)],
        },
        "integW_sin_rr8": {
            "cosine": [(0.5400030619796812, 2000)],
            "sine": [(0.8416630519706616, 2000)],
        },
        "integW_minus_sin_rr8": {
            "cosine": [(-0.5400030619796812, 2000)],
            "sine": [(-0.8416630519706616, 2000)],
        },
    },
    "mixers": {
        "mixer_q1": [{'intermediate_frequency': 362155363.0, 'lo_frequency': 4700000000.0, 'correction': (1.0403961374441604, 0.08620365944377892, 0.09111386578534227, 0.9843282748001614)}],
        "mixer_rr1": [{'intermediate_frequency': -14273000.0, 'lo_frequency': 7399028000.0, 'correction': (1.6535896287305312, 0.2754312691549308, 0.5115152141448717, 0.8903944154702859)}],
        "mixer_q2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': (1.0137535772204032, -0.023556778310603196, -0.024164067010625925, 0.9882760327415352)}],
        "mixer_rr2": [{'intermediate_frequency': 14273000.0, 'lo_frequency': 7399028000.0, 'correction': (1.4325167632183953, 0.03306994338092208, 0.06141560913599801, 0.7713551801945223)}],
        "mixer_q3": [{'intermediate_frequency': 359962738.0, 'lo_frequency': 4700000000.0, 'correction': (1.0039990793637215, 0.042815700862599504, 0.0429226956450435, 1.001496378602361)}],
        "mixer_rr3": [{'intermediate_frequency': 52410500.0, 'lo_frequency': 7421703000.0, 'correction': (1.431804631737311, 0.02992665337714791, 0.05557807055756039, 0.7709717247816292)}],
        "mixer_q4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': (1.0193579031557578, 0.12486540584167889, 0.1240894560926829, 1.0257320991108114)}],
        "mixer_rr4": [{'intermediate_frequency': -52210500.0, 'lo_frequency': 7421703000.0, 'correction': (1.2882567049749953, 0.031353284497739886, 0.049251912255567694, 0.8200915888831498)}],
        "mixer_q5": [{'intermediate_frequency': -45252279.0, 'lo_frequency': 4700000000.0, 'correction': (0.9382861082818438, 0.037662667021408955, 0.03288392472810774, 1.0746392822395396)}],
        "mixer_rr5": [{'intermediate_frequency': 31068000.0, 'lo_frequency': 7365673000.0, 'correction': (0.9375057045439633, 0.043820895142713874, 0.03813999878401696, 1.0771457914081837)}],
        "mixer_q6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': (0.9390212711106408, 0.028444429315723052, 0.024919012889332414, 1.071869270692552)}],
        "mixer_rr6": [{'intermediate_frequency': -30938000.0, 'lo_frequency': 7365673000.0, 'correction': (1.1624594745793735, 0.15129870545135313, 0.1870056694732569, 0.9404988316071948)}],
        "mixer_q7": [{'intermediate_frequency': -136848020.0, 'lo_frequency': 4700000000.0, 'correction': (0.9531282230165004, 0.04084422885368196, 0.03684101032608277, 1.0566970591527876)}],
        "mixer_rr7": [{'intermediate_frequency': 20000000.0, 'lo_frequency': 7036398000.0, 'correction': (1.433221002403429, 0.035912548247809734, 0.06669473246021809, 0.7717343859095386)}],
        "mixer_q8": [{'intermediate_frequency': -140337100.0, 'lo_frequency': 4300000000.0, 'correction': (0.9501664441395031, 0.05850250509417677, 0.0521698803260484, 1.0655021037269372)}],
        "mixer_rr8": [{'intermediate_frequency': 20000000.0, 'lo_frequency': 7036398000.0, 'correction': (1.4323943156170444, 0.032550787359555716, 0.060451462239174865, 0.7712892468707166)}],
        "mixer_cr_c1t2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': (0.9994478269317117, 0.05799530611969734, 0.05735960529050436, 1.010524434050917)}],
        "mixer_cr_c1t4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': (1.0004610094040567, 0.05006488688367021, 0.0497401592685447, 1.006992498695352)}],
        "mixer_cr_c1t6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': (0.9985726912731867, 0.0443569355559235, 0.043972928556151814, 1.007293031623957)}],
        "mixer_cr_c3t2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': (1.0076884136821063, 0.03998122052115623, 0.040401894989739694, 0.9971961140503417)}],
        "mixer_cr_c3t4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': (1.0056392481876182, 0.03830960018530201, 0.038571790344144825, 0.9988034567486318)}],
        "mixer_cr_c3t6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': (1.0075217905279001, 0.039895832667472875, 0.04030322579213445, 0.9973375573222321)}],
        "mixer_cr_c5t2": [{'intermediate_frequency': 255421989.0, 'lo_frequency': 4700000000.0, 'correction': (0.9684553435373363, 0.0713975510023274, 0.06593422441851332, 1.048701799308168)}],
        "mixer_cr_c5t4": [{'intermediate_frequency': 298673853.0, 'lo_frequency': 4700000000.0, 'correction': (0.9634597757129584, 0.072616433625605, 0.06631787837323827, 1.054964582254082)}],
        "mixer_cr_c5t6": [{'intermediate_frequency': 319918280.0, 'lo_frequency': 4700000000.0, 'correction': (0.9691754975480648, 0.0701122327240297, 0.06487874415554874, 1.0473547063673503)}],
        "mixer_q12_1": [{'intermediate_frequency': -11320000.0, 'lo_frequency': 4700000000.0, 'correction': (0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035)}],
        "mixer_q12_2": [{'intermediate_frequency': -114664284.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_3": [{'intermediate_frequency': -8168081.000000001, 'lo_frequency': 4700000000.0, 'correction': (1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166)}],
        "mixer_q12_4": [{'intermediate_frequency': 30572017.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_5": [{'intermediate_frequency': -323684090.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_6": [{'intermediate_frequency': -48785066.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_7": [{'intermediate_frequency': -204595000.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_8": [{'intermediate_frequency': -204595000.0, 'lo_frequency': 4300000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_1": [{'intermediate_frequency': 402155363.0, 'lo_frequency': 4700000000.0, 'correction': (0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035)}],
        "mixer_stark_2": [{'intermediate_frequency': 295421989.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_3": [{'intermediate_frequency': 399962738.0, 'lo_frequency': 4700000000.0, 'correction': (1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166)}],
        "mixer_stark_4": [{'intermediate_frequency': 338673853.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_5": [{'intermediate_frequency': -5252279.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_6": [{'intermediate_frequency': 359918280.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_7": [{'intermediate_frequency': -96848020.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_8": [{'intermediate_frequency': -100337100.0, 'lo_frequency': 4300000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
    },
}


