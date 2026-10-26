# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""     sadfasdf
Created on Sun Dec 25 17:41:47 2022

@author: gautham
"""
import numpy as np
import qutip as qt
import time
#import rk9f
#from rk9f_gpu import qt.sesolve
import scipy.linalg as lin
import scipy.special
import scipy as sp
import sympy as sym
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
#import tabulate
from tabulate import tabulate
import pickle
from tqdm import tqdm
import scipy.linalg as la
from scipy.linalg import block_diag
from scipy.linalg import fractional_matrix_power
from joblib import Parallel, delayed



def check_resonance(pr,tol,dressed = False):
    '''This function takes the qubit dictionary and the coupling matrix and a tolerance (in Grad/s).
       It checks if the spread in frequency space is too close to any pole.
    '''
    wkey = 'w'
    if dressed:
        wkey = 'w_dressed'
    for i in range(pr.N):
        for j in range(pr.N):
            if i == j:
                continue
            if pr.J[i][j]!=0 and np.abs(pr.qubits[i][wkey]-pr.qubits[j][wkey])<tol:
                  print("Coupled qubits {}, {} are too close in frequency".format(i,j))
            if pr.control_target[i][j]!=0 and np.abs((pr.qubits[i][wkey]-pr.qubits[j][wkey]) - pr.qubits[i]['a']/2)<tol:
                print("Control {}, Target {} are too close to pole -anh_c/2".format(i,j))
            if pr.J[i][j]!=0 and np.abs((pr.qubits[i][wkey]-pr.qubits[j][wkey]) - pr.qubits[i]['a'])<tol:
                print("Coupled qubits {}, {} are too close to pole -anh_{}".format(i,j,i))
            if pr.control_target[i][j]!=0 and (pr.qubits[i][wkey]-pr.qubits[j][wkey] - pr.qubits[i]['a'])>tol:
                print("Control {}, Target {} are beyond pole -anh_{}.Gates will be slow".format(i,j,i))
            if pr.control_target[i][j]!=0 and np.abs(pr.qubits[i][wkey]-pr.qubits[j][wkey] + pr.qubits[j]['a'])<tol:
                print("Control {}, Target {} are too close to pole anh_t".format(i,j))
            for k in range(pr.N):
                if i==k or j==k:
                    continue
                if pr.control_target[j][i]!=0 and pr.control_target[j][k]!=0:
                    print("inside. j = {}, i = {}, k = {}".format(j,i,k))
                    if np.abs(pr.qubits[i][wkey]-pr.qubits[k][wkey])<tol:
                        print("Targets {},{} sharing control {} are too close in frequency".format(i,k,j))
                    if np.abs(pr.qubits[i][wkey]- pr.qubits[k][wkey] + pr.qubits[k]['a'])<tol or np.abs(pr.qubits[i][wkey]-pr.qubits[k][wkey] + pr.qubits[i]['a'])<tol:
                        print("Targets {},{} sharing control {} are too close to poles del_{},{} = anh_{} or del_{},{} =-anh_{}".format(i,k,j,i,k,k,i,k,i))
                if pr.J[i][j]!=0 and pr.control_target[j][k]!=0:
                    if np.abs(pr.qubits[i][wkey] + pr.qubits[k][wkey]- 2*pr.qubits[j][wkey] + pr.qubits[j]['a'])<tol:
                        print("Qubit {}, connected with control {} and target {} is close to del_{},{} + del_{},{} = anh_{}".format(i,j,k,i,j,k,j,j))



def region_classifier(pr,dressed = False):
    key = 'w'
    if dressed:
        key = 'w_dressed'
    rows = [['Ctrl\Tgt'] + list(range(0,pr.N))]
    for i in range(pr.N):
        row = [i]
        for j in range(pr.N):
            region = '-'
            if pr.control_target[i][j]!=0:
                del_ct = pr.qubits[i][key] - pr.qubits[j][key]
                if del_ct<-pr.qubits[j]['a']:
                    region = 0
                elif -pr.qubits[j]['a']<del_ct<0:
                    region = 1
                elif 0<del_ct<pr.qubits[i]['a']/2:
                    region = 2
                elif pr.qubits[i]['a']/2<del_ct<pr.qubits[i]['a']:
                    region = 3
                elif pr.qubits[i]['a']<del_ct<3*pr.qubits[i]['a']/2:
                    region = 4
                elif 3*pr.qubits[i]['a']/2<del_ct<2*pr.qubits[i]['a']:
                    region = 5
                else:
                    region = 6
            row.append(region)
        rows.append(row)
    print(tabulate(rows,tablefmt = 'grid'))


def pulse_envelope(t,Emax,tp,rf):
    tr = rf*tp

    if 0<=t<tr:
        return (1 - np.cos(np.pi*t/tr))*0.5*Emax
    elif tr<=t<=tp-tr:
        return Emax
    elif tp-tr<=t<=tp:
        return 0.5*(1 - np.cos(np.pi*(tp - t)/tr))*Emax
    else:
        return 0

def pulse_coeff(t,args):
    Emax = args['Emax']
    tp = args['tp']
    rf = args['rf']
    tr = rf*tp
    if 0<=t<tr:
        return (1 - np.cos(np.pi*t/tr))*0.5*Emax
    elif tr<=t<=tp-tr:
        return Emax
    elif tp-tr<=t<=tp:
        return 0.5*(1 - np.cos(np.pi*(tp - t)/tr))*Emax
    else:
        return 0

def pulse_coeff_dag(t,args):
    Emax = np.conjugate(args['Emax'])
    tp = args['tp']
    rf = args['rf']
    tr = rf*tp
    if 0<=t<tr:
        return (1 - np.cos(np.pi*t/tr))*0.5*Emax
    elif tr<=t<=tp-tr:
        return Emax
    elif tp-tr<=t<=tp:
        return 0.5*(1 - np.cos(np.pi*(tp - t)/tr))*Emax
    else:
        return 0



class processor:
    '''
        Main class. Creates an object with arbitrary number of transmon qubits and coupling

        Parameters
        ----------
            N: int
                Number of qubits
            N_l: int
                Number of levels in each qubit
            w: numpy 1D array of floats
                Frequencies of qubits in Grad/s
            anh: numpy 1D array of floats
                Anharmonicities of qubits in Grad/s
            J: numpy 2D array of floats
                J[i][j] specifies coupling between qubit 'i' and qubit 'j' in Grad/s
            control_target: numpy 2D array
                control_target[i][j] = 1 if qubit 'i' is the control for qubit 'j'. Else 0

        Attributes
        ----------
            N:
                Number of qubits
            N_l:
                Number of levels per qubit
            J:
                Coupling matrix of processor J[i][j] = coupling between qubit 'i' and qubit 'j' in Grad/s
            control_target:
                Matrix specifying controls and targets. control_target[i][j] = 1 if qubit 'i' is the control for qubit 'j'. Else 0
            drive_w:
                Drive Frequency (Calculations are performed in this frame)
            qubits:
                Dictionary containing parameters of qubits
                Key - Value pairs:
                integer index - dictionary of parameters of that particular qubit
                Example:
                qubits[0]['w'] = frequency of qubit 0 (Grad/s)
                qubits[1]['a'] = anharmonicity of qubit 1 (Grad/s)
                qubits[5]['cp'] = list of qubits to which qubit 5 is coupled
                qubits[0]['w_kerr'] = dictionary with all kerr transition energies (Grad/s)
                    qubits[0]['w_kerr']['00->10'] = Transition energywhen second qubit is in state |0>
                qubits[0]['w_dressed'] = dressed frequency of qubit (Grad/s)
                qubits[0]['w_mean_kerr'] = mean of all Kerr frequencies of this qubit
                qubits[0]['w_dev_kerr'] = deviation of Kerr frequencies from mean

            H_bare:
                Qubit Hamiltonian with only Qubit (Duffing Oscillator) terms
            H_g:
                Coupling Hamiltonian with only coupling (photon exchange) terms
            H_c:
                Processor Hamiltonian = H_g + H_bare
            a_ops:
                Dictionary of annihilation operators a_ops[i] = annihiltion operator of qubit 'i'
            ex_ops, ey_ops, ez_ops:
                Dictionary of Effective Pauli Operators (when projected to computational subspace)
                These are similar to a_ops. ex_ops[i] = X operator of qubit 'i', when projected to computational subspace

        Note: Excitation restriction has not been implemented yet
    '''
    # Initialization Functions

    def __init__(self,N,N_l,w,anh,J,control_target):
        '''
            Constructor of processor class
        '''

        # Create fundamental attributes
        self.N = N
        self.N_l = N_l

        # Create coupling attributes
        self.J = J
        self.control_target = control_target

        # Create Qubit dictionary
        self.create_qubits(w,anh,J)

        # Set rotating frame's Angular frequency
        self.w_frame = 0

        # Create Processor Hamiltonian in Lab Frame
        self.create_H_pr(self.w_frame)

        # Find dressed frequencies and Kerr frequencies of each qubit
        self.find_dressed()

        # Enable/Disable progress bars in various stages of simulation
        self.schrodinger_progress_bar = None # For Schrodinger Time Evolution
        self.progress_bar = None # For other long computations

        # Other flag variables for convenience
        self.save_M = False # For saving propagator for large systems
        self.full_rank_choice = 0 # For choosing which subset is to be used for  phase estimation
        self.propagator_path = None # Path to save propagator

    def create_qubits(self,w,anh,J):
        '''
            Method to create the qubit dictionary.
            Arguments
            ---------
                w: numpy 1D array
                    Frequencies of qubits in Grad/s
                anh: numpy 1D array
                    Anharmonicities of qubits in Grad/s
                J: numpy 2D array
                    Coupling between qubits. J[i][j] = Coupling between qubit 'i' and qubit 'j' in Grad/s

            Returns
            -------
                None
        '''
        # Create qubit dictionary
        self.qubits = {}
        for i in range(self.N):
            self.qubits[i] = {}
            self.qubits[i]['w'] = w[i] # Set Frequency
            self.qubits[i]['a'] = anh[i] # Set anharmonicity
            self.qubits[i]['cp'] = [] # List of qubits to which this qubit is coupled

        # Populate list of qubits to which each qubit is coupled
        for i in range(self.N):
            for j in range(self.N):
                if self.J[i][j]!=0:
                    self.qubits[i]['cp'].append(j)


    '''########################## Hamiltonian Functions ########################################'''

    def create_H_pr(self,w_frame):
        '''
            Creates Processor's Hamiltonian (without drive Hamiltonian)
            This is based on existing parameters in qubits and J

            Arguments
            ---------
                w_frame: float
                    Angular Frequency (Grad/s) of the rotating frame in which we want the Hamiltonian

            Returns
            -------
                None
        '''

        # Create Hamiltonian

        # Coupling Terms
        self.H_g = qt.tensor([qt.qeye(self.N_l) for i in range(self.N)])*0

        # Bare Terms
        self.H_bare = qt.tensor([qt.qeye(self.N_l) for i in range(self.N)])*0

        # Annihilation Operators
        self.a_ops = {}

        # Effective Pauli Operators (when projected to computational subspace)
        ex_ops = {}
        ey_ops = {}
        ez_ops = {}

        for i in range(self.N):

            # Define tensor structure of annihilation operators
            ai = qt.tensor([qt.qeye(self.N_l) if k!=i else qt.destroy(self.N_l) for k in range(self.N)])
            self.a_ops[i] = ai

            # Define effective pauli operators
            ez_ops[i] = 1 - 2*(ai.dag()*ai)
            ex_ops[i] = (ai.dag()+ai)
            ey_ops[i] = ((ai.dag() - ai)/(1j))

            # Create Linear Oscillator Terms
            self.H_bare += self.qubits[i]['w']*ai.dag()*ai

            # Create Duffing Oscillator Terms, assuming Kerr Approximation
            self.H_bare -=0.5*self.qubits[i]['a']*(ai.dag()*ai*ai.dag()*ai - ai.dag()*ai)

            # Shift to drive's rotating frame
            self.H_bare -= w_frame*ai.dag()*ai

            # Create Coupling Terms
            for j in range(i):
                # Add coupling terms only if J[i][j] matrix is non zero
                aj = qt.tensor([qt.qeye(self.N_l) if k!=j else qt.destroy(self.N_l) for k in range(self.N)])
                self.H_g += self.J[i][j]*(ai.dag()*aj + ai*aj.dag())

        # Attribute containing the entire processor's Hamiltonian
        self.H_c = self.H_bare + self.H_g

    def create_He(self,ctrl):
        '''
            Creates the Drive Operators given the control qubit (Qubit that is to be driven)

            Arguments
            ---------
                ctrl: int
                    Index of the control qubit (0....N-1)

            Returns
            -------
                None
        '''
        self.He = self.a_ops[ctrl]
        self.He_dag = self.a_ops[ctrl].dag()

    def create_H_total(self,ctrl,tgt,drive_frequency, pulse_shape, t, args = None):
        '''
            Creates the drive Hamiltonian based on the drive frequency,
            Redefines the processor Hamiltonian in this drive's rotating frame
            Then, transforms all the Hamiltonians to the dressed basis.

            Arguments
            ---------
                ctrl, tgt: int
                    Indices of the Control and Target Qubit (0....N-1). Set ctrl = tgt for single qubit gates
                drive_frequency: float
                    Angular frequency of the drive, in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and gives pulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args: dict
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default - None

            Returns
            -------
                None
        '''
        # Set the frame frequency
        self.w_frame = drive_frequency

        # Create the relevant Hamiltonians
        self.create_H_pr(self.w_frame)
        self.create_He(ctrl)

        # Diagonalize the Processor Hamiltonian
        #Ec_scipy = sp.linalg.eig(np.array(self.H_c, dtype = complex))
        Ec_scipy = sp.linalg.eig(np.array(self.H_c.full(), dtype = complex))



        # Map the states to do proper transform
        state_map_scipy = {}
        for index,i in enumerate(Ec_scipy[1]):
            ind_scipy = np.argmax(np.abs(Ec_scipy[1][:,index]))
            state_map_scipy[ind_scipy] = index

        # Create the Unitary matrix to transform to dressed basis
        U_dressed_scipy = np.zeros((self.N_l**self.N,self.N_l**self.N),dtype = complex)

        for i in range(self.N_l**self.N):
            U_dressed_scipy[:,i] = Ec_scipy[1][:,state_map_scipy[i]]

        # Convert to qutip Qobj for convenience
        # U_dressed_scipy = qt.Qobj(U_dressed_scipy,dims = [[self.N_l]*self.N,[self.N_l]*self.N], shape = (self.N_l**self.N,self.N_l**self.N))
        U_dressed_scipy = qt.Qobj(U_dressed_scipy,dims = [[self.N_l]*self.N,[self.N_l]*self.N])

        U_dressed_scipy = U_dressed_scipy.dag()

        # Transform all Hamiltonians dressed basis
        self.H_c = self.H_c.transform(U_dressed_scipy)
        self.He = self.He.transform(U_dressed_scipy)
        self.He_dag = self.He_dag.transform(U_dressed_scipy)
        self.H_bare = self.H_bare.transform(U_dressed_scipy)
        self.H_g = self.H_bare.transform(U_dressed_scipy)

        # Create pulse functions and arrays
        def pulse_shape_dag(t,args):
            '''
                Function to return the complex conjugate of pulse shape for given args
            '''
            return np.conjugate(pulse_shape(t,args))
        self.t = t
        self.args = args

        self.pulse_shape = pulse_shape
        self.pulse_shape_dag = pulse_shape_dag

        # Create Hamiltonian to be fed to QuTiP's Schrodinger Solver
        self.H =[self.H_c,[self.He,self.pulse_shape],[self.He_dag,self.pulse_shape_dag]]

    def H_of_t(self,t,return_Qobj = False):
        '''
            Returns a numpy array containing the Hamiltonian at time 't'

            Arguments
            ---------
                t: float
                    Time at which Hamiltonian is to be found
                return_Qobj: Bool
                    Bool to choose return type. Returns Qobj if True, else returns np array
                    Default - False

            Returns
            -------
                H: numpy 2D array, complex (if return_Qobj is False)
                    Hamiltonian at time 't'
                H: qutip.Qobj (if return_Qobj is True)
                    Hamiltonian at time 't'
        '''
        H = self.H_c + self.pulse_shape(t,self.args)*self.He +self.pulse_shape_dag(t,self.args)*self.He_dag
        if return_Qobj:
            return H
        else:
            return np.array(H, dtype = complex)
        return H

    def find_dressed(self):
        '''
            Finds all computational subspace transition frequencies for the
            processor Hamiltonian and populates qubit dictionary with these values

            Arguments
            ---------
                None

            Returns
            -------
                None
        '''

        # Find eigen states of processor Hamiltonian
        E_val, E_vec = lin.eigh(np.array(self.H_c.full(), dtype = complex))
        E_vec = [list(i) for i in E_vec.T]
        E_c = [E_val,E_vec]

        # Map states to appropriate energies
        ind_Ec = {}
        for i in range(len(E_c[1])):
            ind = np.argmax(np.abs(np.array(E_c[1][i])))
            ind_Ec[ind] = E_c[0][i]
        self.ind_Ec = ind_Ec

        # Populate Qubit Dictionary with Appropriate Parameters
        for i in range(self.N):
            self.qubits[i]['w_kerr'] = {} # Dictionary Containing 2**(N-1) Transition Frequencies

            # Run through 2**(N-1) states for each qubit and store transitions
            for j in range(2**(self.N-1)):
                str_bin_j = bin(j).split('0b')[1]
                str_bin_j = '0'*(self.N-len(str_bin_j)-1) + str_bin_j
                bin_j_low = str_bin_j[0:i] + '0' + str_bin_j[i:] #Lower Energy State
                bin_j_high = str_bin_j[0:i] + '1' + str_bin_j[i:]#Higher Energy State
                # Corresponding Lower Index
                low_ind = sum([self.N_l**(self.N-1-k) if bin_j_low[k] == '1' else 0 for k in range(self.N)])
                # Corresponding Higher Index
                high_ind = sum([self.N_l**(self.N-1-k) if bin_j_high[k] == '1' else 0 for k in range(self.N)])
                # Store Transition Frequency
                self.qubits[i]['w_kerr'][bin_j_low + '->' + bin_j_high] = (ind_Ec[high_ind] - ind_Ec[low_ind])
                if j == 0:
                    self.qubits[i]['w_dressed'] = ind_Ec[high_ind] -ind_Ec[low_ind]
        # Store Mean Frequency and Deviation in Frequency
        for i in range(self.N):
            self.qubits[i]['w_mean_kerr'] = np.mean(list(self.qubits[i]['w_kerr'].values()))
            self.qubits[i]['w_dev_kerr'] = np.std(list(self.qubits[i]['w_kerr'].values()))


    '''########################## Propagator Functions #########################################'''

    def get_prop_full(self,ctrl,tgt,drive_frequency,pulse_shape,t,args = None):
        '''
            Finds the entire propagator (all levels) at specified times 't' for current set of arguments using QuTiP

            Arguments
            ---------
                ctrl, tgt: int
                    Indices of the Control and Target Qubit (0....N-1)
                drive_frequency: float
                    Angular frequency of the drive, in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and gives pulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args: dictionary
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default - None

            Returns
            -------
                out_U: list
                    List of propagator matrices (Qobjs) at specified times
        '''
        # Create Hamiltonian
        self.create_H_total(ctrl,tgt,drive_frequency,pulse_shape,t,args)
        # Do Time Evolution of the Identity Matrix
        U0 = qt.tensor([qt.qeye(self.N_l) for i in range(self.N)])
        out_U = qt.sesolve(self.H,U0,self.t,args = args, progress_bar= self.schrodinger_progress_bar) #, progress_bar = True
        return out_U.states

    def get_out_vectors(self,ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = None, return_evolution = False):
        '''
            Given a list of vectors in the computational subspace,
            returns a list of time evolved vectors.

            Arguments
            ---------
                ctrl, tgt: int
                    Indices of control and target qubit
                vectors: list of tuples
                    Each element in the list is a tuple of 'N' elements.
                    Each element of a tuple is either 0 or 1, representing the state of that qubit
                drive_frequency: float
                    Angular frequency of the drive, in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and gives pulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args: dict
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default - None
                return_evolution: Bool
                    If True, function returns a Dictionary of each vector's evolution at each point of time.
                    If False, returns only the final states

            Returns
            -------
                psi_out_l: list (If return_evolution is False)
                    A list of the final state (Qobj) of all the vectors specified in the input list
                psi_out_d_evolution: dict (If return_evolution is True)
                    A Dictionary containing lists of time evolution of vectors specified in input.
                    Key will be a string representing the initial state of the qubits.
                    Value will be a list of Qobj vectors representingstate at each point in time
        '''

        # Create Hamiltonian
        #print("here is the bottleneck the code takes enormous time here1")
        self.create_H_total(ctrl,tgt,drive_frequency,pulse_shape,t,args)

        # Create list of Qobj vectors to be evolved
        psi0_l = []
        #print("here is the bottleneck the code takes enormous time here2")
        for ind,i in enumerate(vectors):
            psi0_l.append(qt.tensor([qt.basis(self.N_l,j) for j in i]))

        # Create iterable and evolve each vector
        psi_out_l = []
        #print("here is the bottleneck the code takes enormous time here3")
        # Dictionary to store time evolution
        psi_out_d_evolution = {}
        #print("here is the bottleneck the code takes enormous time here4")

        if self.progress_bar:
            iterable = tqdm(enumerate(psi0_l))
        else:
            iterable = enumerate(psi0_l)
        
        #print("iterable is :",iterable)

        for ind,psi0 in iterable:
            # Do Schrodinger Evolution
            #print("here is the bottleneck the code takes enormous time here5")
            #st = 0
            #st = time.time()
            #print("Hamiltonian is=" ,self.H, "psi0 is=",psi0, "time=",t, "args is =",args)
            psi_out = qt.sesolve(self.H,psi0,self.t,args = args)
            # Append the final state to the list
            #print(f'{time.time()-st}')
            psi_out_l.append(psi_out.states[-1])

            if return_evolution:
                # Create string representing initial state
                key = ''
                for char in vectors[ind]:
                    key+=str(char)
                # Store list of states
                psi_out_d_evolution[key] = psi_out.states

        if return_evolution:
            return psi_out_d_evolution
        else:
            return psi_out_l

    # def get_out_vectors(self, ctrl, tgt, vectors, drive_frequency, pulse_shape, t,args=None, return_evolution=False):
    #    """
    #       Evolve multiple input states in parallel using the new batched qt.sesolve.
    #    """

    # # Create Hamiltonian
    #    self.create_H_total(ctrl, tgt, drive_frequency, pulse_shape, t, args)

    # # Prepare list of initial Qobj states
    #    psi0_l = [qt.tensor([qt.basis(self.N_l, j) for j in vec]) for vec in vectors]

    # # Call batched qt.sesolve once for all states
    #    result = qt.sesolve(self.H, psi0_l, t, args=args)

    #    if return_evolution:
    #     # result.states is {batch_idx: [Qobj, Qobj, ...]}
    #     psi_out_d_evolution = {}
    #     for idx, vec in enumerate(vectors):
    #         key = ''.join(str(x) for x in vec)
    #         psi_out_d_evolution[key] = result.states[idx]
    #     return psi_out_d_evolution

    #    else:
    #     # Return only final states
    #     final_states = [
    #         states[-1] for states in result.states.values()
    #     ] if isinstance(result.states, dict) else [result.states[-1]]

    #     #print(final_states)
    #     return final_states






    def get_M(self,ctrl,tgt,drive_frequency,pulse_shape,t,args = None):
        '''
            Generates propagator in the computational subspace by
            evolving vectors only in the computational subspace.

            Arguments
            ---------
                ctrl, tgt: int
                    Indices of the Control and Target Qubit (0....N-1)
                drive_frequency: float
                    Angular frequency of the drive, in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and givespulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution isdone. The pulse shape is sampled at these times.
                args: dict
                    A dictionary containing the arguments to be passedto the pulse shape function
                    Default - None

            Returns
            -------
                M: Qobj
                    Propagator Projected into the Computational Subspace.
                    Tensor order is permuted to spec1 x spec2 x .... xctrl x tgt
        '''

        # Create Hamiltonian
        self.create_H_total(ctrl,tgt,drive_frequency,pulse_shape,t,args)
        #print("I am Vengence")

        # Create Vectors to be evolved
        vectors = []
        for i in range(2**self.N):
            vectors.append(tuple([int(j) for j in np.binary_repr(i,self.N)]))
        #print("I am Vengence")

        # Call Funtion to Evolve Vectors
        #print("here is the bottleneck the code takes enormous time here")
        vectors_out = self.get_out_vectors(ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = args)

        # Extract only computational subspace elements to get propagator in computational subspace
        M = np.zeros((2**self.N,2**self.N),dtype = complex)
        #st = time.time()
        
        for i in range(2**self.N):
            for j in range(2**self.N):
                # Second index of vectors_out extracts only computational subspace elements
                M[i][j] = vectors_out[j][sum([int(k)*(self.N_l)**(self.N-ind-1) for ind,k in enumerate(list(np.binary_repr(i,self.N)))])]
        #print(f'I am Vengence:{time.time()-st}')


        # Convert to Quantum Object and Permute
        #M = qt.Qobj(M, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape = (2**self.N,2**self.N))
        M = qt.Qobj(M, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]])
        if ctrl == tgt:
            # For single qubit gates
            M = M.permute([i for i in range(self.N) if i!=tgt]+[tgt])
            #print("I am Vengence")

        else:
            # For CR gates
            M = M.permute([i for i in range(self.N) if i!=ctrl and i!=tgt]+[ctrl,tgt])
            #print("I am Vengence")


        # Save the propagator if need be
        if self.save_M:
            l = [[ctrl,tgt,drive_frequency,t,args],np.array(M, dtype = complex)]
            with open(self.propagator_path + '_CR_gate_ctrl_{}_tgt_{}_{}_MHz_Drive_{}_ns_gate_time.pkl'.format(ctrl,tgt,np.round(args['Emax']/(2*np.pi),3),np.around(args['tp'],3)),'wb') as f:
                pickle.dump(l,f)
        return M
    
    def Mfull_to_Mcomp(self,U,ctrl,tgt):
        '''
            Projects a given complete propagator into thecomputational subspace.
            Also permutes the elements to ensure that control andtarget qubits are the last indices.

            Arguments
            ---------
                U: Qobj
                    Unitary Propagator in the whole Hilbert space of N_l**N
                ctrl, tgt: int
                    Indices of control and target qubit

            Returns
            -------
                M: Qobj
                    Unitary Propagator projected into thecomputational subspace of 2**N
        '''
        # Take only computational subpsace elements
        M = np.zeros((2**self.N,2**self.N),dtype = complex)
        for i in range(2**self.N):
            for j in range(2**self.N):
                M[i][j] = U[sum([int(k)*(self.N_l)**(self.N-ind-1) for ind,k in enumerate(list(np.binary_repr(i,self.N)))]),sum([int(l)*(self.N_l)**(self.N-ind-1) for ind,l in enumerate(list(np.binary_repr(j,self.N)))])]
        # Create and Permute Qobj
                #M = qt.Qobj(M, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape = (2**self.N,2**self.N))
                M = qt.Qobj(M, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]])
        if ctrl == tgt:
            # For single qubit gates
            M = M.permute([i for i in range(self.N) if i!=tgt]+[tgt])
        else:
            # For CR gates
            M = M.permute([i for i in range(self.N) if i!=ctrl and i!=tgt]+[ctrl,tgt])
        return M


    '''########################## Accessory Functions ##########################################'''

    def disp_qubits(self):
        '''
            Function to print all Qubit parameters in a tabular form

            Arguments
            ---------
                None

            Returns
            -------
                None
        '''
        rows = [['Qubit','frequency (GHz)','anharmonicity(GHz)','Targets']]
        for i in range(self.N):
            rows.append([i+1,self.qubits[i]['w']/(2*np.pi),self.qubits[i]['a']/(2*np.pi),[j+1 for j in range(self.N) if self.control_target[i][j]!=0]])
        print(tabulate(rows,tablefmt = 'grid'))

    def print_U(self,M_in, rounding = 2, mag_angle_form = True):
        '''
            Prints a given quantum object/numpy 2D array in a readable form

            Arguments
            ---------
                M_in: Qobj or numpy array
                    The input object to be printed
                rounding: int
                    The number of decimal places to which the printed matrix is rounded.
                    Default = 2
                mag_angle_form: Bool
                    If True, it prints the magnitude of the elements of the array,
                    followed by the angles of the elements in degrees.
                    If False, it prints it in complex number format i.e. (a + bj)

            Returns
            -------
                None
        '''
        np.set_printoptions(suppress=True)
        if type(M_in) == np.array([1]):
            M = M_in
        else:
            M = np.array(M_in,dtype = complex)
        if mag_angle_form:
            print(np.around(np.abs(M),rounding))
            print((np.around(np.abs(M),1)!=0)*np.around(np.angle(M,deg = True),rounding))
        else:
            print(np.around(M,rounding))
        np.set_printoptions(suppress=False)

    def qubit_trajectories(self,ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = None):
        '''
            Evolves all the vectors in the computational subspace and generates
            a dictionary with each qubit's evolutions. Note that this is done using
            the partial trace operation to separate each qubit out.

            Arguments
            ---------
                ctrl, tgt:  int
                    Indices of control and target qubit
                vectors: list of tuples
                    Each element in the list is a tuple of 'N' elements.
                    Each element is either 0 or 1, representing the state of that qubit
                drive_frequency: float
                    Angular frequency of the drive, in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and gives pulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args: dict
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default - None

            Returns
            -------
                partial_trace_qubit_list: list
                    A list of dictionaries. Each dictionary in the list corresponds to the evolution of each qubit.
                    Each dictionary has keys corresponding to the initial state of the qubits, and values are lists,
                    which correspond to the density matrix of each qubit at each point in time.
        '''

        # Call Funtion to Evolve Vectors
        vectors_out = self.get_out_vectors(ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = args, return_evolution = True)

        # Create one dictionary for each qubit and store them in a list
        partial_trace_qubit_list = [{} for i in range(self.N)]

        for state in vectors_out:
            for i in range(self.N):
                # First do partial trace
                l = [j.ptrace(i) for j in vectors_out[state]]

                # Then project into computational subspace
                if self.N == 1:
                    #partial_trace_qubit_list[i][state] = [qt.Qobj([[j[0][0][0],j[1][0][0]]],dims = [[2],[1]], shape = (2,1)) for j in l]
                    partial_trace_qubit_list[i][state] = [qt.Qobj([[j[0][0][0],j[1][0][0]]],dims = [[2],[1]]) for j in l]
                else:
                    partial_trace_qubit_list[i][state] = [qt.Qobj([[j[0,0],j[0,1]],[j[1,0],j[1,1]]],dims = [[2],[2]]) for j in l]
        return partial_trace_qubit_list

    def extract_expectation_values(self,state_list):
        '''
            Extracts x,y,z expectation values from a list of qubit density matrices

            Arguments
            ---------
                state_list: list
                    List of qubit (2D) density matrices

            Returns
            -------
                x,y,z: lists
                    list of corresponding X, Y, Z expectation values
        '''
        x = []
        y = []
        z = []

        for state in state_list:
            x.append(qt.expect(qt.sigmax(),state))
            y.append(qt.expect(qt.sigmay(),state))
            z.append(qt.expect(qt.sigmaz(),state))
        return x,y,z

    def Bloch_sphere_visualize(self,path,animate_t_step,ctrl,tgt,drive_frequency,pulse_shape,t,args = None, vectors = None, animate = False, use_points = False,angles = None, dpi = 300):
        '''
            Function to plot qubit evolution on the Bloch sphere

            Arguments
            ---------
                path: string
                    Path for saving gifs/images
                animate_t_step: int
                    Step at which the images should be plotted. Every point in t[::animate_t_step] is plotted
                ctrl,tgt : int
                    Indices of control and target qubits
                drive_frequency: float
                    Drive frequency in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and gives pulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args: dict
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default - None 
                    vectors: list of tuples
                    List of N-length tuples, with each element of the tuple corresponding to the initial state of that qubit.
                    The corresponding computational basis states are evolved in time
                    Default - None
                 animate: Bool
                    Toggles between saving gifs and images
                    Default - False
                use_points: Bool
                    If images are saved, toggles between plotting points vs arrows on the Bloch Sphere
                    Default - False
                angles: array like
                    Sets the azimuthal and elevation angles (Degrees) of the Bloch spheres which are saved
                    angles[0] - azimuthal angle in Degrees
                    angles[1] - elevation angle in Degrees
                    Default - None
                dpi: Float
                    Resolution to save the image/gif
                    Default - 300

            Returns
            -------
                None
        '''
        # Evolve all computational states if no preferred states are given
        if vectors == None:
            vectors = []
            for i in range(2**self.N):
                vectors.append(tuple([int(j) for j in np.binary_repr(i,self.N)]))
                qubit_states = self.qubit_trajectories(ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = args)

        else:
            qubit_states = self.qubit_trajectories(ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = args)

        # If gifs are needed
        if animate:
            # Set configuration of gif
            fig = plt.figure(dpi = dpi)
            if angles:
                ax = Axes3D(fig, azim=angles[0], elev= angles[1])
            else:
                ax = Axes3D(fig, azim=-40, elev=30)
            sphere = qt.Bloch(fig = fig, axes=ax)

            # Function to add states to sphere
            def animate(i,qubit,state):
                print(i,end = '\r')
                sphere.clear()
                sphere.add_states(qubit[state][i])
                sphere.make_sphere()
                return ax

            # Function to initialize Bloch Sphere
            def init():
                sphere.vector_color = ['r']
                return ax

            # Animate and save for each state
            for ind,qubit in enumerate(qubit_states):
                for state in qubit:

                    print("state: ",state, " qubit: ",ind)
                    ani = animation.FuncAnimation(fig, animate, np.arange(0,len(qubit[state]),animate_t_step),
                                                  init_func=init,blit=False, repeat=False, fargs = (qubit,state))
                    if ind == ctrl:
                        ani.save(path +'bloch_sphere_{}qubit_{}_init_state_{}.gif'.format('ctrl_',ind,state),fps=80)
                    elif ind == tgt:
                        ani.save(path +'bloch_sphere_{}qubit_{}_init_state_{}.gif'.format('tgt_',ind,state),fps=80)
                    else:
                        ani.save(path +'bloch_sphere_{}qubit_{}_init_state_{}.gif'.format('',ind,state),fps=80)

        # To save only images
        else:
            # Set basic sphere configuration
            fig = plt.figure(dpi = dpi)
            sphere = qt.Bloch(fig = fig)
            if angles:
                sphere.view = angles
            for ind,qubit in enumerate(qubit_states):
                for state in qubit:

                    print("state: ",state, " qubit: ",ind)
                    sphere.clear()
                    # If only points are required
                    if use_points:
                        x,y,z = self.extract_expectation_values(qubit[state])
                        sphere.add_points([x,y,z])
                    # If states are to be plotted
                    else:
                        sphere.add_states(qubit[state][0::animate_t_step])
                    if ind == ctrl:
                        sphere.save(path +'bloch_sphere_{}qubit_{}_init_state_{}.png'.format('ctrl_',ind,state))
                    elif ind == tgt:
                        sphere.save(path +'bloch_sphere_{}qubit_{}_init_state_{}.png'.format('tgt_',ind,state))
                    else:
                        sphere.save(path +'bloch_sphere_{}qubit_{}_init_state_{}.png'.format('',ind,state))

    def plot_expectation_values(self,ctrl,tgt,drive_frequency,pulse_shape,t,args = None, vectors = None):
        '''
            Function to plot qubit evolution as expectation values

            Arguments
            ---------
                ctrl,tgt : int
                    Indices of control and target qubits
                drive_frequency: float
                    Drive frequency in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and gives pulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args: dict
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default - None
                vectors: list of tuples
                    List of N-length tuples, with each element of the tuple corresponding to the initial state of that qubit.
                    The corresponding computational basis states are evolved in time
                    Default - None

            Returns
            -------
                None
        '''

        # Evolve all computational states if no vectors are specified
        if vectors == None:
            vectors = []
            for i in range(2**self.N):
                vectors.append(tuple([int(j) for j in np.binary_repr(i,self.N)]))
                qubit_states = self.qubit_trajectories(ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = args)

        else:
            qubit_states = self.qubit_trajectories(ctrl,tgt,vectors,drive_frequency,pulse_shape,t,args = args)

        # Iterate and plot over all qubits and initial states
        for ind,qubit in enumerate(qubit_states):
            for state in qubit:
                x,y,z = self.extract_expectation_values(qubit[state])

                fig, axs = plt.subplots(1,3)
                fig.set_size_inches(18,4)
                fig.suptitle('Qubit {} {} '.format(ind,('(ctrl)' if ind == ctrl else '(tgt)') if ind == ctrl or ind == tgt else '') + "Initial State: {}".format(state), fontsize = '20')

                label_dict = {0:'z',1:'x',2:'y'}
                for col,axis in enumerate([z,x,y]):
                    axs[col].plot(t,axis)
                    axs[col].grid()
                    axs[col].set(ylabel = label_dict[col].upper() + 'Expectation')
                    axs[col].set_ylim([-1.1,1.1])
                for ax in axs.flat:
                    ax.set(xlabel = 'Time (ns)')
                plt.subplots_adjust(hspace = 0.6)
                plt.show()

    def get_f_np(self,U,V):
            '''
                Returns the fidelity between two numpy matrices U and V

                Arguments
                ---------
                    U,V: Numpy complex 2D arrays
                        Matrices to be compared

                Returns
                -------
                    F: float
                        Fidelity between matrices
            '''

            d = U.shape[0]
            N = int(np.log2(d))
            U_f = qt.Qobj(U, dims = [[2 for i in range(N)],[2 for i in range(N)]], shape = (2**N,2**N))
            V_f = qt.Qobj(V, dims = [[2 for i in range(N)],[2 for i in range(N)]], shape = (2**N,2**N))
            F = (1/(d*(d+1)))*((U_f.dag()*U_f).tr() + np.abs((U_f.dag()*V_f).tr())**2)
            return np.real(F)

    def get_f_qt(self,U,V):
            '''
                Returns the fidelity between two QuTiP objects U and V

                Arguments
                ---------
                    U,V: Qobj
                        Matrices to be compared

                Returns
                -------
                    F: float
                        Fidelity between matrices
            '''

            d = U.shape[0]

            F = (1/(d*(d+1)))*((U.dag()*U).tr() + np.abs((U.dag()*V).tr())**2)
            return F

    def closest_U_svd(self,M):
        '''
            Finds the closest Unitary to a given Matrix M, by using Singular Value Decomposition

            Arguments:
                M (Numpy 2D array)

            Returns:
                U (Numpy 2D Array)
                    Closest Unitary to M
        '''

        V,_,Wdag = la.svd(M)
        U = V.dot(Wdag)
        return U


    def plot_static_zz(self,option = 'Mean', legend = True):
        '''
            Plots the spread of frequencies in the processor
            (dependent on the state of other qubits) after coupling is introduced

            Arguments:
                option = 'Mean'
                    Plots the deviation from the mean
                option = 'bare'
                    Plots the deviation from the bare frequencies
                option = 'dressed'
                    Plots the deviation from the dressed frequency (other qubits are in |0>)

                legend - Bool
                    If true, adds a legend to the plot
        '''
        label_font_size = 20
        tick_font_size = 18

        x = np.arange(self.N)*self.N # the label locations
        width = 0.075  # the width of the bars

        fig, ax = plt.subplots()
        fig.set_size_inches(8,6)

        heights_all = [] #Added by Jay
        for j in range(2**(self.N-1)):
            heights = []
            for i in range(self.N):
                if option == 'dressed':heights.append((list(self.qubits[i]['w_kerr'].values())[j] -self.qubits[i]['w_dressed'])*1e6/(2*np.pi))
                elif option == 'bare':heights.append((list(self.qubits[i]['w_kerr'].values())[j] -self.qubits[i]['w'])*1e6/(2*np.pi))
                elif option == 'Mean':heights.append((list(self.qubits[i]['w_kerr'].values())[j] -self.qubits[i]['w_mean_kerr'])*1e6/(2*np.pi))
            ax.bar(x - (j-2**(self.N-2))*width, heights, width,label=np.binary_repr(j).zfill(self.N-1))
            heights_all.append(heights) #Added by Jay


        labels = ['Qubit {}'.format(i+1) for i in range(self.N)]
        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Variation of frequency \n from {}frequency(kHz)'.format(option), fontsize = label_font_size, labelpad =7)
