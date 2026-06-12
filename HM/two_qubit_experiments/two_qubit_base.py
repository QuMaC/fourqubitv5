from HM.single_qubit_experiments.single_qubit_base import BaseExperiment


class TwoQubitExperiment(BaseExperiment):
    def __init__(self, q_list: list, expt_name: str = None, **kwargs):
        if len(q_list) != 2:
            raise ValueError("q_list must contain exactly 2 qubits")
        super().__init__(expt_name=expt_name, **kwargs)

        self.q_control_no = q_list[0]
        self.q_target_no = q_list[1]

        self.cr_ac_str = f"cr_ac_c{self.q_control_no}t{self.q_target_no}"
        self.cr_elem = f"cr_c{self.q_control_no}t{self.q_target_no}"
        self.cr_ac_elem = f"cr_ac_c{self.q_control_no}t{self.q_target_no}"
        self.paramp_on_q_control = kwargs.get("paramp_on_q_control", False)
        self.paramp_on_q_target = kwargs.get("paramp_on_q_target", False)

        self.ctrl = self.build_qubit_context(self.q_control_no, self.q_control_no)
        self.tgt = self.build_qubit_context(self.q_target_no, self.q_target_no)
        self.q_control_str = self.ctrl.q_str
        self.q_target_str = self.tgt.q_str
        self.rr_control_str = self.ctrl.rr_str
        self.rr_target_str = self.tgt.rr_str
        self.cr_str = f"cr_c{self.q_control_no}t{self.q_target_no}"
        self.paramp_on_q_control = self.ctrl.paramp
        self.paramp_on_q_target = self.tgt.paramp

        # Compatibility aliases for common two-qubit scripting patterns.
        self.elec_delay_ns_control = self.ctrl.elec_delay_ns
        self.elec_delay_ns_target = self.tgt.elec_delay_ns
        self.phase_offset_rad_control = self.ctrl.phase_offset_rad
        self.phase_offset_rad_target = self.tgt.phase_offset_rad
        self.out_control = self.ctrl.out
        self.out_target = self.tgt.out

        self.n_avg = kwargs.get("n_avg", 500 if self.paramp_on_q_control or self.paramp_on_q_target else 2000)
        




    # def run_experiment(self):
    #     pass

    # def analyze_and_plot(self):
    #     pass

    # def save_experiment_data(self):
    #     pass