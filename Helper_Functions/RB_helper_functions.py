from qm.qua import *
import numpy as np
from Helper_Functions.macros import *

cayley_table = np.int_(np.genfromtxt('../Configuration_Files/Resources/c1_cayley_table.csv', delimiter=','))[1:, 1:]
inv_gates = [int(np.where(cayley_table[i, :] == 0)[0][0]) for i in range(24)]

def generate_sequence(max_circuit_depth, seed):

    cayley = declare(int, value=cayley_table.flatten().tolist())
    inv_list = declare(int, value=inv_gates)
    current_state = declare(int)
    step = declare(int)
    sequence = declare(int, size=max_circuit_depth+1)
    inv_gate = declare(int, size=max_circuit_depth+1)
    i = declare(int)
    rand = Random(seed=seed)

    assign(current_state, 0)
    with for_(i, 0, i < max_circuit_depth, i+1):
        assign(step, rand.rand_int(24))
        assign(current_state, cayley[current_state*24+step])
        assign(sequence[i], step)
        assign(inv_gate[i], inv_list[current_state])

    return sequence, inv_gate


def power_law(m, a, b, p):
    return a * (p ** m) + b

def play_sequence_BB_flg(qe, sequence_list, depth, BB_flg):
    i = declare(int)
    with for_(i, 0, i <= depth, i+1):

        with switch_(sequence_list[i], unsafe=True):
            # print(sequence_list[i])
            with case_(0):
                play('I', qe)
            with case_(1):
                # play_cmd('X180', qe, BB_flg)
                BB1_X180(qe)
            with case_(2):
                # play_cmd('Y180', qe, BB_flg)
                # BB1_Y180(qe)
                play_Y180(qe)
            with case_(3):
                # play_cmd('Y180', qe, BB_flg)
                # BB1_Y180(qe)
                play_Y180(qe)
                # play_cmd('X180', qe, BB_flg)
                BB1_X180(qe)
            with case_(4):
                # play_cmd('X90', qe, BB_flg)
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                BB1_X90(qe)
                play_Y90(qe)
            with case_(5):
                # play_cmd('X90', qe, BB_flg)
                # play_cmd('mY90', qe, BB_flg)
                # BB1_mY90(qe)
                BB1_X90(qe)
                play_mY90(qe)
            with case_(6):
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                play_Y90(qe)
            with case_(7):
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
                # play_cmd('mY90', qe, BB_flg)
                # BB1_mY90(qe)
                play_mY90(qe)
            with case_(8):
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                play_Y90(qe)
                # play_cmd('X90', qe, BB_flg)
                BB1_X90(qe)
            with case_(9):
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                play_Y90(qe)
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
            with case_(10):
                # play_cmd('mY90', qe, BB_flg)
                # BB1_mY90(qe)
                play_mY90(qe)
                # play_cmd('X90', qe, BB_flg)
                BB1_X90(qe)
            with case_(11):
                # play_cmd('mY90', qe, BB_flg)
                # BB1_mY90(qe)
                play_mY90(qe)
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
            with case_(12):
                # play_cmd('X90', qe, BB_flg)
                BB1_X90(qe)
            with case_(13):
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
            with case_(14):
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                play_Y90(qe)
            with case_(15):
                # play_cmd('mY90', qe, BB_flg)
                # BB1_mY90(qe)
                play_mY90(qe)
            with case_(16):
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                play_Y90(qe)
                # play_cmd('X90', qe, BB_flg)
                BB1_X90(qe)
            with case_(17):
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
                # play_cmd('mY90', qe, BB_flg)
                # BB1_mY90(qe)
                play_mY90(qe)
                # play_cmd('X90', qe, BB_flg)
                BB1_X90(qe)
            with case_(18):
                # play_cmd('X180', qe, BB_flg)
                BB1_X180(qe)
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                play_Y90(qe)
            with case_(19):
                # play_cmd('X180', qe, BB_flg)
                BB1_X180(qe)
                # play_cmd('mY90', qe, BB_flg)
                # BB1_mY90(qe)
                play_mY90(qe)
            with case_(20):
                # play_cmd('Y180', qe, BB_flg)
                # BB1_Y180(qe)
                play_Y180(qe)
                # play_cmd('X90', qe, BB_flg)
                BB1_X90(qe)
            with case_(21):
                # play_cmd('Y180', qe, BB_flg)
                # BB1_Y180(qe)
                play_Y180(qe)
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
            with case_(22):
                # play_cmd('X90', qe, BB_flg)
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                BB1_X90(qe)
                play_Y90(qe)
                # play_cmd('X90', qe, BB_flg)
                BB1_X90(qe)
            with case_(23):
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)
                # play_cmd('Y90', qe, BB_flg)
                # BB1_Y90(qe)
                play_Y90(qe)
                # play_cmd('mX90', qe, BB_flg)
                BB1_mX90(qe)