#         ax.set_title('Cross-Kerr shift in {} qubitsystem'.format(self.N),fontsize = 15)
        ax.set_xticks(x)
        ax.set_xticklabels(labels,fontsize = tick_font_size)
        plt.yticks(fontsize = tick_font_size+2, weight = 'bold')

        if legend:
            ax.legend()
        plt.ylim(-400,400)
        # plt.legend(bbox_to_anchor=(1, 1),bbox_transform=plt.gcf().transFigure)
        plt.grid(True)
        plt.show()

        return heights_all

    '''########################## New Error Budget #############################################'''

    def get_U_CR_from_angles(self,phi0, phi1, theta,print_U_matrix = False, print_vals = False):
        '''
            Returns a Unitary Matrix from the CR Gate Family for a set of given angles

            Arguments
            ---------
                phi0, phi1: float
                    Rotation of the target when the control is in |0> vs |1>.
                    Angles are in radians
                theta: Numpy 1D array of floats
                    N-1 dimensional array, with each angle (radians) corresponding to phase picked up by each qubit
                print_U_matrix: Bool
                    If True, function prints the matrix U which is created.
                    Use to debug
                    Default - False
                print_vals: Bool
                    If True, function prints all the values of phi,theta given
                    Use to debug
                    Default - False


            Returns
            -------
                U_CR (Qobj):
                    Unitary Matrix from the CR Gate Family, as per the specified angles
        '''

        # Generate CR Matrix in a relevant tensor product structure
        # Tensor multiply all the phases of spectator qubits first
        phase = np.eye(1,dtype = complex)
        for i in range(self.N-2):
            mat = np.zeros((2,2),dtype = complex)
            mat[0][0] = 1
            mat[1][1] = np.exp(1j*theta[i])
            phase = np.kron(phase,mat)

        # Create Control Target Matrix
        ct = np.zeros((4,4), dtype = complex)
        thetac = theta[-1]


        ct[0][0] = np.cos(phi0/2)
        ct[1][1] = np.cos(phi0/2)

        ct[2][2] = np.exp(1j*thetac)*np.cos(phi1/2)
        ct[3][3] = np.exp(1j*thetac)*np.cos(phi1/2)

        ct[1][0] = -1j*np.sin(phi0/2)
        ct[0][1] = -1j*np.sin(phi0/2)

        ct[3][2] = -1j*np.exp(1j*thetac)*np.sin(phi1/2)
        ct[2][3] = -1j*np.exp(1j*thetac)*np.sin(phi1/2)

        # Tensor multiply phases and control target matrix
        U_CR = np.kron(phase,ct)
        #U_CR = qt.Qobj(U_CR, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape = (2**self.N,2**self.N))
        U_CR = qt.Qobj(U_CR, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]])

        if print_U_matrix:
            self.print_U(U_CR)

        if print_vals:

            print("phi0 avg = ", phi0*180/np.pi)
            print("phi1 avg= ", phi1*180/np.pi)

            print("theta_final \n", theta*180/(np.pi))


        return U_CR

    def get_f_blackbox(self,angles,M):
        '''
            Function that returns the fidelity given all the angles estimated

            Arguments
            ---------
                angles: array like, contains floats
                    N+1 dimensional array. First two elements contain phi0, phi1 (angles of rotation of target)
                    Rest of the elements contain theta (phases picked up by spectators and control)

                M: Qobj
                    Unitary Propagator

            Returns
            -------
                -fidelity: float
                    -1*(Fidelity between matrix constructed from angles and propagator M)
        '''
        # Create matrix from angles
        U_CR = self.get_U_CR_from_angles(angles[0], angles[1], angles[2:])

        # Return -1*fidelity
        return -1*self.get_f_qt(U_CR,M)

    def get_angles_optimal(self,M, use_zero_initial_values = False):
        '''
            Function to compute the angles of best fit for the CR gate from the propagator M

            Arguments
            ---------
                M: Qobj
                    Unitary propagator, projected into the computational subspace
                    Tensor order should be appropriate (spec qubits x ctrl x tgt)
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values computed using the older methods are given to optimizer
                    Default - False

            Returns
            -------
                phi0, phi1: float
                    Rotation of the target about the X axis when the ctrl is in |0> vs |1>
                theta: array of floats
                    (N-1) Array of float numbers which correspond to phases picked up by each spectator
        '''

        if use_zero_initial_values:
            angles_initial = [0,0] + [0]*(self.N - 1)
        else:
            # Extract analytical angles for initial conditions
            phi0, phi1, theta = self.get_angles(M)
            # Extract phase difference between phases accumulated for|1> and |0> of each qubit
            theta_diff = theta[1::2] - theta[::2]
            angles_initial = [phi0,phi1] + list(theta_diff)

        # Minimize -1*fidelity (Maximize fidelity) and extract bestset of angles
        res = scipy.optimize.minimize(self.get_f_blackbox,angles_initial,args= (M), method = 'Nelder-Mead')

        phi0 = res.x[0]
        phi1 = res.x[1]
        theta = res.x[2:]

        return phi0, phi1, theta

    def get_U_CR_optimizer(self,M, use_zero_initial_values = False):
        '''
            Function to create the closest matrix in the CR family to the propagator

            Arguments
            ---------
                M: Qobj
                    Propagator of the gate, projected into the computational subspace
                    Tensor order should be (spec qubits x ctrl x tgt)
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer

            Returns
            -------
                U_CR: Qobj
                    Closest unitary in the CR family
        '''
        # Extract optimal angles
        phi0, phi1, theta = self.get_angles_optimal(M,use_zero_initial_values = use_zero_initial_values)
        # Create the matrix from angles
        U_CR = self.get_U_CR_from_angles(phi0, phi1, theta)
        return U_CR

    def get_U_CR_CP(self,M,print_vals = False):
        '''
            Returns Closest Unitary Matrix from the CR Gate Family for a given propagator, ignoring conditional phase

            Arguments
            ---------
                M: Qobj
                    Propagator, as projected into computational subspace
                    Tensor order should be (spec qubits x ctrl x tgt)
                print_vals: Bool
                    If True, function prints all the values of phi,theta estimated from the matrix
                    Use to debug
                    Default - False

            Returns
            -------
                U_CR_CP (Qobj):
                    Closest Unitary Matrix from the CR Gate Family,allowing for conditional phases
        '''

        # Extract Angles from each block diagonal (allow for conditional phase)
        phi0,phi1,theta0, theta1 = self.get_angles(M, print_vals,get_all_theta = True)

        U_CR_CP = np.zeros((2**self.N,2**self.N), dtype = complex)
        for i in range(2**(self.N-2)):
            # Construct the matrix
            ind_0 = 4*i
            U_CR_CP[ind_0][ind_0] = np.exp(1j*theta0[i])*np.cos(phi0/2)
            U_CR_CP[ind_0][ind_0+1] = -1j*np.exp(1j*theta0[i])*np.sin(phi0/2)
            U_CR_CP[ind_0+1][ind_0] = -1j*np.exp(1j*theta0[i])*np.sin(phi0/2)
            U_CR_CP[ind_0+1][ind_0+1] = np.exp(1j*theta0[i])*np.cos(phi0/2)

            ind_1 = 4*i+2
            ind_0 = 4*i
            U_CR_CP[ind_1][ind_1] = np.exp(1j*theta1[i])*np.cos(phi1/2)
            U_CR_CP[ind_1][ind_1+1] = -1j*np.exp(1j*theta1[i])*np.sin(phi1/2)
            U_CR_CP[ind_1+1][ind_1] = -1j*np.exp(1j*theta1[i])*np.sin(phi1/2)
            U_CR_CP[ind_1+1][ind_1+1] = np.exp(1j*theta1[i])*np.cos(phi1/2)

        # Convert to Qobj and Return
        U_CR_CP = qt.Qobj(U_CR_CP, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]])#, shape =(2**self.N,2**self.N))

        return U_CR_CP

    def get_U_CR_N(self,M,n):
        '''
            Finds closest unitary operation where 'n' qubits can rotate arbitrarly,
            for a given propagator (in computational subspace). Uses SVD

            Arguments
            ---------
                M: Qobj
                    Propagator, as projected into computational subspace,
                    Should be Permuted such that control and target are penultimate and final indices
                n: int
                    Shows the number of qubits which are allowed to rotate arbitrarily.
                    n = 1 only target is free
                    n = 2 control and target are free
                    n = 3 onwards, each spectator is included one by one

            Returns
            -------
                M_svd: Qobj
                    Closest Unitary operation in which 'n' qubits are allowed to rotate arbitrarily,
                    but other qubits can only pick up a phase
        '''

        M = np.array(M.full(), dtype = complex)
        # M = np.array(M)
        M_svd = np.zeros((2**self.N,2**self.N), dtype = complex)

        # Extract Closest Unitary for each element in the block diagonal
        for i in range(2**(self.N-n)):
            ind = (2**n)*i
            # print(M)
            U_svd = self.closest_U_svd(M[ind:ind+2**n,ind:ind+2**n])
            M_svd[ind:ind+2**n,ind:ind+2**n] = U_svd

        # Convert to Qobj and Return
        # M_svd = qt.Qobj(M_svd, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape = (2**self.N,2**self.N))
        M_svd = qt.Qobj(M_svd, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]])
        return M_svd

    def calibrate_cnot_phi(self,ctrl,tgt,drive_frequency,pulse_shape,args,E_key = 'Emax',t_key = 'tp',E_list = np.arange(3,90,3),t_list = np.arange(50,150,25), use_optimizer = True, use_zero_initial_values = False):
        '''
            Method to extract angle of rotation of target for varying drive strengths a pulse lengths.
            Can be used to calibrate the CR gate. Works only if the pulse shape function has a flat top,
            and symmetric rise and fall which are a fraction of pulse length.

            Arguments
            ---------
                ctrl, tgt (int):
                    indices of ctrl and tgt qubit
                drive_frequency (float):
                    Drive Frequency in Grad/s
                pulse_shape (function):
                    Function that returns pulse value as a function of time
                args (dict):
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key (hashable object):
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key (hashable object):
                    args[t_key] = Pulse length
                    Default: 'tp'
                E_list (1D numpy array):
                    List of drive strengths in MHz
                    Default: np.arange(3,90,3)
                t_list (1D numpy array):
                    List of pulse lengths in nanoseconds
                    Default: np.arange(50,200,25)
                use_optimizer: Bool
                    If True, angles are extracted using the optimizer
                    If False, angles are extracted analytically
                    Default - True

            Returns
            -------
                phi0, phi1 (dict):
                    phi0[drive_strength] = list of angles of rotation corresponding to t_list
        '''
        # Dictionaries to be returned
        phi0 = {}
        phi1 = {}
        print("nice")

        # Run through E_list and t_list
        for i in tqdm(E_list):
            phi0[i] = []
            phi1[i] = []
            args[E_key] = i*1e-3*2*np.pi
            for j in t_list:
                args[t_key] = j
                t = np.linspace(0,j,600)
                # Get propagator
                #print("I am vengance")
                M = self.get_M(ctrl,tgt,drive_frequency,pulse_shape,t,args)
                #print("I am vengance")
                # Get angles
                if use_optimizer:
                    a,b,_ = self.get_angles_optimal(M,use_zero_initial_values = use_zero_initial_values)
                else:
                    a,b,_ = self.get_angles(M)
                phi0[i].append(a)
                phi1[i].append(b)
            phi0[i] = np.array(phi0[i])
            phi1[i] = np.array(phi1[i])

        return phi0,phi1

    def calibrate_cnot_t(self,ctrl,tgt,drive_frequency,pulse_shape,args,E_key = 'Emax',t_key = 'tp',E_list = np.arange(3,90,3),t_list = np.arange(50,150,25), use_optimizer = True, use_zero_initial_values = False):
        '''
            Method to calibrate the CR gate. Works only if the pulse shape function has a flat top,
            and symmetric rise and fall which are a fraction of pulse length. Finds time taken for
            target states to separate by an angle of 180 degrees, when the control is in |0> vs |1>

            Arguments
            ---------
                ctrl, tgt (int):
                    indices of ctrl and tgt qubit
                drive_frequency (float):
                    Drive Frequency in Grad/s
                pulse_shape (function):
                    Function that returns pulse value as a function of time
                args (dict):
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key (hashable object):
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key (hashable object):
                    args[t_key] = Pulse length
                    Default: 'tp'
                E_list (1D numpy array):
                    List of drive strengths in MHz
                    Default: np.arange(3,90,3)
                t_list (1D numpy array):
                    List of pulse lengths in nanoseconds
                    Default: np.arange(50,200,25)
                use_optimizer: Bool
                    If True, angles are extracted using the optimizer
                    If False, angles are extracted analytically
                    Default - True
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer

            Returns
            -------
                ts (list):
                    List of pulse lengths correspoding to E_list
                phi0, phi1 (dict):
                    phi0[drive_strength] = list of angles of rotation corresponding to t_list
        '''
        # Get angles
        phi0,phi1 =self.calibrate_cnot_phi(ctrl,tgt,drive_frequency,pulse_shape,args,E_key,t_key,E_list,t_list,use_optimizer = use_optimizer, use_zero_initial_values =use_zero_initial_values)

        # List of calibrated times, corresponding to E_list
        ts = []

        # Extrapolate time evolution and get pulse time
        for i in phi0:
            m0,b0 = np.polyfit(t_list[1:4],phi0[i][1:4],1)
            m1,b1 = np.polyfit(t_list[1:4],phi1[i][1:4],1)
            tcnot = np.roots([-m1+m0,-b1+b0+np.pi])
            if len(tcnot)==0:
                continue
            ts.append(tcnot[0])
        return ts,phi0,phi1

    '''################################## Parallelized version - Jay #######################################'''

    def calibrate_cnot_t_parallel(self,ctrl,tgt,drive_frequency,pulse_shape,args,E_key = 'Emax',t_key = 'tp',E_list = np.arange(3,90,3),t_list = np.arange(50,150,25), use_optimizer = True, use_zero_initial_values = False):
        '''
            Method to calibrate the CR gate. Works only if the pulse shape function has a flat top,
            and symmetric rise and fall which are a fraction of pulse length. Finds time taken for
            target states to separate by an angle of 180 degrees, when the control is in |0> vs |1>

            Arguments
            ---------
                ctrl, tgt (int):
                    indices of ctrl and tgt qubit
                drive_frequency (float):
                    Drive Frequency in Grad/s
                pulse_shape (function):
                    Function that returns pulse value as a function of time
                args (dict):
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key (hashable object):
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key (hashable object):
                    args[t_key] = Pulse length
                    Default: 'tp'
                E_list (1D numpy array):
                    List of drive strengths in MHz
                    Default: np.arange(3,90,3)
                t_list (1D numpy array):
                    List of pulse lengths in nanoseconds
                    Default: np.arange(50,200,25)
                use_optimizer: Bool
                    If True, angles are extracted using the optimizer
                    If False, angles are extracted analytically
                    Default - True
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer

            Returns
            -------
                ts (list):
                    List of pulse lengths correspoding to E_list
                phi0, phi1 (dict):
                    phi0[drive_strength] = list of angles of rotation corresponding to t_list
        '''
        print("hello")
        # Get angles
        phi0,phi1 = self.calibrate_cnot_phi_parallel(ctrl,tgt,drive_frequency,pulse_shape,args,E_key,t_key,E_list,t_list, use_optimizer = use_optimizer, use_zero_initial_values = use_zero_initial_values)

        print(phi0)
        print(phi1)

        # List of calibrated times, corresponding to E_list
        ts = []

        # Extrapolate time evolution and get pulse time
        for i in phi0:
            m0,b0 = np.polyfit(t_list[1:4],phi0[i][1:4],1)
            m1,b1 = np.polyfit(t_list[1:4],phi1[i][1:4],1)
            tcnot = np.roots([-m1+m0,-b1+b0+np.pi])
            if len(tcnot)==0:
                continue
            ts.append(tcnot[0])
        return ts,phi0,phi1
        # ts = []

        # MAX_TIME = 900.0   # ns (cap)
        # MIN_TIME = 1.0

        # for i in phi0:
        #     try:
        #         # fit linear region
        #         m0, b0 = np.polyfit(t_list[1:4], phi0[i][1:4], 1)
        #         m1, b1 = np.polyfit(t_list[1:4], phi1[i][1:4], 1)

        #         denom = (-m1 + m0)

        #         # Handle near-zero slope (BAD REGION)
        #         if abs(denom) < 1e-6:
        #             tcnot = MAX_TIME
        #         else:
        #             tcnot = (np.pi + b1 - b0) / denom

        #         # Handle invalid values
        #         if not np.isfinite(tcnot):
        #             tcnot = MAX_TIME

                # Clip extreme values
        #         tcnot = np.clip(tcnot, MIN_TIME, MAX_TIME)

        #     except Exception:
        #         tcnot = MAX_TIME

        #     ts.append(tcnot)
        
        # return ts,phi0,phi1
        # print(ts)


    def calibrate_cnot_phi_parallel(self,ctrl,tgt,drive_frequency,pulse_shape,args,E_key = 'Emax',t_key = 'tp',E_list = np.arange(3,90,3),t_list = np.arange(50,150,25), use_optimizer = True, use_zero_initial_values = False):
        '''
            Method to extract angle of rotation of target for varying drive strengths a pulse lengths.
            Can be used to calibrate the CR gate. Works only if the pulse shape function has a flat top,
            and symmetric rise and fall which are a fraction of pulse length.

            Arguments
            ---------
                ctrl, tgt (int):
                    indices of ctrl and tgt qubit
                drive_frequency (float):
                    Drive Frequency in Grad/s
                pulse_shape (function):
                    Function that returns pulse value as a function of time
                args (dict):
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key (hashable object):
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key (hashable object):
                    args[t_key] = Pulse length
                    Default: 'tp'
                E_list (1D numpy array):
                    List of drive strengths in MHz
                    Default: np.arange(3,90,3)
                t_list (1D numpy array):
                    List of pulse lengths in nanoseconds
                    Default: np.arange(50,200,25)
                use_optimizer: Bool
                    If True, angles are extracted using the optimizer
                    If False, angles are extracted analytically
                    Default - True

            Returns
            -------
                phi0, phi1 (dict):
                    phi0[drive_strength] = list of angles of rotation corresponding to t_list
        '''
        # Dictionaries to be returned
        phi0 = {}
        phi1 = {}
        #print("Hello again")

        # Run through E_list and t_list
        for i in tqdm(E_list):
            phi0[i] = []
            phi1[i] = []
            args[E_key] = i*1e-3*2*np.pi
        
             

            def process(j):
                #print("I am batman")

                args[t_key] = j
                t = np.linspace(0,j,600)
                #print("I am vengence")
                # Get propagator
                M = self.get_M(ctrl,tgt,drive_frequency,pulse_shape,t,args)
                #print("I am vengence")
                # Get angles
                if use_optimizer:
                    a,b,_ = self.get_angles_optimal(M, use_zero_initial_values = use_zero_initial_values)
                else:
                    a,b,_ = self.get_angles(M)
                #print("I am the knight")

                return a, b

            results = Parallel(n_jobs=-2)(delayed(process)(j) for j in t_list)
            results = np.transpose(np.asarray(results))

            phi0[i] = results[0]
            phi1[i] = results[1]

        return phi0,phi1

    '''###################################### End of addition by Jay#######################################'''

    def get_F(self,ctrl,tgt,drive_frequency, pulse_shape, t, args = None, use_optimizer = True, use_zero_initial_values = False):
        '''
            Finds the CR Gate Fidelity between a specified control and target,
            for a given drive frequency and pulse

            Arguments
            ---------
                ctrl, tgt: int
                    Indices of the Control and Target Qubit (0....N-1)
                drive_frequency: float
                    Angular frequency of the drive, in Grad/s
                pulse_shape: Python Function
                    A function which takes time as an input and gives pulse value at that time
                t: Numpy 1D array
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args: dict
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default - None
                use_optimizer: Bool
                    If True, the optimizer is used to find angles and closest U_CR
                    If False, the angles are computed analytically
                    Default - True
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer
                    Default - False

            Returns
            -------
                F: float
                    Fidelity of the gate
        '''
        # Extract propagator
        M = self.get_M(ctrl,tgt,drive_frequency,pulse_shape,t,args)
        # Find closest unitary
        if use_optimizer:
            U_CR = self.get_U_CR_optimizer(M,use_zero_initial_values = use_zero_initial_values)
        else:
            U_CR = self.get_U_CR(M)

        # Find and return fidelity
        F = self.get_f_qt(M,U_CR)
        return F

    def E_vs_F_optimizer(self,ctrl,tgt,drive_frequency,calib_path,pulse_shape,args,E_key = 'Emax',t_key = 'tp',t_step_key = 't_step', use_zero_initial_values = False):
        '''
            Method to find Fidelity vs Drive Strength, for a pre-calibrated list (E vs t) of drive-strengths

            Arguments
            ---------
                ctrl, tgt: int
                    indices of ctrl and tgt qubit
                drive_frequency: float
                    Drive Frequency in Grad/s
                calib_path: string
                    Path to the pickle file with calibration times
                pulse_shape: function
                    Function that returns pulse value as a function of time
                args: dict
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key: hashable object
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key: hashable object
                    args[t_key] = Pulse length
                    Default: 'tp'
                t_step_key: hashable object
                    args[t_step_key] = Time sampling step
                    Default: 't_step'
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer

            Returns
            -------
                F_list: list
                    List of fidelities
                E_list: list
                    Corresponding list of drive strengths in MHz
        '''
        # # Identify Detuning in MHz
        # det = int(1e3*(self.qubits[ctrl]['w']-self.qubits[tgt]['w']+ 0.0001)/(2*np.pi))

        # # Load precalibrated list of gate times
        # with open("./pickles/CR_gate_raw_fidelity/cnot_times_{}_MHz.pkl".format(det),'rb')as f:
        #     ts = pickle.load(f)

        with open(calib_path,'rb') as f:
            ts = pickle.load(f)

        # Get fidelity for each such set of parameters
        F_list = []
        E_list = list(ts.keys())
        for i in tqdm(ts):
            args[t_key] = ts[i]
            args[E_key] = 1e-3*i*2*np.pi
            t = np.arange(0,args[t_key],args[t_step_key])
            F = self.get_F_optimizer(ctrl,tgt,drive_frequency,pulse_shape,t,args, use_zero_initial_values = use_zero_initial_values)
            F_list.append(F)
        return F_list,E_list

    def get_new_error_budget(self,M, use_optimizer = True, use_zero_initial_values = False, no_CP = True):
        '''
            Function to get error budget of a given propagator in the computational subspace, as per new definitions
            For the CR Gate
            Arguments
            ---------
                M: Qobj
                    Unitary propagator projected into the computational subspace
                use_optimizer: Bool
                    If True, the optimizer is used to find angles and closest U_CR
                    If False, the angles are computed analytically
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer
                no_CP: Bool
                    If True, it doesn't calculate conditional phase error, and lumps this together with target rotation error
                    If False, it calculates it and returns it
                    Default: True

            Returns
            -------
                E: float
                    CR gate error
                E_CP: float
                    Conditional phase errors
                    Not returned if no_CP is True
                E_T: float
                    Target rotation errors
                E_C: float
                    Control rotation errors
                E_specs: list of float
                    List of each spectator's rotation error
                E_leak: float
                    Leakage errors
        '''

        # Get closest CR Unitary
        if use_optimizer:
            U_CR = self.get_U_CR_optimizer(M,use_zero_initial_values = use_zero_initial_values)
        else:
            U_CR = self.get_U_CR(M)

        # Get closest CR Unitary which allows conditional phase
        U_CR_CP = self.get_U_CR_CP(M)

        # Get closest unitary where target has arbitrary rotation
        U_TU = self.get_U_CR_N(M,1)

        # Get closest unitary where control and target have arbitrary rotation
        U_CTU = self.get_U_CR_N(M,2)

        # Find all fidelity metrics
        E_U_CR = 1 - self.get_f_qt(M,U_CR)
        E = E_U_CR

        E_U_CR_CP = 1 - self.get_f_qt(M,U_CR_CP)
        E_CP = E_U_CR - E_U_CR_CP
        E_U_TU = 1 - self.get_f_qt(M,U_TU)

        if no_CP:
            E_T = E_U_CR - E_U_TU
        else:
            E_T = E_U_CR_CP - E_U_TU

        E_U_CTU = 1 - self.get_f_qt(M,U_CTU)
        E_C = E_U_TU - E_U_CTU

        E_specs = []
        for i in range(2,self.N):
            E_specs.append(self.get_f_qt(M,self.get_U_CR_N(M,i+1)) - self.get_f_qt(M,self.get_U_CR_N(M,i)))

        E_leak = 1 - self.get_f_qt(M,self.get_U_CR_N(M,self.N))

        if no_CP:
            return E, E_T, E_C, E_specs, E_leak
        else:
            return E, E_CP, E_T, E_C, E_specs, E_leak

    def E_vs_F_new_error_budget(self,ctrl,tgt,drive_frequency,calib_path, pulse_shape,args = None,E_key = 'Emax',t_key ='tp',t_step_key = 't_step', use_optimizer = True,use_zero_initial_values = False, E_max = None, E_min = None,no_progress_bar = False, no_CP = True):
        '''
            Method to find Fidelity and Error Budget vs Drive Strength, for a pre-calibrated list (E vs t) of drive-strengths
            This uses the new definitions

            Arguments:
                ctrl, tgt: int
                    indices of ctrl and tgt qubit
                drive_frequency: float
                    Drive Frequency in Grad/s
                calib_path: string
                    Path to the pickle file with calibration times
                pulse_shape: function
                    Function that returns pulse value as a function of time
                args: dict
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key: hashable object
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key: hashable object
                    args[t_key] = Pulse length
                    Default: 'tp'
                t_step_key: hashable object
                    args[t_step_key] = Time sampling step
                    Default: 't_step'
                use_optimizer: Bool
                    If True, the optimizer is used. If False, the analytical solver is used
                    Default: True
                use_zero_initial_values: Bool
                    If True, the optimizer is given zero initial conditions
                    If False, the optimizer is given analytical initial conditions
                    Default: True
                E_max: float
                    Maximum value of drive strength to which the computation is performed
                    Default: None
                E_min: float
                    Minimum value of drive strength to which the computation is performed
                    Default: None
                no_progress_bar: Bool
                    If true, a progress bar is activated
                    Default: False
                no_CP: Bool
                    If True, it doesn't calculate conditional phase error, and lumps this together with target rotation error
                    If False, it calculates it and returns it
                    Default: True

            Returns:
                Elements of each list correspond to different drive strengths
                E: list
                    List of CR gate errors
                E_CP: list
                    List of conditional phase errors
                    Not returned if no_CP if True
                E_T: list
                    List of target rotation errors
                E_C: list
                    List of control rotation errors
                E_specs: list
                    Contains lists of each spectator's rotation error
                E_leak: list
                    List of leakage errors
        '''
        # # Identify detuning in MHz
        # det = int(1e3*(self.qubits[ctrl]['w']-self.qubits[tgt]['w']+ 0.0001)/(2*np.pi))

        # # Load list of precalibrated gate times
        # with open("./pickles/CR_gate_raw_fidelity/cnot_times_{}_MHz.pkl".format(det),'rb')as f:
        #     ts = pickle.load(f)

        with open(calib_path,'rb') as f:
            ts = pickle.load(f)

        # Define lists to be populated
        E_list = []
        E_CP_list = []
        E_T_list = []
        E_C_list = []
        E_specs_list = []
        E_leak_list = []

        if no_progress_bar:
            iterable = ts
        else:
            iterable = tqdm(ts)
        # For each configuration, get fidelities
        for i in iterable:

            args[t_key] = ts[i]
            args[E_key] = 1e-3*i*2*np.pi
            #print("I am batman")
            t = np.arange(0,args[t_key],args[t_step_key])
            #print(len(t))

            if E_max:
                if i>E_max or i<E_min:
                    continue

            M = self.get_M(ctrl,tgt,drive_frequency,pulse_shape,t,args)

            if no_CP:
                E, E_T, E_C, E_specs, E_leak =self.get_new_error_budget(M, use_optimizer = use_optimizer,use_zero_initial_values=use_zero_initial_values, no_CP = no_CP)
            else:
                E, E_CP, E_T, E_C, E_specs, E_leak = self.get_new_error_budget(M, use_optimizer = use_optimizer,use_zero_initial_values=use_zero_initial_values, no_CP = no_CP)
                E_CP_list.append(E_CP)



            E_list.append(E)
            E_T_list.append(E_T)
            E_C_list.append(E_C)
            E_specs_list.append(E_specs)
            E_leak_list.append(E_leak)

        results = E_list, E_T_list, E_C_list, E_specs_list, E_leak_list

