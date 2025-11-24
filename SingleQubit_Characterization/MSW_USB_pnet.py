#%%
# Control Mini-Circuits' RC or USB series mechanical switches via USB
# Requirements:
#   1: Python.Net (pip install pythonnet)
#   2: Mini-Circuits' DLL API file (mcl_RF_Switch_ControllerNET45.dll)
#      https://www.minicircuits.com/softwaredownload/mcl_RF_Switch_Controller64_dll.zip
#      Note: - Windows may block the DLL file after download as a precaution
#            - Right-click on the file, select properties, click "Unblock" (if shown)

import clr # pythonnet
clr.AddReference('mcl_RF_Switch_Controller_NET45')      # Reference the DLL

from mcl_RF_Switch_Controller_NET45 import USB_RF_SwitchBox

sl_to_fridge = '11509250001'
sl_from_fridge = '11509250002'

sl_list = [sl_from_fridge, sl_to_fridge]

vna_opx_switch_map = {'112':{'A': 0, 'D': 0, 'C': 0},
                      '134':{'A': 1, 'D': 0, 'C': 0},
                      '212':{'B': 0, 'D': 1, 'C': 0},
                      '234':{'B': 1, 'D': 1, 'C': 0},
              }

def check_USB_switch_status():
    sw = USB_RF_SwitchBox()
    for sl_no in sl_list:
        st = sw.Connect(sl_no)[0]
        if st > 0:
            print(f'{sl_no} connection ok')
        else:
            print(f'{sl_no} connection not ok')
        sw.Disconnect()


def switch_to_vna(qe):
    sw = USB_RF_SwitchBox()
    for sl_no in sl_list:
        state = sw.Connect(sl_no)[0]
        if state > 0 :
            print('Connect ok')
        else:
            print('Connect not ok. Still proceeding')
        for key, value in vna_opx_switch_map[qe].items():
            sw.Set_Switch(key,value)
        sw.Disconnect()



sw = USB_RF_SwitchBox()     # Create an instance of the switch class

Status = sw.Connect()[0]       # Connect the switch (pass the serial number as an argument if required)

#%%
if Status > 0:              # The connection was successful

    Responses = sw.Send_SCPI(":SN?", "")            # Read serial number
    print (str(Responses[2]))   # Python interprets the response as a tuple [function return (0 or 1), command parameter, response parameter]

    Responses = sw.Send_SCPI(":MN?", "")            # Read model name
    print (str(Responses[2]))

    # SP6T switches (specify the switch channel A to B, model dependent)
    Status = sw.Send_SCPI("SP6TA:STATE:6", "")      # Set switch state (SW A, COM<>6)
    Responses = sw.Send_SCPI("SP6TA:STATE?", "")    # Read switch state (SP6TA)
    print (str(Responses[2]))

    # SP4T switches (specify the switch channel A to B, model dependent)
    #Status = sw.Send_SCPI("SP4TA:STATE:4", "")      # Set switch state (SW A, COM<>4)
    #Responses = sw.Send_SCPI("SP4TA:STATE?", "")    # Read switch state (SP4TA)
    #print (str(Responses[2]))

    # SPDT & transfer switches (specify the switch channel A to H, model dependent)
    #Status = sw.Send_SCPI("SETA=1", "")             # Set switch state (SW A, COM<>2)
    #Responses = sw.Send_SCPI("SWPORT?", "")         # Read switch state, returns a byte value of all switch states (1 bit per switch)
    #print (str(Responses[2]))

    sw.Disconnect()             # Disconnect at the end of the program

else:
    print ("Could not connect.")

# %%
