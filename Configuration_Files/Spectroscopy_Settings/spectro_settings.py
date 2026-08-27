# load the qubit_spec_settings.json and resonator_spec_settings.json files
import json
from pathlib import Path
from Configuration_Files.config_dictionaries import path_global

qubit_spec_settings_path = path_global + "/Configuration_Files/Spectroscopy_Settings/qubit_spec_settings.json"
resonator_spec_settings_path = path_global + "/Configuration_Files/Spectroscopy_Settings/resonator_spec_settings.json"

with open(qubit_spec_settings_path, "r") as f:
    qubit_spec_settings = json.load(f)

with open(resonator_spec_settings_path, "r") as f:
    resonator_spec_settings = json.load(f)