# First, make sure they are same length
        lens = [len(l) for l in results]
        print(f"Original lengths: {lens}")

        max_len = max(lens)
        results_fixed = []

        for row in results:
            new_row = []
            for x in row:
                if isinstance(x, list):
                    if len(x) == 0:
                        new_row.append(0.0)
                    else:
                        new_row.append(np.mean(x))
                elif isinstance(x, np.ndarray):
                    if x.size == 0:
                        new_row.append(0.0)
                    else:
                        new_row.append(np.mean(x))
                else:
                    new_row.append(x)
    # Pad each row to same length if needed
            if len(new_row) < max_len:
                new_row += [0.0] * (max_len - len(new_row))
            results_fixed.append(new_row)

        arr = np.asarray(results_fixed)
        print("Shape:", arr.shape)
        print("Dtype:", arr.dtype)
        results_list = [list(row) for row in results_fixed]
        print("cow")


# Now transpose is safe
        results_transposed = np.transpose(np.asarray(results_list))
        print("Transposed shape:", results_transposed.shape)

        #print("h5")

        
        if no_CP:
            print("yes")
            E_list, E_T_list, E_C_list, E_specs_list, E_leak_list = results_transposed.T
            return E_list, E_T_list, E_C_list, E_specs_list, E_leak_list
            print("Length:", len(result))
        else:
            print("yes1")
            E_list, E_CP_list, E_T_list, E_C_list, E_specs_list,E_leak_list = results_transposed.T
            return E_list, E_CP_list, E_T_list, E_C_list,E_specs_list, E_leak_list


    '''########################## Parallelised Version - Jay #########################################'''
    def E_vs_F_new_error_budget_parallel(self,ctrl,tgt,drive_frequency,calib_path, pulse_shape,args = None,E_key = 'Emax',t_key ='tp',t_step_key = 't_step', use_optimizer = True,use_zero_initial_values = False, E_max = None, E_min = None,no_progress_bar = False, no_CP = True):

        '''
            Method to find Fidelity and Error Budget vs Drive Strength, for a pre-calibrated list (E vs t) of drive-strengths
            This uses the new definitions

            Arguments:
                ctrl, tgt: int
                    indices of ctrl and tgt qubit
                drive_frequency: float
                    Drive Frequency in Grad/s
                calib_path: string
                    Path to the pickle file with calibration times
                pulse_shape: function
                    Function that returns pulse value as a function of time
                args: dict
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key: hashable object
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key: hashable object
                    args[t_key] = Pulse length
                    Default: 'tp'
                t_step_key: hashable object
                    args[t_step_key] = Time sampling step
                    Default: 't_step'
                use_optimizer: Bool
                    If True, the optimizer is used. If False, the analytical solver is used
                    Default: True
                use_zero_initial_values: Bool
                    If True, the optimizer is given zero initial conditions
                    If False, the optimizer is given analytical initial conditions
                    Default: True
                E_max: float
                    Maximum value of drive strength to which the computation is performed
                    Default: None
                E_min: float
                    Minimum value of drive strength to which the computation is performed
                    Default: None
                no_progress_bar: Bool
                    If true, a progress bar is activated
                    Default: False
                no_CP: Bool
                    If True, it doesn't calculate conditional phase error, and lumps this together with target rotation error
                    If False, it calculates it and returns it
                    Default: True

            Returns:
                Elements of each list correspond to different drive strengths
                E: list
                    List of CR gate errors
                E_CP: list
                    List of conditional phase errors
                    Not returned if no_CP if True
                E_T: list
                    List of target rotation errors
                E_C: list
                    List of control rotation errors
                E_specs: list
                    Contains lists of each spectator's rotation error
                E_leak: list
                    List of leakage errors
        '''
        # # Identify detuning in MHz
        # det = int(1e3*(self.qubits[ctrl]['w']-self.qubits[tgt]['w']+ 0.0001)/(2*np.pi))

        # # Load list of precalibrated gate times
        # with open("./pickles/CR_gate_raw_fidelity/cnot_times_{}_MHz.pkl".format(det),'rb')as f:
        #     ts = pickle.load(f)

        with open(calib_path,'rb') as f:
            ts = pickle.load(f)


        if no_progress_bar:
            iterable = ts
        else:
            iterable = tqdm(ts)

    

        #print("h1")
        def process(i):
            args[t_key] = ts[i]
            args[E_key] = 1e-3 * i * 2 * np.pi
            t = np.arange(0, args[t_key], args[t_step_key])
            #t_list.append(t)
            #print(len(ti))
            #print("h2")
            if E_max:
                if i>E_max or i<E_min:
                    print("Fix limits")
                    return None

            #t = np.array(t_list, dtype=object)
            #print("h3")
            M = self.get_M(ctrl,tgt,drive_frequency,pulse_shape,t,args)

            if no_CP:
                E, E_T, E_C, E_specs, E_leak =self.get_new_error_budget(M, use_optimizer = use_optimizer, use_zero_initial_values=use_zero_initial_values, no_CP = no_CP)
                return E, E_T, E_C, E_specs, E_leak
            else:
                E, E_CP, E_T, E_C, E_specs, E_leak =self.get_new_error_budget(M, use_optimizer = use_optimizer,use_zero_initial_values=use_zero_initial_values, no_CP = no_CP)
                return E, E_CP, E_T, E_C, E_specs, E_leak

        # For each configuration, get fidelities
        results = Parallel(n_jobs=-3)(delayed(process)(i) for i in iterable)
        #print("h5")
        results_fixed = []
        for row in results:
            new_row = []
            for x in row:
        # If it's a Python list
                if isinstance(x, list):
                    if len(x) == 0:
                        new_row.append(0.0)
                    else:
                        new_row.append(np.mean(x))  # Use mean of the list
                   # If it's a NumPy array

                elif isinstance(x, np.ndarray):
                    if x.size == 0:
                        new_row.append(0.0)
                    else:
                        new_row.append(np.mean(x))  # Use mean of the array
        # If it's scalar, keep it
                else:
                    new_row.append(x)
            results_fixed.append(new_row)  # Already a list, so no tuple needed


        print(results)
        arr = np.asarray(results_fixed)
        print(arr.shape)
        print(arr.dtype)
        results_list = [list(row) for row in results_fixed]

        results = np.transpose(np.asarray(results_list))
        #print("h5")

        if no_CP:
            E_list, E_T_list, E_C_list, E_specs_list, E_leak_list = results
            return E_list, E_T_list, E_C_list, E_specs_list, E_leak_list
        else:
            E_list, E_CP_list, E_T_list, E_C_list, E_specs_list,E_leak_list = results
            return E_list, E_CP_list, E_T_list, E_C_list,E_specs_list, E_leak_list

    '''###################################### End of addition by Jay #######################################'''
    '''########################## Old Error Budget #############################################'''

    def generate_angle_LHS(self):
        '''
            Method to return the LHS used to analytically estimate the phases acquired by each qubit.

            Arguments
            ---------
                None

            Returns
            -------
                LHS (numpy 2D array):
                    Array consisting of LHS used to estimate phases acquired by each qubit using least square estimation
        '''
        LHS = np.zeros((2**(self.N-1),2*(self.N-1)))
        for i in range(2**(self.N-1)):
            lhs = [int(j) for j in np.binary_repr(i,(self.N-1))]
            for ind,j in enumerate(lhs):
                LHS[i][2*ind] = j^1
                LHS[i][2*ind+1] = j^0
        return LHS

    def generate_full_rank_angle_LHS(self, LHS):
        '''
            Function to return a list of full rank matrices which are subsets of the actual phase computation LHS

            Arguments
            ---------
                None

            Returns
            -------
                l (list):
                    List containing lists of boolean values, which select full rank subsets of the LHS matrix
        '''
        d = sym.ntheory.multinomial_coefficients(LHS.shape[0],self.N)
        # print(d)l
        l = []
        for i in d:
            test = True
            for j in i:
                if j>1:
                    test = False
            if test:
                ind_l = [bool(j) for j in i]
                if np.linalg.matrix_rank(LHS[ind_l])>=self.N:
                    l.append([bool(j) for j in i])
        return l

    def get_phases(self,LHS,RHS):
        '''
            Returns the phases acquired by each qubit, given the LHS and RHS of theta

            Arguments
            ---------
                LHS, RHS (Numpy Arrays):
                    LHS, RHS used to estimate phases acquired by each qubit

            Returns
            -------
                theta_final (Numpy Array):
                    Phases acquired by each qubit
        '''
        l = self.generate_full_rank_angle_LHS(LHS)
        theta_final_l = []
        for i in l:
            LHS_mod = LHS[i]
            RHS_mod = RHS[i]
            theta = np.linalg.lstsq(LHS_mod,RHS_mod)
            theta_final = theta[0]#[::-1]

            theta_final_l.append(theta_final)
        theta_final = theta_final_l[self.full_rank_choice]
        return theta_final

    def get_angles(self,M,print_vals = False, low_ind = 0, high_ind = -1, get_all_theta = False):
        '''
            Finds the parameters (rotation angles and phases) of the closest Unitary from the CR Unitary Family

            Arguments
            ---------
                M (Qobj):
                    Propagator, as projected into computational subspace
                    Should be Permuted such that control and target are penultimate and final indices
                print_vals (Bool):
                    If True, function prints all the values of phi,theta estimated from the matrix
                    Use to debug
                    Default: False
                get_all_theta (Bool):
                    If True, gives all theta values to get U_CR_CP

            Returns
            -------
                phi0_avg (float):
                    Average Rotation angle (in radians) of the Target Qubit, when control is in |0>
                    Averaged over 2**(N-2) states of other spectator qubits
                phi1_avg (float):
                    Average Rotation angle (in radians) of the Target Qubit, when control is in |1>
                    Averaged over 2**(N-2) states of other spectator qubits
                theta_final (Numpy 1D array):
                    Dimension (2**(N-1),1)
                    theta_final[0::2] - Contains total phases accumulated when control is in |0>
                    theta_final[1::2] - Contains total phases accumulated when control is in |1>
                    Total Phase accumulated is the sum of the phases accumulate by the control and spectator qubits
        '''

        #M = np.array(M.full() , dtype = complex)
        M = np.array(M.full() , dtype = complex)
        phi0 = np.zeros(2**(self.N-2))
        phi1 = np.zeros(2**(self.N-2))
        theta0 = np.zeros(2**(self.N-2))
        theta1 = np.zeros(2**(self.N-2))

        # Extract Parameters
        for i in range(2**(self.N-2)):
            ind = 4*i

            phi0[i] = -np.angle((M[ind+0][ind+0] + M[ind+1][ind+1] + M[ind+0][ind+1] + M[ind+1][ind+0])/(M[ind+0][ind+0] + M[ind+1][ind+1] - M[ind+0][ind+1] - M[ind+1][ind+0]))
            phi1[i] = -np.angle((M[ind+2][ind+2] + M[ind+3][ind+3] + M[ind+2][ind+3] + M[ind+3][ind+2])/(M[ind+2][ind+2] + M[ind+3][ind+3] - M[ind+2][ind+3] - M[ind+3][ind+2]))

            theta0[i] = np.angle((M[ind+0][ind+0] + M[ind+1][ind+1])*np.cos(phi0[i]/2) + 1j*(M[ind+0][ind+1] + M[ind+1][ind+0])*np.sin(phi0[i]/2))
            theta1[i] = np.angle((M[ind+2][ind+2] + M[ind+3][ind+3])*np.cos(phi1[i]/2) + 1j*(M[ind+2][ind+3] + M[ind+3][ind+2])*np.sin(phi1[i]/2))

        # Average phi
        phi0_avg = np.mean(phi0)
        phi1_avg = np.mean(phi1)

        if get_all_theta:
            return phi0_avg, phi1_avg, theta0, theta1

        # Extract thetas
        LHS = self.generate_angle_LHS()
        RHS = np.zeros(2**(self.N-1))
        for i in range(2**(self.N-1)):
            if i%2 == 0:
                RHS[i] = theta0[int(i/2)]
            else:
                RHS[i] = theta1[int(i/2)]

        # Save non-truncated LHS,RHS for convenience
        self.LHS = LHS
        self.RHS = RHS

        # Estimate theta from the angles extracted
        theta_final = self.get_phases(self.LHS,self.RHS)


        # Print Values as per input
        if print_vals:
            print("phi0 array: ")
            print(np.array(phi0)*180/np.pi)
            print("phi1 array: ")
            print(np.array(phi1)*180/np.pi)
            print("theta0 array: ")
            print(np.array(theta0)*180/np.pi)
            print("theta1 array: ")
            print(np.array(theta1)*180/np.pi)


            print("phi0 avg = ",phi0_avg*180/np.pi)
            print("phi1 avg= ",phi1_avg*180/np.pi)

            print("LHS = \n")
            print(np.abs(LHS))
            print("RHS = \n")
            print(RHS*180/(np.pi))

            print("theta_final \n", theta_final*180/(np.pi))
            print("RHS estimated: ", self.LHS@theta_final *180/np.pi)

        return phi0_avg, phi1_avg, theta_final

    def get_U_CR(self,M,print_vals = False):
        '''
            Returns Closest Unitary Matrix from the CR Gate Family for a given propagator
            Uses the Analytical method

            Arguments
            ---------
                M (Qobj):
                    Propagator, as projected into computational subspace
                    Should be Permuted such that control and target are penultimate and final indices
                print_vals (Bool):
                    If True, function prints all the values of phi,theta estimated from the matrix
                    Use to debug
                    Default: False

            Returns
            -------
                U_CR (Qobj):
                    Closest Unitary Matrix from the CR Gate Family
        '''

        # Extract Angles
        phi0,phi1,theta = self.get_angles(M, print_vals)

        # Generate CR Matrix in a relevant tensor product structure

        # Tensor multiply all the phases of spectator qubits first
        phase = np.eye(1,dtype = complex)
        for i in range(self.N-2):
            mat = np.zeros((2,2),dtype = complex)
            mat[0][0] = np.exp(1j*theta[2*i])
            mat[1][1] = np.exp(1j*theta[2*i+1])
            phase = np.kron(phase,mat)

        # Create Control Target Matrix
        ct = np.zeros((4,4), dtype = complex)
        thetac_0 = theta[-2]
        thetac_1 = theta[-1]


        ct[0][0] = np.exp(1j*thetac_0)*np.cos(phi0/2)
        ct[1][1] = np.exp(1j*thetac_0)*np.cos(phi0/2)

        ct[2][2] = np.exp(1j*thetac_1)*np.cos(phi1/2)
        ct[3][3] = np.exp(1j*thetac_1)*np.cos(phi1/2)

        ct[1][0] = -1j*np.exp(1j*thetac_0)*np.sin(phi0/2)
        ct[0][1] = -1j*np.exp(1j*thetac_0)*np.sin(phi0/2)

        ct[3][2] = -1j*np.exp(1j*thetac_1)*np.sin(phi1/2)
        ct[2][3] = -1j*np.exp(1j*thetac_1)*np.sin(phi1/2)


        # Tensor multiply phases and control target matrix
        U_CR = np.kron(phase,ct)
        U_CR = qt.Qobj(U_CR, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape = (2**self.N,2**self.N))
        return U_CR

    '''########################## Single Qubit Gate Functions##################################'''

    def get_U_RX_from_angles(self,phi, theta,print_U_matrix = False, print_vals = False):
        '''
            Returns Closest Unitary Matrix from the RX Gate Family for a given propagator

            Arguments
            ---------
                phi: float
                    Rotation of the qubit
                    Angles are in radians
                theta: Numpy 1D array of floats
                    N-1 dimensional array, with each angle (radians) corresponding to phase picked up by each qubit
                print_U_matrix: Bool
                    If True, function prints the matrix U which is created.
                    Use to debug
                    Default - False
                print_vals: Bool
                    If True, function prints all the values of phi,theta given
                    Use to debug
                    Default - False

            Returns
            -------
                U_RX (Qobj):
                    Closest Unitary Matrix from the RX Gate Family
        '''

        # Generate RX Matrix in a relevant tensor product structure
        # Tensor multiply all the phases of spectator qubits first
        phase = np.eye(1,dtype = complex)
        for i in range(self.N-2):
            mat = np.zeros((2,2),dtype = complex)
            mat[0][0] = 1
            mat[1][1] = np.exp(1j*theta[i])
            phase = np.kron(phase,mat)

        # Create RX Matrix (Code reused from CR Gate)
        ct = np.zeros((4,4), dtype = complex)
        # thetac_0 = theta[-2]
        thetac_1 = theta[-1]


        ct[0][0] = np.cos(phi/2)
        ct[1][1] = np.cos(phi/2)

        ct[2][2] = np.exp(1j*thetac_1)*np.cos(phi/2)
        ct[3][3] = np.exp(1j*thetac_1)*np.cos(phi/2)

        ct[1][0] = -1j*np.sin(phi/2)
        ct[0][1] = -1j*np.sin(phi/2)

        ct[3][2] = -1j*np.exp(1j*thetac_1)*np.sin(phi/2)
        ct[2][3] = -1j*np.exp(1j*thetac_1)*np.sin(phi/2)

        # Tensor multiply phases and control target matrix
        U_RX = np.kron(phase,ct)
        #U_RX = qt.Qobj(U_RX, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape = (2**self.N,2**self.N))
        U_RX = qt.Qobj(U_RX, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]])


        if print_U_matrix:
            self.print_U(U_RX)

        if print_vals:

            print("phi0 avg = ", phi*180/np.pi)

            print("theta_final \n", theta*180/(np.pi))


        return U_RX

    def get_f_blackbox_RX(self,angles,M):
        '''
            Function that returns the fidelity given all the angles estimated

            Arguments
            ---------
                angles: array like, contains floats
                    N dimensional array. First element contains phi (angle of rotation of qubit)
                    Rest of the elements contain theta (phases picked up by spectators)

                M: Qobj
                    Unitary Propagator

            Returns
            -------
                -fidelity: float
                    -1*(Fidelity between matrix constructed from angles and propagator M)
        '''


        U_RX = self.get_U_RX_from_angles(angles[0], angles[1:])

        return -1*self.get_f_qt(U_RX,M)

    def get_angles_RX_optimal(self,M, use_zero_initial_values = False):
        '''
            Function to compute the angles of best fit for the RX gate from the propagator M

            Arguments
            ---------
                M: Qobj
                    Unitary propagator, projected into the computational subspace
                    Tensor order should be appropriate (spec qubits x tgt qubit)
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values computed using the older methods are given to optimizer
                    Default - False

            Returns
            -------
                phi: float
                    Rotation of the target about the X axis
                theta: array of floats
                    (N-1) Array of float numbers which correspond to phases picked up by each spectator
        '''


        phi0,phi1, theta = self.get_angles(M)
        phi = (phi0+phi1)*0.5

        theta_diff = theta[1::2] - theta[::2]
        angles_initial = [phi] + list(theta_diff)


        if use_zero_initial_values:
            angles_initial = [0] + [0]*(self.N - 1)

        res = scipy.optimize.minimize(self.get_f_blackbox_RX,angles_initial,args = (M), method = 'Nelder-Mead')

        phi = res.x[0]
        theta = res.x[1:]

        return phi, theta

    def get_U_RX_optimizer(self,M, use_zero_initial_values = False):
        '''
            Function to create the closest matrix in the RX family to the propagator

            Arguments
            ---------
                M: Qobj
                    Propagator of the gate, projected into the computational subspace
                    Tensor order should be (spec qubits x tgt)
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer

            Returns
            -------
                U_RX: Qobj
                    Closest unitary in the RX family
        '''

        phi, theta = self.get_angles_RX_optimal(M,use_zero_initial_values = use_zero_initial_values)
        U_RX = self.get_U_RX_from_angles(phi, theta)
        return U_RX

    def get_U_RX_CP(self,M,print_vals = False):
        '''
            Returns Closest Unitary Matrix from the RX Gate Family for
a given propagator, ignoring conditional phase

            Arguments
            ---------
                M (Qobj):
                    Propagator, as projected into computational subspace
                    Should be Permuted such that control and target are penultimate and final indices
                print_vals (Bool):
                    If True, function prints all the values ofphi,theta estimated from the matrix
                    Use to debug
                    Default: False

            Returns
            -------
                U_RX (Qobj):
                    Closest Unitary Matrix from the RX Gate Family,ignoring conditional phase
        '''

        # Extract Angles
        phi0,phi1,theta0, theta1 = self.get_angles(M, print_vals,get_all_theta = True)
        phi = (np.abs(phi0)+np.abs(phi1))*0.5
        phi0 = np.sign(phi0)*phi
        phi1 = np.sign(phi1)*phi
        U_RX_CP = np.zeros((2**self.N,2**self.N), dtype = complex)
        for i in range(2**(self.N-2)):

            ind_0 = 4*i
            U_RX_CP[ind_0][ind_0] = np.exp(1j*theta0[i])*np.cos(phi0/2)
            U_RX_CP[ind_0][ind_0+1] = -1j*np.exp(1j*theta0[i])*np.sin(phi0/2)
            U_RX_CP[ind_0+1][ind_0] = -1j*np.exp(1j*theta0[i])*np.sin(phi0/2)
            U_RX_CP[ind_0+1][ind_0+1] = np.exp(1j*theta0[i])*np.cos(phi0/2)

            ind_1 = 4*i+2
            ind_0 = 4*i
            U_RX_CP[ind_1][ind_1] = np.exp(1j*theta1[i])*np.cos(phi1/2)
            U_RX_CP[ind_1][ind_1+1] = -1j*np.exp(1j*theta1[i])*np.sin(phi1/2)
            U_RX_CP[ind_1+1][ind_1] = -1j*np.exp(1j*theta1[i])*np.sin(phi1/2)
            U_RX_CP[ind_1+1][ind_1+1] = np.exp(1j*theta1[i])*np.cos(phi1/2)

        # Convert to Qobj and Return
        #U_RX_CP = qt.Qobj(U_RX_CP, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape =(2**self.N,2**self.N))
        U_RX_CP = qt.Qobj(U_RX_CP, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]])

        return U_RX_CP

    def get_U_X_Rotation(self,M,print_vals = False):
        '''
            Returns Closest Unitary Matrix from the X Rotation Family for a given propagator
            Uses the Analytical Method
            Arguments
            ---------
                M (Qobj):
                    Propagator, as projected into computational subspace
                    Should be Permuted such that control and target are penultimate and final indices
                print_vals (Bool):
                    If True, function prints all the values of phi,theta estimated from the matrix
                    Use to debug
                    Default: False

            Returns
            -------
                U_X (Qobj):
                    Closest Unitary Matrix from the X Rotation Family
        '''

        # Extract Angles
        phi0,phi1,theta = self.get_angles(M, print_vals)

        # Average angle of rotation about X axis
        phi = 0.5*(phi0+phi1)

        # Generate X Rotation in a relevant tensor product structure

        # Tensor multiply all the phases of spectator qubits first
        phase = np.eye(1,dtype = complex)
        for i in range(self.N-2):
            mat = np.zeros((2,2),dtype = complex)
            mat[0][0] = np.exp(1j*theta[2*i])
            mat[1][1] = np.exp(1j*theta[2*i+1])
            phase = np.kron(phase,mat)

        # Create Control Target Matrix
        ct = np.zeros((4,4), dtype = complex)
        thetac_0 = theta[-2]
        thetac_1 = theta[-1]


        ct[0][0] = np.exp(1j*thetac_0)*np.cos(phi/2)
        ct[1][1] = np.exp(1j*thetac_0)*np.cos(phi/2)

        ct[2][2] = np.exp(1j*thetac_1)*np.cos(phi/2)
        ct[3][3] = np.exp(1j*thetac_1)*np.cos(phi/2)

        ct[1][0] = -1j*np.exp(1j*thetac_0)*np.sin(phi/2)
        ct[0][1] = -1j*np.exp(1j*thetac_0)*np.sin(phi/2)

        ct[3][2] = -1j*np.exp(1j*thetac_1)*np.sin(phi/2)
        ct[2][3] = -1j*np.exp(1j*thetac_1)*np.sin(phi/2)


        # Tensor multiply phases and control target matrix
        U_X = np.kron(phase,ct)
        U_X = qt.Qobj(U_X, dims = [[2 for i in range(self.N)],[2 for i in range(self.N)]], shape = (2**self.N,2**self.N))
        return U_X

    def get_F_X(self,tgt,drive_frequency, pulse_shape, t, args = None):
        '''
            Finds the X Rotation Gate Fidelity on a specific target qubit,
            for a given drive frequency and pulse
            Uses the Analytical Method

            Arguments
            ---------
                ctrl, tgt (int)
                    Indices of the Control and Target Qubit (0....N-1)
                drive_frequency (float)
                    Angular frequency of the drive, in Grad/s
                pulse_shape (Python Function)
                    A function which takes time as an input and gives pulse value at that time
                t (Numpy 1D array)
                    An array of times through which the evolution is done. The pulse shape is sampled at these times.
                args (dict)
                    A dictionary containing the arguments to be passed to the pulse shape function
                    Default: None

            Returns
            -------
                F (float):
                    Fidelity of the gate
        '''
        ctrl = tgt
        M = np.array(self.get_M(ctrl,tgt,drive_frequency,pulse_shape,t,args), dtype = complex)
        U_X = np.array(self.get_U_X_Rotation(M), dtype = complex)
        F = self.get_f_np(M,U_X)
        return F

    def calibrate_X_phi(self,tgt,drive_frequency,pulse_shape,args,E_key = 'Emax',t_key = 'tp',E_list = np.arange(3,90,3),t_list = np.arange(50,150,25), use_optimizer = True, use_zero_initial_values = False):
        '''
            Method to extract angle of rotation of target for varying drive strengths a pulse lengths.
            Can be used to calibrate the X rotation gate. Works only if the pulse shape function has a flat top,
            and symmetric rise and fall which are a fraction of pulse length.

            Arguments
            ---------
                tgt (int):
                    index tgt qubit
                drive_frequency (float):
                    Drive Frequency in Grad/s
                pulse_shape (function):
                    Function that returns pulse value as a function of time
                args (dict):
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key (hashable object):
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key (hashable object):
                    args[t_key] = Pulse length
                    Default: 'tp'
                E_list (1D numpy array):
                    List of drive strengths in MHz
                    Default: np.arange(3,90,3)
                t_list (1D numpy array):
                    List of pulse lengths in nanoseconds
                    Default: np.arange(50,200,25)
                use_optimizer: Bool
                    If True, angles are extracted using the optimizer
                    If False, angles are extracted analytically
                    Default - True
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer

            Returns
            -------
                phi (dict):
                    phi[drive_strength] = list of angles of rotation corresponding to t_list
        '''
        # Dictionaries to be returned
        phi = {}

        # Run through E_list and t_list
        for i in tqdm(E_list):
            phi[i] = []
            args[E_key] = i*1e-3*2*np.pi
            for j in t_list:
                args[t_key] = j
                t = np.linspace(0,j,600)
                # Get propagator
                M = self.get_M(tgt,tgt,drive_frequency,pulse_shape,t,args)
                # Get angles
                if use_optimizer:
                    phi_opt, _ = self.get_angles_RX_optimal(M, use_zero_initial_values = use_zero_initial_values)
                    phi[i].append(phi_opt)
                else:
                    a,b,_ = self.get_angles(M)
                    phi[i].append(0.5*(a+b))

            phi[i] = np.array(phi[i])

        return phi

    def calibrate_X_t(self,angle,tgt,drive_frequency,pulse_shape,args,E_key = 'Emax',t_key = 'tp',E_list = np.arange(3,90,3),t_list = np.arange(50,150,25), use_optimizer = True, use_zero_initial_values = False):
        '''
            Method to calibrate the RX gate. Works only if the pulse shape function has a flat top,
            and symmetric rise and fall which are a fraction of pulse length. Finds time taken for
            rotation by a specified angle.

            Arguments
            ---------
                angle (float):
                    RX Angle for which the gate must be calibrated in radians
                tgt (int):
                    index of target qubit
                drive_frequency (float):
                    Drive Frequency in Grad/s
                pulse_shape (function):
                    Function that returns pulse value as a function of time
                args (dict):
                    Dictionary with key value pairs specifying arguments to pulse_shape function.
                E_key (hashable object):
                    args[E_key] = Max amplitude of pulse
                    Default: 'Emax'
                t_key (hashable object):
                    args[t_key] = Pulse length
                    Default: 'tp'
                E_list (1D numpy array):
                    List of drive strengths in MHz
                    Default: np.arange(3,90,3)
                t_list (1D numpy array):
                    List of pulse lengths in nanoseconds
                    Default: np.arange(50,200,25)
                use_optimizer: Bool
                    If True, angles are extracted using the optimizer
                    If False, angles are extracted analytically
                    Default - True
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer

            Returns
            -------
                ts (list):
                    List of pulse lengths correspoding to E_list
                phi (dict):
                    phi[drive_strength] = list of angles of rotation corresponding to t_list
        '''
        # Get angles
        phi = self.calibrate_X_phi(tgt,drive_frequency,pulse_shape,args,E_key,t_key,E_list,t_list,use_optimizer = use_optimizer, use_zero_initial_values = use_zero_initial_values)

        # List of calibrated times, corresponding to E_list
        ts = []

        # Extrapolate time evolution and get pulse time
        for i in phi:
            m,b = np.polyfit(t_list[1:4],phi[i][1:4],1)
            trx = np.roots([-m,-b+angle])
            if len(trx)==0:
                continue
            ts.append(trx[0])
        return ts,phi

    def get_new_error_budget_RX(self,M, use_optimizer = True,  use_zero_initial_values = False, no_CP = True):
        '''
            Function to get error budget of a given propagator in the computational subspace, as per new definitions
            For the RX Gate
            Arguments
            ---------
                M: Qobj
                    Unitary propagator projected into the computational subspace
                use_optimizer: Bool
                    If True, the optimizer is used to find angles and closest U_CR
                    If False, the angles are computed analytically
                use_zero_initial_values: Bool
                    If True, zero initial values are given to the optimizer
                    If False, analytical initial values are given to the optimizer
                no_CP: Bool
                    If True, it doesn't calculate conditional phase error, and lumps this together with target rotation error
                    If False, it calculates it and returns it
                    Default: True

            Returns
            -------
                E: float
                    RX gate error
                E_CP: float
                    Conditional phase errors (returned only if no_CP = False)
                E_T: float
                    Target rotation errors
                E_specs: list of float
                    List of each spectator's rotation error
                E_leak: float
                    Leakage errors
        '''
        # Get closest CR Unitary
        if use_optimizer:
            U_RX = self.get_U_RX_optimizer(M,use_zero_initial_values = use_zero_initial_values)
        else:
            U_RX = self.get_U_X_Rotation(M)

        # Get closest RX Unitary which allows conditional phase
        U_RX_CP = self.get_U_RX_CP(M)

        # Get closest unitary where target has arbitrary rotation
        U_TU = self.get_U_CR_N(M,1)

        # Find all fidelity metrics
        E_U_RX = 1 - self.get_f_qt(M,U_RX)
        E = E_U_RX

        E_U_RX_CP = 1 - self.get_f_qt(M,U_RX_CP)
        E_CP = E_U_RX - E_U_RX_CP

        E_U_TU = 1 - self.get_f_qt(M,U_TU)
        if no_CP:
            E_T = E_U_RX - E_U_TU
        else:
            E_T = E_U_RX_CP - E_U_TU


        E_specs = []
        for i in range(1,self.N):
            E_specs.append(self.get_f_qt(M,self.get_U_CR_N(M,i+1)) - self.get_f_qt(M,self.get_U_CR_N(M,i)))

        E_leak = 1 - self.get_f_qt(M,self.get_U_CR_N(M,self.N))

        if no_CP:
            return E, E_T, E_specs, E_leak
        else:
            return E, E_CP, E_T, E_specs, E_leak


    def E_vs_F_new_error_budget_RX(self,tgt,drive_frequency,calib_path, pulse_shape,args = None,E_key = 'Emax',t_key = 'tp',t_step_key = 't_step', use_optimizer = True, use_zero_initial_values = False, no_CP= True):
         '''
             Method to find Fidelity and Error Budget vs Drive Strength, for a pre-calibrated list (E vs t) of drive-strengths
             This uses the new definitions

             Arguments
             ---------
                 tgt: int
                     index of the target qubit
                 drive_frequency: float
                     Drive Frequency in Grad/s
                 calib_path: string
                     Path to the pickle file containing single qubit gate calibration times
                 pulse_shape: function
                     Function that returns pulse value as a function of time
                 args: dict
                     Dictionary with key value pairs specifyingarguments to pulse_shape function.
                 E_key: hashable object
                     args[E_key] = Max amplitude of pulse
                     Default: 'Emax'
                 t_key: hashable object
                     args[t_key] = Pulse length
                     Default: 'tp'
                 t_step_key: hashable object
                     args[t_step_key] = Time sampling step
                     Default: 't_step'
                 use_optimizer: Bool
                     If True, the optimizer is used. If False, the analytical solver is used
                     Default: True
                 use_zero_initial_values: Bool
                     If True, the optimizer is given zero initial conditions
                     If False, the optimizer is given analytical initial conditions
                     Default: True
                no_CP: Bool
                    If True, it doesn't calculate conditional phase error, and lumps this together with target rotation error
                    If False, it calculates it and returns it
                    Default: True

             Returns
             -------
                 Elements of each list correspond to different drive strengths
                 E_list: list
                     List of CR gate errors
                 E_CP_list: list
                     List of conditional phase errors
                 E_T_list: list
                     List of target rotation errors
                 E_specs_list: list
                     Contains lists of each spectator's rotation error
                 E_leak_list: list
                     List of leakage errors
         '''

         # Load list of precalibrated gate times
         path = calib_path
         # path = "./pickles/CR_gate_raw_fidelity/RX_times.pkl"
         # path ="./pickles/CR_gate_raw_fidelity/RX_times_0.01_25_101_points.pkl"
         with open(path,'rb') as f:
            ts = pickle.load(f)

         # Define lists to be populated
         E_list = []
         E_CP_list = []
         E_T_list = []
         E_C_list = []
         E_specs_list = []
         E_leak_list = []

         drive_list = list(ts.keys())
         t_list = list(ts.values())
         iterable = enumerate(t_list)
         # For each configuration, get fidelities

         for ind,i in tqdm(iterable):
             args[t_key] = i
             args[E_key] = 1e-3*drive_list[ind]*2*np.pi
             t = np.arange(0,args[t_key],0.5)
             M = self.get_M(tgt,tgt,drive_frequency,pulse_shape,t,args)
             #M = self.get_M(tgt,tgt,drive_frequency,pulse_shape,t,args).full()
             if no_CP:
                 E, E_T, E_specs, E_leak = self.get_new_error_budget_RX(M,use_optimizer = use_optimizer,use_zero_initial_values = use_zero_initial_values, no_CP = no_CP)
             else:
                 E, E_CP, E_T, E_specs, E_leak = self.get_new_error_budget_RX(M,use_optimizer = use_optimizer, use_zero_initial_values = use_zero_initial_values, no_CP = no_CP)
                 E_CP_list.append(E_CP)

             E_list.append(E)
             E_T_list.append(E_T)
             E_specs_list.append(E_specs)
             E_leak_list.append(E_leak)

         if no_CP:
             return E_list, E_T_list, E_specs_list, E_leak_list
         else:
             return E_list, E_CP_list, E_T_list, E_specs_list, E_leak_list


