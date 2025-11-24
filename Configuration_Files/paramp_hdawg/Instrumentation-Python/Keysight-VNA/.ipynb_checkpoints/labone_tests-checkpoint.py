#%%
import numpy as np
import time
import zhinst.core

from hadawg_init import *


#%%

import zhinst

daq = zhinst.core.ziDAQServer('127.0.0.1', 8004, 6)
# Starting module awgModule on 2024/02/26 14:07:29
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 0)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
# Starting module awgModule on 2024/02/26 14:07:30
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 1)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
# Starting module awgModule on 2024/02/26 14:07:30
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 2)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
# Starting module awgModule on 2024/02/26 14:07:30
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 3)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
# Starting module awgModule on 2024/02/26 14:07:42
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 0)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
# Starting module awgModule on 2024/02/26 14:07:42
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 1)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
# Starting module awgModule on 2024/02/26 14:07:42
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 2)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
# Starting module awgModule on 2024/02/26 14:07:42
awg = daq.awgModule()
awg.set('device', 'dev8099')
awg.set('index', 3)
awg.execute()
# To read the acquired data from the module, use a
# while loop like the one below. This will allow the
# data to be plotted while the measurement is ongoing.
# Note that any device nodes that enable the streaming
# of data to be acquired, must be set before the while loop.
# result = 0
# while awg.progress() < 1.0 and not awg.finished():
#     time.sleep(1)
#     result = awg.read()
#     print(f"Progress {float(awg.progress()) * 100:.2f} %\r")
#%%

init_code_paramp(daq)
# %%
all_ch_on(daq)

#%%
# all_ch_off(daq)
# %%
