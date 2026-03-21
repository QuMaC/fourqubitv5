from Configuration_Files.configuration_4qubitsv3 import sl_list, vna_opx_switch_map
import os as _os
import clr  # pythonnet

# Load by full path so the DLL just needs to live in the same folder as this file.
# Download from: https://www.minicircuits.com/softwaredownload/mcl_RF_Switch_Controller64_dll.zip
_dll_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'mcl_RF_Switch_Controller_NET45.dll')
clr.AddReference(_dll_path)

from mcl_RF_Switch_Controller_NET45 import USB_RF_SwitchBox

sw = USB_RF_SwitchBox()


def VNA_route_off():
    for sl_no in sl_list:
        st = sw.Connect(sl_no)[0]
        if st > 0:
            print('Connection ok')
        else:
            print('Connection not ok. still proceeding')
        sw.Set_Switch('C', 1)
        sw.Disconnect()


def check_USB_switch_status():
    for sl_no in sl_list:
        st = sw.Connect(sl_no)[0]
        if st > 0:
            print(f'{sl_no} connection ok')
        else:
            print(f'{sl_no} connection not ok')
        sw.Disconnect()


def switch_to_vna(qe):
    # for sl_no in sl_list:
    #     state = sw.Connect(sl_no)[0]
    #     if state > 0:
    #         print('Connect ok')
    #     else:
    #         print('Connect not ok. Still proceeding')
    #     for key, value in vna_opx_switch_map[qe].items():
    #         sw.Set_Switch(key, value)
    #     sw.Disconnect()

    for switch in vna_opx_switch_map[qe].keys():
        state = sw.Connect(switch)[0]
        if state > 0:
            print('Connect ok')
        else:
            print('Connect not ok. Still proceeding')

        for key, value in vna_opx_switch_map[qe][switch].items():
            sw.Set_Switch(key, value)
        sw.Disconnect()