#============= Effective Hamiltonian Code (Sumeru)================================
no_of_qubits = 2
def binomial(n, k): #calculates binomial coefficients
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0
#=========================================================================================
def twoqubit_h(dim, w1, w2, del1, del2, g12):
    #this function defines the two qubit hamiltonian with delta being anharmonicities
    #the exchange coupling is given by g12
    a1 = qt.tensor(qt.destroy(dim), qt.qeye(dim))
    a1dag = qt.tensor(qt.create(dim), qt.qeye(dim))
    a2 = qt.tensor(qt.qeye(dim), qt.destroy(dim))
    a2dag = qt.tensor(qt.qeye(dim), qt.create(dim))
    H1 = w1*(a1dag*a1) + (del1/2)*((a1dag*a1)*(a1dag*a1)-(a1dag*a1))
    H2 =  w2*(a2dag*a2) + (del2/2)*((a2dag*a2)*(a2dag*a2)-(a2dag*a2))
    Hc = g12*(a1dag*a2 + a1*a2dag)
    Htot = H1 + H2 + Hc
    return Htot
#=========================================================================================
# The ordering of states in qutip is in number_base(n) format as in
# {00, 01, 02, ..., 0d, 10, 11, ..., 1d, ..., d0, ..., dd}
# We shall first truncate the Hamiltonian to limit the maximum numberof excitations
# Next we rearrange the Hamiltonian in the binomial pyramid format given below:
# {00, 01, 10, 02, 11, 20 rest}
#=========================================================================================
def red_h(dim, w1, w2, del1, del2, g12):
    d_hs = binomial(dim + no_of_qubits - 1, no_of_qubits ) #dimension of Hilbert Space
    y = np.zeros(d_hs, dtype =int)
    l = 0
    for i in range(0, dim):
        for j in range(0, i+1):
            y[l] = dim*j + (i - j)
            l = l+1
    empty2d = np.zeros([d_hs, d_hs], dtype = complex)
    base_ham = twoqubit_h(dim, w1, w2, del1, del2, g12)
    for i1 in range(0, d_hs):
        for j1 in range(0, d_hs):
            empty2d[i1, j1] = base_ham[y[i1], y[j1]]
    return empty2d