def play_sequence_KNILL(qe, sequence_list, depth, BB_flg):
    i = declare(int)
    with for_(i, 0, i <= depth, i+1):

        with switch_(sequence_list[i], unsafe=True):
            with case_(0):
                play('I', qe)
            with case_(1):
                KNILL_X180(qe)
            with case_(2):
                play_Y180(qe)
            with case_(3):
                play_Y180(qe)
                KNILL_X180(qe)
            with case_(4):
                play_X90(qe)#BB1_X90(qe)
                play_Y90(qe)
            with case_(5):
                play_X90(qe)#BB1_X90(qe)
                play_mY90(qe)
            with case_(6):
                play_mX90(qe)#BB1_mX90(qe)
                play_Y90(qe)
            with case_(7):
                play_mX90(qe)#BB1_mX90(qe)
                play_mY90(qe)
            with case_(8):
                play_Y90(qe)
                play_X90(qe)#BB1_X90(qe)
            with case_(9):
                play_Y90(qe)
                play_mX90(qe)#BB1_mX90(qe)
            with case_(10):
                play_mY90(qe)
                play_X90(qe)#BB1_X90(qe)
            with case_(11):
                play_mY90(qe)
                play_mX90(qe)#BB1_mX90(qe)
            with case_(12):
                play_X90(qe)#BB1_X90(qe)
            with case_(13):
                play_mX90(qe)#BB1_mX90(qe)
            with case_(14):
                play_Y90(qe)
            with case_(15):
                play_mY90(qe)
            with case_(16):
                play_mX90(qe)#BB1_mX90(qe)
                play_Y90(qe)
                play_X90(qe)#BB1_X90(qe)
            with case_(17):
                play_mX90(qe)#BB1_mX90(qe)
                play_mY90(qe)
                play_X90(qe)#BB1_X90(qe)
            with case_(18):
                KNILL_X180(qe)
                play_Y90(qe)
            with case_(19):
                KNILL_X180(qe)
                play_mY90(qe)
            with case_(20):
                play_Y180(qe)
                play_X90(qe)#BB1_X90(qe)
            with case_(21):
                play_Y180(qe)
                play_mX90(qe)#BB1_mX90(qe)
            with case_(22):
                play_X90(qe)#BB1_X90(qe)
                play_Y90(qe)
                play_X90(qe)#BB1_X90(qe)
            with case_(23):
                play_mX90(qe)#BB1_mX90(qe)
                play_Y90(qe)
                play_mX90(qe)#BB1_mX90(qe)

