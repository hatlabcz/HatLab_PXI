# Welcome to HAT_PXIe!
This repository is for the PXIe control and cool quantum computer experiments. Start from Hatlab, in the hope of throwing out a minnow to catch a whale.

# Overview

# Quickstart
```python
import M3_module as MM
M3 = MM.M3_module

# Load firmware and HVI
M3.loadAWGFirmware(AWG_FPGA_path + AWG_FPGA_filename)
M3.loadFirmware(FPGA_path + FPGA_filename)
M3.openHVI(HVI_path + HVI_trigger_filename)
```
```python
# Upload a pi pulse(qbit drive) and a box car(cavity drive) into AWG
M3.AWGInit()
seq = M3.sequenceGenerate('box')
M3.AWGUpload(seq)
```

# Advanced Application

# Copyright and Contacts