#=========================================================================================
"Dressed Hamiltonian"
#=========================================================================================
def zz_khz(dim, w1, w2, del1, del2, g12):
    val, vec = np.linalg.eig(red_h(dim, w1, w2, del1, del2, g12))
    vec_arr = np.argmax(vec, axis = 0) #eigenvectors along columns
    val_sor_ind = np.argsort(vec_arr)
    val_incr = val[val_sor_ind]
    zz_split_tot = val_incr[4] - val_incr[2] - val_incr[1] + val_incr[0]
    zz_err = -zz_split_tot/2
    return np.real(zz_err*1e6)
#=========================================================================================
def U(dim, w1, w2, del1, del2, g12):
    val, vec = np.linalg.eig(red_h(dim, w1, w2, del1, del2, g12))
    vec_arr = np.argmax(vec, axis = 0) #eigenvectors along columns
    val_sor_ind = np.argsort(vec_arr)
    unitary = vec[:,val_sor_ind]
    return unitary
#=========================================================================================
#Dressed (diagonal Hamiltonian)
def H_diag(dim, w1, w2, del1, del2, g12):
    u_op = U(dim, w1, w2, del1, del2, g12)
    u_op_dag = np.asmatrix(u_op).getH()
    matrix1 = np.matmul(u_op_dag, red_h(dim, w1, w2, del1, del2, g12))
    dressed_ham = np.matmul(matrix1, u_op)
    return dressed_ham