def play_sequence_UCP5b(qe, sequence_list, depth, BB_flg):
    i = declare(int)
    with for_(i, 0, i <= depth, i+1):

        with switch_(sequence_list[i], unsafe=True):
            with case_(0):
                play('I', qe)
            with case_(1):
                UCP5b_X180(qe)
            with case_(2):
                UCP5b_Y180(qe)
            with case_(3):
                UCP5b_Y180(qe)
                UCP5b_X180(qe)
            with case_(4):
                play("d_X90", qe)
                play("d_Y90", qe)
            with case_(5):
                play("d_X90", qe)#BB1_X90(qe)
                play("d_mY90", qe)
            with case_(6):
                play("d_mX90", qe)#BB1_mX90(qe)
                play("d_Y90", qe)
            with case_(7):
                play("d_mX90", qe)#BB1_mX90(qe)
                play("d_mY90", qe)
            with case_(8):
                play("d_Y90", qe)
                play("d_X90", qe)#BB1_X90(qe)
            with case_(9):
                play("d_Y90", qe)
                play("d_mX90", qe)#BB1_mX90(qe)
            with case_(10):
                play("d_mY90", qe)
                play("d_X90", qe)#BB1_X90(qe)
            with case_(11):
                play("d_mY90", qe)
                play("d_mX90", qe)#BB1_mX90(qe)
            with case_(12):
                play("d_X90", qe)#BB1_X90(qe)
            with case_(13):
                play("d_mX90", qe)#BB1_mX90(qe)
            with case_(14):
                play("d_Y90", qe)
            with case_(15):
                play("d_mY90", qe)
            with case_(16):
                play("d_mX90", qe)#BB1_mX90(qe)
                play("d_Y90", qe)
                play("d_X90", qe)#BB1_X90(qe)
            with case_(17):
                play("d_mX90", qe)#BB1_mX90(qe)
                play("d_mY90", qe)
                play("d_X90", qe)#BB1_X90(qe)
            with case_(18):
                UCP5b_X180(qe)
                play("d_Y90", qe)
            with case_(19):
                UCP5b_X180(qe)
                play("d_mY90", qe)
            with case_(20):
                UCP5b_Y180(qe)
                play("d_X90", qe)#BB1_X90(qe)
            with case_(21):
                UCP5b_Y180(qe)
                play("d_mX90", qe)#BB1_mX90(qe)
            with case_(22):
                play("d_X90", qe)#BB1_X90(qe)
                play("d_Y90", qe)
                play("d_X90", qe)#BB1_X90(qe)
            with case_(23):
                play("d_mX90", qe)#BB1_mX90(qe)
                play("d_Y90", qe)
                play("d_mX90", qe)#BB1_mX90(qe)

def play_sequence_UCP5b_CPMG(qe, sequence_list, depth, BB_flg):
    i = declare(int)
    with for_(i, 0, i <= depth, i+1):

        with switch_(sequence_list[i], unsafe=True):
            with case_(0):
                play('I', qe)
            with case_(1):
                UCP5b_X180(qe)
            with case_(2):
                UCP5b_Y180(qe)
            with case_(3):
                UCP5b_Y180(qe)
                UCP5b_X180(qe)
            with case_(4):
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
                CPMG_90("Y90", qe)# play_Y90(qe)
            with case_(5):
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
                CPMG_90("mY90", qe)# play_mY90(qe)
            with case_(6):
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
                CPMG_90("Y90", qe)# play_Y90(qe)
            with case_(7):
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
                CPMG_90("mY90", qe)# play_mY90(qe)
            with case_(8):
                CPMG_90("Y90", qe)# play_Y90(qe)
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
            with case_(9):
                CPMG_90("Y90", qe)# play_Y90(qe)
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
            with case_(10):
                CPMG_90("mY90", qe)# play_mY90(qe)
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
            with case_(11):
                CPMG_90("mY90", qe)# play_mY90(qe)
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
            with case_(12):
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
            with case_(13):
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
            with case_(14):
                CPMG_90("Y90", qe)# play_Y90(qe)
            with case_(15):
                CPMG_90("mY90", qe)# play_mY90(qe)
            with case_(16):
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
                CPMG_90("Y90", qe)# play_Y90(qe)
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
            with case_(17):
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
                CPMG_90("mY90", qe)# play_mY90(qe)
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
            with case_(18):
                UCP5b_X180(qe)
                CPMG_90("Y90", qe)# play_Y90(qe)
            with case_(19):
                UCP5b_X180(qe)
                CPMG_90("mY90", qe)# play_mY90(qe)
            with case_(20):
                UCP5b_Y180(qe)
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
            with case_(21):
                UCP5b_Y180(qe)
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
            with case_(22):
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
                CPMG_90("Y90", qe)# play_Y90(qe)
                CPMG_90("X90", qe)# play_X90(qe)#BB1_X90(qe)
            with case_(23):
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
                CPMG_90("Y90", qe)# play_Y90(qe)
                CPMG_90("mX90", qe)# play_mX90(qe)#BB1_mX90(qe)
