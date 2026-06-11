import dynamiqs as dq
import jax.numpy as jnp
import numpy as np
from typing import TYPE_CHECKING, Sequence
from HM.simulator.two_qubit_simulator.engine.constants import DT_SAMPLE_NS, TWOPI
if TYPE_CHECKING:
    from HM.simulator.two_qubit_simulator.base_classes.device_base import (
        DriveLine,
        Qubit,
    )


class TwoQubitPulseSimulatorDynamiqs:

    def __init__(self, qubits: Sequence[Qubit],
                       J_MHz: float,
                       drive_lines: Sequence[DriveLine],
                       confusion_matrices: tuple[np.ndarray, np.ndarray],
                       n_sub: int = 8,
                       dt_sample_ns: float = DT_SAMPLE_NS):

        assert len(qubits) == 2, "this sim is hard-wired to 2 qubits"
        self.qubits = list(qubits)
        self.J_MHz = J_MHz
        self.drive_lines = {dl.name: dl for dl in drive_lines}
        self.M1, self.M2 = confusion_matrices  
        self.n_sub = n_sub
        self.dt_sample_ns = dt_sample_ns
        self.dims = [q.n_levels for q in qubits]
        self.dim = self.dims[0]*self.dims[1]
        self.delta_qq_MHz = self.qubits[0].frame_MHz - self.qubits[1].frame_MHz
        self.comp_idx = [0,1, self.dims[1], self.dims[1]+1] # a nice was to build a list of indices for the computational subspace
        self.channel_names = list(self.drive_lines.keys())
        self._build_operators()



    def _build_operators(self) -> None:
        n0, n1 = self.dims #unpacking the dimensions of qubits 

        #building anhillation operators:
        a0_local = dq.destroy(n0)
        a1_local = dq.destroy(n1)

        #building identity operators:
        I0 = jnp.eye(n0)
        I1 = jnp.eye(n1)


        #Lift to joint space: a0 acts on q0 and a1 acts on q1:

        a0 = jnp.kron(dq.to_jax(a0_local), I1)
        a1 = jnp.kron(I0, dq.to_jax(a1_local))
        self.a = [a0, a1]
        self.ad = [op.conj().T for op in self.a]

        ## Static drift hamiltionian 
        H_drift = jnp.zeros((self.dim, self.dim), dtype = complex)
        for q, qb in enumerate(self.qubits):
            H_drift = H_drift + (TWOPI*0.5*qb.anharm_MHz*
                                    self.ad[q]@self.ad[q]@self.a[q]@self.a[q])

        self.H_drift = H_drift

        ## Coupling operators (used every time)
        self.coupling_op = self.ad[0]@self.a[1]
        self.coupling_op_dag = self.a[0]@self.ad[1]


    def _hamiltonian_at(self, t_ns:float, envelopes:jnp.ndarray) -> jnp.ndarray:
        """ Hamiltionian built in angular units (2*pi baked in).

        t_ns : the sub-step midpoint time in ns
        envelopes: array of complex envelope values at that time shape (n_channels,) JAX array btw
        """

        H = self.H_drift
        # We're starting from the static part 
        # J picks up a phase that oscillates at the qubit-qubit detuning 

        ph = TWOPI*self.delta_qq_MHz*t_ns*1e-3
        H = H + TWOPI*self.J_MHz*(
            self.coupling_op*jnp.exp(1j*ph) 
            +
            self.coupling_op_dag*jnp.exp(-1j*ph)
        )

        # Drive terms 
        # 0.5 *(eps_eff*a^dag + c.c) 
        # for a self-drive (carrier == frame): detuning is 0, no modulation. 
        # For the CR drive (carrier == target freq): detuning is not zero obvi 
        for i, name in enumerate(self.channel_names):
            dl       = self.drive_lines[name]
            eps      = envelopes[i]
            delta    = dl.carrier_MHz - self.qubits[dl.target].frame_MHz
            eps_eff  = eps*jnp.exp(-1j*TWOPI*delta*t_ns*1e-3)
            q        = dl.target
            H = H + TWOPI*0.5*(
                eps_eff*self.ad[q] + 
                jnp.conj(eps_eff)*self.a[q]
            )


        return H
    

    def run_shot(self, 
                timeline: dict[str, np.ndarray],
                psi0 =None,
                store_trajectory: bool = False
                ):
                """Evolve a state through one full pulse timeline.

                Internally pre computes all substep midpoint times and runs a single jax.lan.scan over all L*n_sub substeps, 
                making the evolution JIT-compilable and differentiable end to end for GRAPE etc. 


                returns a JAX array of shape (dim,1).
                """

                import jax
                unknown = set(timeline.keys()) - set(self.drive_lines)
                if unknown:
                    raise KeyError(f"unknown channels: {unknown}")
                ### the above just checks if all the channels in the timeline are drive lines (not really needed)

                # we need to pre-compute all the substep midpoint times and store them in a JAX array
                L = len(timeline[self.channel_names[0]]) # all channels are of the same length
                timeline_array = jnp.array(
                    np.stack([timeline[name] for name in self.channel_names], axis=1), dtype=complex
                ) #it gives you the sample at every channel at every time step. So lets say you have three channels and time index 3 then element at idx 3 would be a list of the pulse sample at each channel.

                k = jnp.arange(L) #sample index
                s = jnp.arange(self.n_sub) #substep index
                t_mids = (k[:, None] + (s[None, :] +0.5) / self.n_sub) * self.dt_sample_ns
                t_mids_flat = t_mids.reshape(-1) #basicdally using broadcasting we get the t_mid val for each substep at each sample


                # repeat each envelope value n_sub times to create a matching array for the substep expansion
                envelopes_flat = jnp.repeat(timeline_array, self.n_sub, axis=0) # timeline array has the shape (L, n_channels) so repeating it n_sub times gives you (L*n_sub, n_channels)
                                            #what to repeat, how many times, along which axis (2D so it's either 0 or 1) our data is [[val_ch1, val_ch2, val_ch3], [val_ch1, val_ch2, val_ch3], [val_ch1, val_ch2, val_ch3]] so you want to repeat the 0 axis, not the internal 1 axis. 
                # if shape is (n,m) and we repeat axis 0 then the shape becomes (n*r,m) where r is the number of times we repeat.
                
                # timeline_array (L=3 rows):
                #   row 0: [cr=32.5, q1=0, q2=0]
                #   row 1: [cr=32.5, q1=0, q2=0]
                #   row 2: [cr=0,    q1=0, q2=0]

                # envelopes_flat after repeat (L*n_sub=6 rows):
                #   row 0: [cr=32.5, q1=0, q2=0]   ← substep 0 of sample 0
                #   row 1: [cr=32.5, q1=0, q2=0]   ← substep 1 of sample 0
                #   row 2: [cr=32.5, q1=0, q2=0]   ← substep 0 of sample 1
                #   row 3: [cr=32.5, q1=0, q2=0]   ← substep 1 of sample 1
                #   row 4: [cr=0,    q1=0, q2=0]   ← substep 0 of sample 2
                #   row 5: [cr=0,    q1=0, q2=0]   ← substep 1 of sample 2
                # now we have a time array and a envelope table that shows the sample at each substep for each channel.
                if psi0 is None:
                    psi = jnp.zeros((self.dim, 1), dtype=complex).at[0,0].set(1.0)
                else:
                    psi = jnp.array(np.array(psi0).reshape(self.dim,1), dtype=complex)

                dt_sub_us = (self.dt_sample_ns / self.n_sub) * 1e-3


                def step(psi, x):
                    t_ns, envelope_row = x
                    H = self._hamiltonian_at(t_ns, envelope_row)
                    psi_next = dq.expm(-1j*H*dt_sub_us)@psi
                    return psi_next, psi_next


                psi_final, all_states = jax.lax.scan(step,psi, (t_mids_flat, envelopes_flat))


                if store_trajectory:
                    return psi_final, all_states
                return psi_final