#=========================================================================================
"Writing the drive terms"
#=========================================================================================
#Drive operator
def x_op(dim, qubit_index):#qubit index 1 or 2
    x1 = qt.tensor(qt.destroy(dim), qt.qeye(dim)) + qt.tensor(qt.create(dim), qt.qeye(dim))
    x2 = qt.tensor(qt.qeye(dim), qt.destroy(dim)) + qt.tensor(qt.qeye(dim), qt.create(dim))
    if qubit_index==2:
        x1 = x2
    return x1
#=========================================================================================
#Reduced drive matrix
def red_drive(dim, qubit_index):
    d_hs = binomial(dim + no_of_qubits - 1, no_of_qubits ) #dimension of Hilbert Space
    y = np.zeros(d_hs, dtype =int)
    l = 0
    for i in range(0, dim):
        for j in range(0, i+1):
            y[l] = dim*j + (i - j)
            l = l+1
    empty2d = np.zeros([d_hs, d_hs], dtype = complex)
    base_drive = x_op(dim, qubit_index)
    for i1 in range(0, d_hs):
        for j1 in range(0, d_hs):
            empty2d[i1, j1] = base_drive[y[i1], y[j1]]
    return empty2d
#=========================================================================================
#Drive in the dressed frame
def dressed_x_op(dim, w1, w2, del1, del2, g12, qubit_index):
    u_op = U(dim, w1, w2, del1, del2, g12)
    u_op_dag = np.asmatrix(u_op).getH()
    matrix1 = np.matmul(u_op_dag, red_drive(dim, qubit_index))
    dressed_drive = np.matmul(matrix1, u_op)
    return dressed_drive
