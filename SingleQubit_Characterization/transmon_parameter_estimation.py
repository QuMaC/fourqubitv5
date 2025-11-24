import numpy as np
import json
from Configuration_Files.configuration_4qubitsv3 import *

Ej = {}

# for q in [1, 2, 3, 4, 5, 6]:
C = 79e-15
Lj = 12e-9
Ec = e ** 2 / (2 * h * C)
Ej = hbar / (2 * pi * Lj * (2 * e) ** 2)

print("Ec = {0:.3f}".format(Ec * 1e-9))
print("Ej = {0:.3f}".format(Ej * 1e-9))
print("Ej/Ec = {0:.1f}".format(Ej / Ec))

f_q = 1e-9 * (energy_level(1, Ec, Ej / Ec) - energy_level(0, Ec, Ej / Ec))
anh_q = 1e-6 * (2 * energy_level(1, Ec, Ej / Ec) - energy_level(0, Ec, Ej / Ec) - energy_level(2, Ec, Ej / Ec))

print(f"Qubit Frequency = {f_q:.3f} GHz")
print(f"Qubit Anharmonicity = {anh_q:.3f} MHz")