def play_sequence(qe, sequence_list, depth):
    i = declare(int)
    with for_(i, 0, i <= depth, i+1):

        with switch_(sequence_list[i], unsafe=True):

            with case_(0):
                play('I', qe)
            with case_(1):
                play_X180(qe)
            with case_(2):
                play_Y180(qe)
            with case_(3):
                play_Y180(qe)
                play_X180(qe)
            with case_(4):
                play_X90(qe)
                play_Y90(qe)
            with case_(5):
                play_X90(qe)
                play_mY90(qe)
            with case_(6):
                play_mX90(qe)
                play_Y90(qe)
            with case_(7):
                play_mX90(qe)
                play_mY90(qe)
            with case_(8):
                play_Y90(qe)
                play_X90(qe)
            with case_(9):
                play_Y90(qe)
                play_mX90(qe)
            with case_(10):
                play_mY90(qe)
                play_X90(qe)
            with case_(11):
                play_mY90(qe)
                play_mX90(qe)
            with case_(12):
                play_X90(qe)
            with case_(13):
                play_mX90(qe)
            with case_(14):
                play_Y90(qe)
            with case_(15):
                play_mY90(qe)
            with case_(16):
                play_mX90(qe)
                play_Y90(qe)
                play_X90(qe)
            with case_(17):
                play_mX90(qe)
                play_mY90(qe)
                play_X90(qe)
            with case_(18):
                play_X180(qe)
                play_Y90(qe)
            with case_(19):
                play_X180(qe)
                play_mY90(qe)
            with case_(20):
                play_Y180(qe)
                play_X90(qe)
            with case_(21):
                play_Y180(qe)
                play_mX90(qe)
            with case_(22):
                play_X90(qe)
                play_Y90(qe)
                play_X90(qe)
            with case_(23):
                play_mX90(qe)
                play_Y90(qe)
                play_mX90(qe)

def play_sequence_drag(qe, sequence_list, depth):
    i = declare(int)
    with for_(i, 0, i <= depth, i+1):

        with switch_(sequence_list[i], unsafe=True):

            with case_(0):
                play('I', qe)
            with case_(1):
                play('d_X180', qe)
            with case_(2):
                play('d_Y180', qe)
            with case_(3):
                play('d_Y180', qe)
                play('d_X180', qe)
            with case_(4):
                play('d_X90', qe)
                play('d_Y90', qe)
            with case_(5):
                play('d_X90', qe)
                play('d_mY90', qe)
            with case_(6):
                play('d_mX90', qe)
                play('d_Y90', qe)
            with case_(7):
                play('d_mX90', qe)
                play('d_mY90', qe)
            with case_(8):
                play('d_Y90', qe)
                play('d_X90', qe)
            with case_(9):
                play('d_Y90', qe)
                play('d_mX90', qe)
            with case_(10):
                play('d_mY90', qe)
                play('d_X90', qe)
            with case_(11):
                play('d_mY90', qe)
                play('d_mX90', qe)
            with case_(12):
                play('d_X90', qe)
            with case_(13):
                play('d_mX90', qe)
            with case_(14):
                play('d_Y90', qe)
            with case_(15):
                play('d_mY90', qe)
            with case_(16):
                play('d_mX90', qe)
                play('d_Y90', qe)
                play('d_X90', qe)
            with case_(17):
                play('d_mX90', qe)
                play('d_mY90', qe)
                play('d_X90', qe)
            with case_(18):
                play('d_X180', qe)
                play('d_Y90', qe)
            with case_(19):
                play('d_X180', qe)
                play('d_mY90', qe)
            with case_(20):
                play('d_Y180', qe)
                play('d_X90', qe)
            with case_(21):
                play('d_Y180', qe)
                play('d_mX90', qe)
            with case_(22):
                play('d_X90', qe)
                play('d_Y90', qe)
                play('d_X90', qe)
            with case_(23):
                play('d_mX90', qe)
                play('d_Y90', qe)
                play('d_mX90', qe)