#=========================================================================================
"Rotating Wave Approximation (RWA)"
#=========================================================================================
#Define a RWA hamiltonian HA that rotates both the qubits in the drive frame
def HA(dim, wd):
    a1 = qt.tensor(qt.destroy(dim), qt.qeye(dim))
    a1dag = qt.tensor(qt.create(dim), qt.qeye(dim))
    a2 = qt.tensor(qt.qeye(dim), qt.destroy(dim))
    a2dag = qt.tensor(qt.qeye(dim), qt.create(dim))
    rotating_ham =  wd*((a1dag*a1) + (a2dag*a2))
    d_hs = binomial(dim + no_of_qubits - 1, no_of_qubits ) #dimension of Hilbert Space
    y = np.zeros(d_hs, dtype =int)
    l = 0
    for i in range(0, dim):
        for j in range(0, i+1):
            y[l] = dim*j + (i - j)
            l = l+1
    empty2d = np.zeros([d_hs, d_hs], dtype = complex)
    for i1 in range(0, d_hs):
        for j1 in range(0, d_hs):
            empty2d[i1, j1] = rotating_ham[y[i1], y[j1]]
    return empty2d
#=========================================================================================
#Write the full drive hamiltonian in the RWA
def drive_rwa(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2):
    dressed_drive_1 = dressed_x_op(dim, w1, w2, del1, del2, g12, 1)
    dressed_drive_2 = dressed_x_op(dim, w1, w2, del1, del2, g12, 2)
    d_hs = binomial(dim + no_of_qubits - 1, no_of_qubits ) #dimensionof Hilbert Space
    empty2d = np.zeros([d_hs, d_hs], dtype = complex)
    for i1 in range(0, d_hs):
        for j1 in range(0, d_hs):
            if i1>j1:
                empty2d[i1, j1] = ((amp1/2)*np.exp(1.j*phase1)*dressed_drive_1[i1, j1]
                + (amp2/2)*np.exp(1.j*phase2)*dressed_drive_2[i1, j1])
            else:
                empty2d[i1, j1] = ((amp1/2)*np.exp(-1.j*phase1)*dressed_drive_1[i1, j1]
                + (amp2/2)*np.exp(-1.j*phase2)*dressed_drive_2[i1, j1])

    return empty2d
