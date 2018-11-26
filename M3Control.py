# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 14:07:45 2018

I tried my best keep the rules following pep-8, if you have any suggestions,
please contact the author.

@author: Pinlei Lu (Hat Lab)
email: pil9@pitt.edu
"""

import M3_module as MM
import matplotlib.pyplot as plt
import time
import numpy as np
import get_data as gd
import h5py

#%%
FPGA_path ="C:\\HAT_PXIe\\FPGA\\Digitizer\\Project_n_Firmware"
#FPGA_filename = "PreRun.sbp"
#FPGA_filename = "Real_Exp.sbp"
FPGA_filename ="Original.sbp"


AWG_FPGA_path = "C:\\HAT_PXIe\\FPGA\\AWG"
AWG_FPGA_filename = "AWG_Origional.sbp"
#AWG_FPGA_filename = "AWG_Shut_gef.sbp"

HVI_path = "C:\\HAT_PXIe\\HVI"
HVI_trigger_filename = "Pre_Run.HVI"
#HVI_trigger_filename = "Real_Exp_PiPulse.HVI"
#HVI_trigger_filename = "Real_Exp_t1.HVI"
#HVI_trigger_filename = 'Real_Exp_t2.HVI'
###############################################################################
#%%

M3 = MM.M3_Module() # Initialize the module.
M3.openHVI(HVI_path + HVI_trigger_filename) # Open HVI

M3.loadAWGFirmware(AWG_FPGA_path + AWG_FPGA_filename) # Load firmware for the Digitizer
M3.loadFirmware(FPGA_path + FPGA_filename) # Load firmware for the AWG

offset = [-0.098, -0.143, -0.053, 0.194]
offset = [0,0,0,0]
M3.AWGInit(channel_offset=offset, iq_scale=0.844, skew_phase=115.7) # Initialize the AWG
seq = M3.sequenceGenerate('box', pi_pulse_amp=1.0, box_amp=0.13,
                          box_length=800, sigma=45, ef_pi_pulse_amp=0.0,
                          ef_freq = 0.317) # Create the wareform we need
                          
M3.AWGUpload(seq) # Upload the wave into RAM and queue

M3.DigFPGAReset() # Digitizer Reset

M3.writeDemodulateFunc() # Write sinusoidal wave for the demodulation 

'''
Notice here, you need to run 67th syntax first, then comment it 
and run 68th syntax and then comment it. In the continued experiment, you only need 69th syntax.
'''
#M3.IQTraceTruncation(T_SIG=16, T_REF=16) # 1st step: pre run for truncation
#M3.integrateTruncation(100, 500) # 2nd step: integration truncation
M3.writeTruncationCondition(100, 500) # Read the truncation point from the default file


temp = h5py.File('weight', 'r')
I_weight = temp['I_weight'].value[0:2099]
Q_weight = temp['Q_weight'].value[0:2099] # Read the weight function
temp.close()

a,b = M3.writeWeightFunction(I_weight, Q_weight, default=1, weight_start=100, 
                             weight_end=500) # Upload the weight function

'''
For the feedback part, you may need to refer the insruction mannual
M3.writeFeedbackPoint_gefh(#states, x_g, y_g, x_e, y_e, x_f, y_f, 
                           ef_start, ef_span, ge_start, ge_span)
'''
#M3.writeFeedbackPoint(-791, 37, 0, 1, 100, 250)
#M3.writeFeedbackPoint_gefh(3, 2541, -1228, -2772, -1282, -2660, 2061,  0, 300, 300, 200)



#%%
M3.digitizerInit(fullscale = 0.5) # Digitizer initial with prescaler

points_per_cycle = 500
cycles = 1000
multi = 1
    
start = time.time()
data = M3.digitizerRead(points_per_cycle, cycles, multi = multi, 
                        trigger_delay=0, timeout=1000, data_read_mask = '1111') # Acquire the data
print 'Capturing data spend ', time.time() - start, ' s'

I, Q= M3.dataProcess(data, points_per_cycle, cycles, multi, method=1, 
                     wave_num=100, lim=8000, int_start=0, int_end=500) # Process the data

#%%
cycles_x5 = 10
start = time.time()
data = M3.digitizerRead(5000, cycles_x5, multi = 1, trigger_delay = 26, 
                        timeout = 41000,  data_read_mask = '1100') # Acquire the data from the swap RAM
print 'Capturing data spend ', time.time() - start, ' s'

I, Q = M3.dataProcess(data, 5000, cycles_x5, 1000, method = 3, fit = 0, 
                      lim = 20000) # 3: One State fit

#xdata = np.linspace(-1.0, 1.0, 100)
#M3.advancedDataProcess(xdata, data, cycles_x5*50, "20180916", "PXIe", "pi_pulse", "pi_pulse")

#xdata = np.arange(100)
#M3.advancedDataProcess(xdata, data, cycles_x5*50, "201800916", "PXIe", "t1", "t1")

#xdata = np.linspace(0, 49.9, 100)
#M3.advancedDataProcess(xdata, data, cycles_x5*50, "201800916", "PXIe", "t2R", "t2")

#xdata = np.linspace(0, 49.9, 100)
#M3.advancedDataProcess(xdata, data, cycles_x5*50, "201800916", "PXIe", "t2E", "t2_Echo")

#xdata = np.arange(42)
#M3.advancedDataProcess(xdata, data, cycles_x5*119, "201800916", "PXIe", "allxy", "allxy")

#xdata = np.arange(9)
#I,Q = M3.advancedDataProcess(xdata, data, 555555, "201800916", "PXIe", "science_protocol", "130mVscience_protocol", angle = -10.)

#xdata = np.arange(9)
#I,Q = M3.advancedDataProcess(xdata, data, 27777, "201800916", "PXIe", "science_protocol", "real_science_protocol", angle = -10.)

#xdata = np.linspace(-1.0, 1.0, 100)
#M3.advancedDataProcess(xdata, data, cycles_x5*50, "20180916", "PXIe", "ef_pi_pulse", "ef_pi_pulse")


M3.moduleClose()
