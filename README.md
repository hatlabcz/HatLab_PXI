# Welcome to HAT_PXIe!
This repository is for the PXIe control and cool quantum computer experiments.

# Overview
A field-programmable gate array (**FPGA**) is an integrated circuit which can be repeatedly reconfigured to achieve a desired information processing functionality. 

We have realized all qubit data processing with a delay of 22 clock cycles (220 ns) after receiving the last input. using the feedback loop, we can efficiently prepare desired qubit states without waiting for the natural qubit relaxation process, as well as perform weak measurement protocols to study the measurement process.   

For the details of the FPGA, please read [FPGA Manual](https://github.com/hat-lab/HAT_PXIe/blob/master/FPGA%20Manual.pdf)

# Quickstart
(The firmware(.sbp files) provided here may not be loadable on your device, because of incompatibility of firmware version and module slots. You can open the FPGA projects(.FPGAprj files), assign the project to your module, and generate firmware for your own device)

# Pre Run
Before we start a measurement experiment, we need to perform the Pre Run step to get the data truncation points and integrations range.
In this step, only the demodulation calculation is done in FPGA, the demodulation result SI, SQ, RI, and RQ will output to DAQ1-4.
You can do the phase correction (rotation) and integration with the output data in Python.

In this step, you need to use these three files:
```python
FPGA_filename = "PreRun.sbp"
AWG_FPGA_filename = "AWG_Origional.sbp"
HVI_trigger_filename = "Pre_Run.HVI"
```

Then, initialize the module:
```python
import M3_module as MM
M3 = MM.M3_module

# Load firmware and HVI
M3.loadAWGFirmware(AWG_FPGA_path + AWG_FPGA_filename)
M3.loadFirmware(FPGA_path + FPGA_filename)
M3.openHVI(HVI_path + HVI_trigger_filename)
```

After that, you can determine which wave you want to upload.
```python
# Upload a pi pulse(qbit drive) and a box car(cavity drive) into AWG
M3.AWGInit()
seq = M3.sequenceGenerate('box')
M3.AWGUpload(seq)
```

Now, you want to do some setting on the digitizer. The demodulate function will be the 50MHz wave to extract information from the input.


Then the FPGA need to determine the MSB after the demodulation, it will automatically print out and save in the local file. Also you can input some value manually (eg: 16) see what will happen.
```python
M3.DigFPGAReset() # Digitizer Reset (This will send a reset signal to the FPGA and reset almost everything)
M3.writeDemodulateFunc() # Write sinusoidal wave for the demodulation 

M3.IQTraceTruncation(T_SIG=16, T_REF=16) # 1st step: pre run for truncation
#M3.integrateTruncation(100,500) # 2nd step: integration truncation
#M3.writeTruncationCondition(100, 500) # Read the truncation point from the default file
```


After that you need to determine the MSB after integration.
You need to look at the demodulation result, determine the integration start and end point(e.g. 100 and 500) and run the code in the following way.
```python
M3.DigFPGAReset() # Digitizer Reset (This will send a reset signal to the FPGA and reset almost everything)
M3.writeDemodulateFunc() # Write sinusoidal wave for the demodulation 

#M3.IQTraceTruncation(T_SIG=16, T_REF=16) # 1st step: pre run for truncation
M3.integrateTruncation(int_start=100, int_endt=500) # 2nd step: integration truncation
#M3.writeTruncationCondition(100, 500) # Read the truncation point from the default file
```
**Attention:** in the Pre run firmware, we do the integration in the PC, however, this still need to be done for the further firmware.
 
At last, you must comment first two and only use the last one. It will automatically read the value saved in the local file.
```python
M3.DigFPGAReset() # Digitizer Reset (This will send a reset signal to the FPGA and reset almost everything)
M3.writeDemodulateFunc() # Write sinusoidal wave for the demodulation 

#M3.IQTraceTruncation(T_SIG=16, T_REF=16) # 1st step: pre run for truncation
#M3.integrateTruncation(100, 500) # 2nd step: integration truncation
M3.writeTruncationCondition(100, 500) # Read the truncation point from the default file
```

Now you can let the digitizer start reading data.

**WARNING:** It seems like keysight M3102A can only read 1026 cycles data, as long as the number exceed, the results will lost credibility.

The two solutions we got here:
1. Re-configure the "Data Acquisition"(DAQ) block after each 1000 cycles, which is very time-consuming.
2. We implement a RAM in the FPGA, and output 5000*1000 data every time.(Ses details in the FPGA manual)

In the pre run, we are using the first way:
```python
M3.digitizerInit(fullscale = 0.5) # Digitizer initial with prescaler

points_per_cycle = 500
cycles = 1000
multi = 1 # How many times you want to re-configure
    
start = time.time()
data = M3.digitizerRead(points_per_cycle, cycles, multi = multi, 
                        trigger_delay=0, timeout=1000, data_read_mask = '1111') # Acquire the data
print 'Capturing data spend ', time.time() - start, ' s'

I, Q= M3.dataProcess(data, points_per_cycle, cycles, multi, method=1, 
                     wave_num=100, lim=8000, int_start=0, int_end=500) # Process the data
```                     
# Real Experiment

# Advanced Application

You can get most of the details from [FPGA Manual](https://github.com/hat-lab/HAT_PXIe/blob/master/FPGA%20Manual.pdf)
The lastest result we can get is the feedback between three states.

We are currently expanding the FPGA and control software to enable multi-qubit control and readout for remote entanglement protocols, which are not possible with our current generation of non-FPGA based readout and control electronics.

# Copyright and Contacts

If you have any question, please contact:
Prof. Michael Hatridge: hatridge@pitt.edu
Pinlei Lu: pil9@pitt.edu
Chao Zhou: chz78@pitt.edu
Maria Mucci: mmm242@pitt.edu

Want to know more about us, please see [Hatlab](http://hatlab.pitt.edu/)