#=========================================================================================
#Write down the total Hamiltonian under RWA
def tot_H_rwa(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2, wd):
    H_tot = (H_diag(dim, w1, w2, del1, del2, g12) - HA(dim, wd)
    + drive_rwa(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2))
    #change of order in the basis in the form (00, 01, 10, 11, rest)
    d_hs = binomial(dim + no_of_qubits - 1, no_of_qubits ) #dimensionof Hilbert Space
    permutation = np.identity(d_hs)
    permutation[3,4]=1
    permutation[4,3]=1
    permutation[3,3]=0
    permutation[4,4]=0
    per_transpose = np.asmatrix(permutation).getT()
    matrix_1 = np.matmul(per_transpose, H_tot)
    matrix_2 = np.matmul(matrix_1, permutation)
    return matrix_2
"End of RWA"
#This matrix tot_H_rwa captures the whole dynamics of the system, inthe next section we
#will reduce it to an effective hamiltonian which will get rid of thefast oscillations
#=========================================================================================
"Block diagonalization using principle of least action"
#=========================================================================================
#reference:  L S Cederbaum et al 1989 J. Phys. A: Math. Gen. 22 2427
def S_mat(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2,
wd):#eigenvector_mat
    rwa_hamiltonian = np.asarray(tot_H_rwa(dim, w1, w2, del1, del2,
g12, amp1, phase1, amp2, phase2, wd))
    val, vec = np.linalg.eig(rwa_hamiltonian)
    vec_arr = np.argmax(vec, axis = 0) #eigenvectors along columns
    val_sor_ind = np.argsort(vec_arr)
    eigenvector_matrix = vec[:,val_sor_ind]
    return eigenvector_matrix
#=========================================================================================
#Find the block diagonal form of S in the (2*2)+(2*2)+rest blocks
def S_bd(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2, wd):
    d_hs = binomial(dim + no_of_qubits - 1, no_of_qubits ) #dimensionof Hilbert Space
    #initialize the blocks: block 1, 2 and 3
    block1 = np.zeros([2, 2], dtype = complex)
    block2 = np.zeros([2, 2], dtype = complex)
    block3 = np.zeros([d_hs-4, d_hs-4], dtype = complex)
    S = S_mat(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2, wd)
    for i1 in range(0, 2):
        for j1 in range(0, 2):
            block1[i1, j1] = S[i1, j1]
    for i1 in range(0, 2):
        for j1 in range(0, 2):
            block2[i1, j1] = S[i1+2, j1+2]
    for i1 in range(0, d_hs-4):
        for j1 in range(0, d_hs-4):
            block3[i1, j1] = S[i1+4, j1+4]
    bd_matrix = np.asarray(block_diag(block1, block2, block3))
    return bd_matrix
#=========================================================================================
def T_mat(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2, wd):
    S_blkdg = np.asmatrix(S_bd(dim, w1, w2, del1, del2, g12, amp1,
phase1, amp2, phase2, wd))
    S_blkdg_dag = S_blkdg.getH()
    S = np.asmatrix(S_mat(dim, w1, w2, del1, del2, g12, amp1, phase1,
amp2, phase2, wd))
    matrix_1 = np.matmul(S, S_blkdg_dag)
    matrix_2 = np.matmul(S_blkdg, S_blkdg_dag)
    matrix_3 = fractional_matrix_power(matrix_2, -0.5)
    t_matrix = np.matmul(matrix_1, matrix_3)
    return t_matrix
#=========================================================================================
"Write down the effective hamiltonian with the transformation matrix T-mat"
def eff_H(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2, wd):
    H_rwa_0 = tot_H_rwa(dim, w1, w2, del1, del2, g12, amp1, phase1,
amp2, phase2, wd)
    t_matrix = T_mat(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2,
phase2, wd)
    t_matrix_dag = t_matrix.getH()
    matrix_1 = np.matmul(t_matrix_dag, H_rwa_0)
    eff_bd_ham = np.matmul(matrix_1, t_matrix)
    q_space = np.zeros([4, 4], dtype = complex)
    for i1 in range(0, 4):
        for j1 in range(0, 4):
            q_space[i1, j1] = eff_bd_ham[i1, j1]
    return q_space
#=========================================================================================
def interactions(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2, wd):
    ham_final = eff_H(dim, w1, w2, del1, del2, g12, amp1, phase1,
amp2, phase2, wd)
    interaction_mat = np.zeros([6], dtype = float)
    interaction_mat[0] = np.real(ham_final[0,1])-np.real(ham_final[2,3])
    interaction_mat[1] = np.real(ham_final[0,1])+np.real(ham_final[2,3])
    interaction_mat[2] = np.imag(ham_final[0,1])-np.imag(ham_final[2,3])
    interaction_mat[3] = np.imag(ham_final[0,1])+np.imag(ham_final[2,3])
    interaction_mat[4] = (np.real(ham_final[0,0])+np.real(ham_final[3,3])
    -np.real(ham_final[1,1])-np.real(ham_final[2,2]))/2
    interaction_mat[5] = (np.real(ham_final[0,0])+np.real(ham_final[2,2])
    -np.real(ham_final[1,1])-np.real(ham_final[3,3]))/2
    return interaction_mat
#=========================================================================================
"Figure of merit: How good the approximation is?"
#=========================================================================================
def fig_merit(dim, w1, w2, del1, del2, g12, amp1, phase1, amp2, phase2, wd):
    d_hs = binomial(dim + no_of_qubits - 1, no_of_qubits ) #dimensionof Hilbert Space
    S_blkdg = np.asmatrix(S_bd(dim, w1, w2, del1, del2, g12, amp1,
phase1, amp2, phase2, wd))
    S_blkdg_dag = S_blkdg.getH()
    matrix_2 = np.matmul(S_blkdg, S_blkdg_dag)
    trace = np.trace(matrix_2)
    return trace/d_hs
#=========================================================================================
"Generate the plot"
#=========================================================================================