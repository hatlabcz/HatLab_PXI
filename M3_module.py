# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 10:08:15 2018

I tried my best keep the rules following pep-8, if you have any suggestions,
please contact the author.

@author: Pinlei Lu (Hat Lab)
email: pil9@pitt.edu
"""

import sys
sys.path.append('C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
import keysightSD1
import numpy as np
import time
import h5py
import matplotlib.pyplot as plt
import PulseGenerate as PG
import get_data as GD
import data_fit as DF
import fit_all as FA

class M3_Module():
    def __init__(self, init=1):
        self.SLOT_NUM = {"CHASSIS": 1,
                         "AWG1": 2,          # M3202A AWG1
                         "AWG2": 3,          # M3202A AWG2
                         "DIG": 4,           # M3102A Digitizer
                         "MARK1": 5,         # M3201A Marker1
                         "MARK2": 6}         # M3201A Marker1
                         
        if init == 1:
            self.AWG1 = keysightSD1.SD_AOU()
            AWG1_ID = self.AWG1.openWithSlot("", self.SLOT_NUM["CHASSIS"], 
                                             self.SLOT_NUM["AWG1"])
            if AWG1_ID < 0:
                raise NameError('Cannot find AWG1')
            self.MARK1 =  keysightSD1.SD_AOU()
            MARK1_ID = self.MARK1.openWithSlot("", self.SLOT_NUM["CHASSIS"], 
                                               self.SLOT_NUM["MARK1"])
            if MARK1_ID < 0:
                raise NameError('Cannot find MARK1')           
        else:
            raise NameError('Plz fix the code')
        
        self.Digitizer = keysightSD1.SD_AIN()
        Digitizer_ID = self.Digitizer.openWithSlot("", self.SLOT_NUM["CHASSIS"], 
                                                   self.SLOT_NUM["DIG"])    
        if Digitizer_ID < 0:
            raise NameError('Cannot find Digitizer')
        
        self.HVI = keysightSD1.SD_HVI()

    def AWGInit(self, channel_offset=[-0.308, -0.026, 0.187, 0.019], 
                iq_scale=1.151, skew_phase=1.1):
        '''
        Initialize the AWG, including waveform flush, queue flush, queue 
        configuration, AWG output and amplitude prescalar.
        Input:
            channel_offset: DC offset for each AWG channel.
            iq_scale: compensate the amplitude difference between qubit drive
                      channel.
            skew_phase: compensate the cable length difference between qubit
                        drive channel.
        Output:
            None
        '''
        for i in range(4): # Initilization
            
            self.AWG1.AWGflush(i+1)
            self.AWG1.AWGqueueConfig(i+1, 1)
            self.AWG1.channelWaveShape(i+1, keysightSD1.SD_Waveshapes.AOU_AWG)
            self.AWG1.channelAmplitude(i+1, 1)
            
            self.MARK1.AWGflush(i+1)
            self.MARK1.AWGqueueConfig(i+1, 1)
            self.MARK1.channelWaveShape(i+1, keysightSD1.SD_Waveshapes.AOU_AWG)
            self.MARK1.channelAmplitude(i+1, 1)
        self.AWG1.waveformFlush()
        self.MARK1.waveformFlush()
        self.MARK1.channelOffset(1, 1)
        self.MARK1.channelOffset(2, 1)
        for i in range(4):
            self.AWG1.channelOffset(i+1, channel_offset[i])
        self.iq_scale=iq_scale
        self.skew_phase = skew_phase/180. * np.pi
        return 0
        
    def AWGclean(self):
        '''
        Function for cleaning the AWG queue.
        '''
        for i in range(4):
            self.AWG1.AWGflush(i+1)
            self.MARK1.AWGflush(i+1)

    def sequenceGenerate(self, AWG_wave, pi_pulse_amp=0.576, box_amp=1, 
                         box_length=500, sigma = 20, ef_pi_pulse_amp=0.576, 
                         ef_freq = 0.317):
        '''
        Generate various AWG waveform we need.
        Input:
            AWG_wave: the name of AWG waveform.
            **kwarg: the parameter of the waveform.
        Output:
            SequenceClass from PulseGenerate.py                             
        '''                  
        self.AWG_wave = AWG_wave
        if AWG_wave == 'tune_up_mixer':
            seq = PG.Sequence(1, 200000)
            mark_qubit = PG.Square(1, 99900, 0, 1, 0, 0, 1)               
            box = PG.DC_Pulse(1, 199000, 0.1, self.iq_scale, 0, 
                              self.skew_phase, 0.1)
            seq.addPulseBoth(box, 0, 1, trigger=1)
            seq.addPulse(mark_qubit, 0, 5, trigger=1)

        if AWG_wave == 'feedback':
            pi_2_pulse_amp = pi_pulse_amp/2.0
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                              self.skew_phase, pi_pulse_amp, sigma)        
            gau_id = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                                 self.skew_phase, 0, sigma)        
            gau_2 = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                                self.skew_phase, pi_2_pulse_amp, sigma)        
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            
            seq = PG.Sequence(2, 7000)

            seq.addPulseBoth(gau_2, 100, 1, trigger=1)
            seq.addPulse(mark_qubit, 0, 5, trigger=1)
            seq.addPulse(box, 100, 3, trigger=1)
            seq.addPulse(mark_cav, 0, 6, trigger=1)
            seq.addPulseBoth(gau, 6000, 1, trigger=0)
            seq.addPulse(mark_qubit, 5900, 5, trigger=0)
                        
            seq.addPulseBoth(gau_id, 7100, 1, trigger=1)
            seq.addPulse(mark_qubit, 7000, 5, trigger=1)
            seq.addPulse(box, 7100, 3, trigger=1)
            seq.addPulse(mark_cav, 7000, 6, trigger=1)

        if AWG_wave == 'feedback_ef':
            pi_2_pulse_amp = pi_pulse_amp/2.0
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                              self.skew_phase, pi_pulse_amp, sigma)        
            gau_ef = PG.Gaussian(1, sigma*10, ef_freq, self.iq_scale, 0, 
                                 self.skew_phase, ef_pi_pulse_amp, sigma)  
            gau_id = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                                 self.skew_phase, 0, sigma)        
            gau_2 = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                                self.skew_phase, pi_2_pulse_amp, sigma)        
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
        
            seq = PG.Sequence(2, 7000)

            time_point = 0
            seq.addPulseBoth(gau, time_point+100, 1, trigger=1)
            seq.addPulse(mark_qubit, time_point, 5, trigger=1)
            seq.addPulseBoth(gau_ef, time_point+600, 1, trigger=0)
            seq.addPulse(mark_qubit, time_point+500, 5, trigger=0)
            
            seq.addPulse(box, time_point+100, 3, trigger=1)
            seq.addPulse(mark_cav, time_point, 6, trigger=1)
            
            seq.addPulseBoth(gau_ef, time_point+5000, 1, trigger=0)
            seq.addPulse(mark_qubit, time_point+4900, 5, trigger=0)
            seq.addPulseBoth(gau, time_point+6000, 1, trigger=0)
            seq.addPulse(mark_qubit, time_point+5900, 5, trigger=0)      

            time_point += 7000                                    # Second Msmt
            seq.addPulseBoth(gau_id, time_point+100, 1, trigger=1)
            seq.addPulse(mark_qubit, time_point, 5, trigger=1)
            seq.addPulse(box, time_point+100, 3, trigger=1)
            seq.addPulse(mark_cav, time_point, 6, trigger=1)
            
        if AWG_wave == "single_pi_pulse":
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                              self.skew_phase, pi_pulse_amp, sigma)        
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            
            seq = PG.Sequence(1, 2000)  
            seq.addPulseBoth(gau, 100, 1, trigger=1)
            seq.addPulse(mark_qubit, 0, 5, trigger=1)
            seq.addPulse(box, 100, 3, trigger=1)
            seq.addPulse(mark_cav, 0, 6, trigger=1)

        if AWG_wave == "pi_pulse_tune_up":
            wave_num = 100
            seq = PG.Sequence(wave_num, 1000)
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            time_point = 0
            for i in range(wave_num):   
                amp_range = np.linspace(-1.0, 1.0, 100)
                amp  = amp_range[i]
                gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                                  self.skew_phase, amp, sigma)
                seq.addPulseBoth(gau, time_point + 100, 1, trigger=1)
                seq.addPulse(mark_qubit, time_point, 5, trigger=1)
                seq.addPulseBoth(box, time_point + 100, 3, trigger=1)
                seq.addPulse(mark_cav, time_point, 6, trigger=1)  
                time_point += 1000    
                
        if AWG_wave == 'ef_pi_pulse':
            wave_num = 100
            seq = PG.Sequence(wave_num, 2000)
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            time_point = 0
            gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                              self.skew_phase, pi_pulse_amp, sigma)
            for i in range(wave_num):   
                amp_range = np.linspace(-1.0, 1.0, 100)
                amp  = amp_range[i]
                freq = 0.3 + i*0.01
                
                seq.addPulseBoth(gau, time_point + 100, 1, trigger=1)
                seq.addPulse(mark_qubit, time_point, 5, trigger=1)
                
                gau_ef = PG.Gaussian(1, sigma*10, 0.322, self.iq_scale, 0, 
                                  self.skew_phase, amp, sigma)
                seq.addPulseBoth(gau_ef, time_point + 600, 1, trigger=0)
                seq.addPulse(mark_qubit, time_point + 500, 5, trigger=0)
                
                seq.addPulseBoth(box, time_point + 100, 3, trigger=1)
                seq.addPulse(mark_cav, time_point , 6, trigger=1)  
                time_point += 2000      
                
        if AWG_wave == 'ef_transition':
            wave_num = 100
            seq = PG.Sequence(wave_num, 2000)
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            time_point = 0
            gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                              self.skew_phase, pi_pulse_amp, sigma)
            for i in range(wave_num):   
                freq = 0.3 + i*0.001
                
                seq.addPulseBoth(gau, time_point + 100, 1, trigger=1)
                seq.addPulse(mark_qubit, time_point, 5, trigger=1)
                
                gau_ef = PG.Gaussian(1, sigma*10, freq, self.iq_scale, 0, 
                                  self.skew_phase, ef_pi_pulse_amp, sigma)
                seq.addPulseBoth(gau_ef, time_point + 600, 1, trigger=0)
                seq.addPulse(mark_qubit, time_point + 500, 5, trigger=0)
                
                seq.addPulseBoth(box, time_point + 100, 3, trigger=1)
                seq.addPulse(mark_cav, time_point , 6, trigger=1)  
                time_point += 2000      
                
        if AWG_wave == 't1':
            wave_num = 100
            pi_2_pulse_amp = pi_pulse_amp/2.0
            seq = PG.Sequence(wave_num, 1000)
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                              self.skew_phase, pi_pulse_amp, sigma)
            time_point = 0
            for i in range(wave_num):
                seq.addPulseBoth(gau, time_point + 100, 1, trigger=1)
                seq.addPulse(mark_qubit, time_point, 5, trigger=1)
                seq.addPulseBoth(box, time_point + 100, 3, trigger=1)
                seq.addPulse(mark_cav, time_point, 6, trigger=1)
                time_point += 1000

        if AWG_wave == 't2R':
            wave_num = 100
            pi_2_pulse_amp = pi_pulse_amp/2.0
            seq = PG.SequenceEasy(wave_num, 101000)
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            gau_2 = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                                self.skew_phase, pi_2_pulse_amp, sigma)
            time_point = 0
            
            for i in range(wave_num):
                time_interval = 500*(i+1)
                seq.addPulseBoth(gau_2, time_point+100, 1, trigger=1)
                seq.addPulseBoth(gau_2, time_point+300+time_interval+100, 1,
                                 trigger=0)
                seq.addPulse(mark_qubit, time_point, 5, trigger=1)
                seq.addPulse(mark_qubit, time_point+300+time_interval, 5, 
                             trigger=0)
                seq.addPulse(box, time_point+100, 3, trigger=1)
                seq.addPulse(mark_cav, time_point, 6, trigger=1)
                time_point += 101000

        if AWG_wave == 't2E':
            pi_2_pulse_amp = pi_pulse_amp/2.0
            wave_num = 100
            seq = PG.SequenceEasy(wave_num, 101000)
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            gau_2 = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                                self.skew_phase, pi_2_pulse_amp, sigma)
            gau = PG.Gaussian(1, sigma*10, 0.1, self.iq_scale, 0, 
                              self.skew_phase, pi_pulse_amp, sigma)
            time_point = 0
            for i in range(wave_num):
                time_interval = 500*(i+1)
                seq.addPulseBoth(gau_2, time_point+100, 1, trigger=1)
                seq.addPulseBoth(gau, time_point+600+time_interval/2+100, 1, 
                                 trigger=0)
                seq.addPulseBoth(gau_2, time_point+600+time_interval+100, 1, 
                                 trigger=0)

                seq.addPulse(mark_qubit, time_point, 5, trigger=1)
                seq.addPulse(mark_qubit, time_point+500+time_interval/2, 5, 
                             trigger=0)
                seq.addPulse(mark_qubit, time_point+500+time_interval, 5, 
                             trigger=0)

                seq.addPulse(box, time_point+600, 3, trigger=1)
                seq.addPulse(mark_cav, time_point+500, 6, trigger=1)
                time_point += 101000

        if AWG_wave == 'allxy':
            pi_2_pulse_amp = pi_pulse_amp/2.0
            seq = PG.Sequence(42, 2000)
            box = PG.Square(1, box_length, 0, 1, 0, 0, box_amp)
            mark_qubit = PG.Square(1, int(sigma*6.5), 0, 1, 0, 0, 1)
            mark_cav = PG.Square(1, int(box_length/2.0+200), 0, 1, 0, 0, 1)
            gau_x = PG.Gaussian(1, 10*sigma, 0.1, self.iq_scale, 0, 
                                self.skew_phase, pi_pulse_amp, sigma)
            gau_y = PG.Gaussian(1, 10*sigma, 0.1, self.iq_scale, np.pi/2., 
                                self.skew_phase, pi_pulse_amp, sigma)
            gau_x2 = PG.Gaussian(1, 10*sigma, 0.1, self.iq_scale, 0, 
                                 self.skew_phase, pi_2_pulse_amp, sigma)
            gau_y2 = PG.Gaussian(1, 10*sigma, 0.1, self.iq_scale, np.pi/2., 
                                 self.skew_phase, pi_2_pulse_amp, sigma)
            gau_id = PG.Gaussian(1, 10*sigma, 0.1, self.iq_scale, 0, 
                                 self.skew_phase, 0.0, sigma)
            pulse_list = [gau_id, gau_id,
                          gau_x, gau_x,
                          gau_y, gau_y,
                          gau_x, gau_y,
                          gau_y, gau_x, #First Group
                          gau_x2, gau_id,
                          gau_y2, gau_id,
                          gau_x2, gau_y2,
                          gau_y2, gau_x2,
                          gau_x2, gau_y,
                          gau_y2, gau_x,
                          gau_x, gau_y2,
                          gau_y, gau_x2,
                          gau_x2, gau_x,
                          gau_x, gau_x2,
                          gau_y2, gau_y,
                          gau_y, gau_y2, #Second Group
                          gau_x, gau_id,
                          gau_y, gau_id,
                          gau_x2, gau_x2,
                          gau_y2, gau_y2 #Thrid Group
                         ]
            time_point = 0
            for i in range(42):
                seq.addPulseBoth(pulse_list[2*(i/2)], time_point + 100, 1, 
                                            trigger=1)
                seq.addPulseBoth(pulse_list[2*(i/2)+1], time_point + 600, 1, 
                                            trigger=0)
                seq.addPulse(mark_qubit, time_point, 5, trigger=1)
                seq.addPulse(mark_qubit, time_point + 500, 5, trigger=0)
                seq.addPulse(box, time_point + 100, 3, trigger=1)
                seq.addPulse(mark_cav, time_point + 0, 6, trigger=1)
                time_point += 2000
                
        seq.checkFormat()
        seq.show_pulse()
        plt.show()
        return seq

    def AWGUpload(self, seq):
        '''
        Uploade into the AWG board RAM and queue.
        Input:
            Sequence Class.
        Output:
            None
        '''
        
        for i in range(len(seq.waveform_list)):
            temp_Wave = keysightSD1.SD_Wave()
            temp_Wave.newFromArrayDouble(0, seq.waveform_list[i])
            self.AWG1.waveformLoad(temp_Wave, i, 0)
            self.MARK1.waveformLoad(temp_Wave, i, 0)
        
        sequence_list = seq.sequence_list
        waveform_list = seq.waveform_list
        '''
        newFromArrayDouble(int waveformType, double waveformData)
        waveformType(0: Analog 16bits; 1: Analog 32bits)
        
        waveformLoad / into the module onboard RAM (SD Wave waveform Object, 
        int waveformNumber, int paddingMode)
        padding mode: (default 0)
        
        AWGqueueWaveform(int nAWG, int waveformNumber, int triggerMode, 
                         int startDelay (10ns) < must smaller than 65536 ns, 
                         int cycles, int prescaler)
        triggerMode(0: Auto; 1: SWHVITRIG; 5: SWHVITRIG_CYCLE; 2: EXTRIG; 
                    6: EXTRIG_CYCLE)
        '''
        for i in range(8):
            if len(sequence_list[i]) != 0:
                wait_time = 0
                if i <= 3:
                    num_seq = 0
                    for k in range(len(sequence_list[i])):
                        time_delay = sequence_list[i][k][1] - wait_time
                        if sequence_list[i][k][2] == 1:
                            time_delay = sequence_list[i][k][1] - \
                                            seq.sequence_length * num_seq
                            num_seq += 1
                        self.AWG1.AWGqueueWaveform(i+1, sequence_list[i][k][0], 
                                                   sequence_list[i][k][2], 
                                                   time_delay/10, 1, 0)
                        wait_time = sequence_list[i][k][1] + \
                                    len(waveform_list[sequence_list[i][k][0]])
                        
                else:
                    wait_time = 0
                    num_seq = 0
                    for k in range(len(sequence_list[i])):
                        time_delay = sequence_list[i][k][1] - wait_time
                        if sequence_list[i][k][2] == 1:
                            time_delay = sequence_list[i][k][1] - \
                                         seq.sequence_length * num_seq
                            num_seq += 1
                            
                        self.MARK1.AWGqueueWaveform(i-3,sequence_list[i][k][0], 
                                                    sequence_list[i][k][2], 
                                                    time_delay/10, 1, 0)
                        wait_time = sequence_list[i][k][1] + \
                                    len(waveform_list[sequence_list[i][k][0]]) * 2
                                    
        print "Upload wave Succeed"
        print 'Wait for 1 sec, AWG and Mark start wait for trigger'
        time.sleep(1)
        self.AWG1.AWGstartMultiple(0b1111)
        self.MARK1.AWGstartMultiple(0b1111)
        return 0
        
    def DigFPGAReset(self):
        '''
        Reset Digitizer FPGA
        '''
        self.Digitizer.FPGAreset(2)
        print 'Reset FPGA and wait 0.1s'
        time.sleep(0.1)        
    
    def loadFirmware(self, filename):
        '''
        Load Digitizer FPGA
        Input:
            filename of FPGA (*.sbq)
        '''
        if self.Digitizer.FPGAload(filename) >=0:
            print filename, 'FPGA Load Succeed'
        else:
        	raise NameError('Plz check the firware you upload')
         
    def loadAWGFirmware(self, filename):
        '''
        Load AWG FPGA
        Input:
            filename of FPGA (*.sbq)
        '''
        if self.AWG1.FPGAload(filename) >=0:
            print filename, 'FPGA Load Succeed'
        else:
        	raise NameError('Plz check the firware you upload')       

    def writeDemodulateFunc(self, phase = 0.0, amp = 1.0):
        '''
        Write demodulate function(50 MHz sinusoidal)
        '''
        wave_sin_list = np.array((2**15-1) * amp * \
                        np.sin(((np.linspace(0,2,11)))*np.pi), dtype = int)
        wave_cos_list = np.array((2**15-1) * amp * \
                        np.cos(((np.linspace(0,2,11)))*np.pi), dtype = int)
        '''
        FPGAwritePCport(int nPCport, int [] data, int address, int addressMode, 
                        int accessMode)
        Address Mode: 0: Auto Increment; 1: Fixed; 
        Access Mode: 0: Non DMA; 1: DMA
        '''
        
        if not self.Digitizer.FPGAwritePCport(0, wave_sin_list, 0, 0, 0):
            print 'Write Sin wave successful'
        else:
            print 'Plz check, write PC port wrong'
        if not self.Digitizer.FPGAwritePCport(1, wave_cos_list, 0, 0, 0):
            print 'Write Cos wave successful'
        else:
            print 'Plz check, write PC port wrong'   
    
    def IQTraceTruncation(self, T_SIG = 18, T_REF = 18):
        '''
        Save the pre truncation point in the 'pre_run_info' as h5py format.
        Input: 
            initial pre truncation point.
        '''
        self.Digitizer.FPGAwritePCport(2, [T_SIG, T_REF], 0, 0, 0)
        self.HVI.start()
        print "HVI start, wait 0.1 sec, let the signal coming into the board"
        time.sleep(0.1)
        
        sig_truncation = self.Digitizer.FPGAreadPCport(3, 1, 0, 0, 0)[0]
        ref_truncation = self.Digitizer.FPGAreadPCport(3, 1, 4096, 0, 0)[0]
        print 'Signal first truncated: ', sig_truncation
        print 'Reference first truncated: ', ref_truncation

        self.pre_run_filename = 'pre_run_info'
        pre_run_file = h5py.File(self.pre_run_filename, 'w')
        pre_run_file.create_dataset("sig_truncation", data = sig_truncation)
        pre_run_file.create_dataset("ref_truncation", data = ref_truncation)
        pre_run_file.close()
        self.HVI.stop()
        print "Get first truncation point, now HVI STOP!"
        
    def integrateTruncation(self, int_start, int_end):
        '''
        Save the truncation point after integrate in the 'pre_run_info' 
        as h5py format.
        Input: 
            Integration start and end point.
        '''        
        self.int_start = int_start
        self.int_end = int_end
        pre_run_file = h5py.File('pre_run_info', 'r+')
        sig_truncation = pre_run_file["sig_truncation"].value
        ref_truncation = pre_run_file["ref_truncation"].value
        
        self.HVI.start()
        print "HVI start, wait 0.1 sec, let the signal coming into the board"
        
        self.Digitizer.FPGAwritePCport(2, [sig_truncation,ref_truncation,
                                           int_start/5, int_end/5], 0, 0, 0)
        time.sleep(0.1)
        print "Based on the following condition, determine the integration", \
              " truncation condition"
        print [sig_truncation,ref_truncation,int_start/5, int_end/5]
        
        sig_int_truncation = self.Digitizer.FPGAreadPCport(3, 1, 8192, 0, 0)
        ref_int_truncation = self.Digitizer.FPGAreadPCport(3, 1, 12288, 0, 0)
        
        print 'Signal integration truncated: ', sig_int_truncation
        print 'Reference integration truncated: ', ref_int_truncation
        try:
            pre_run_file.create_dataset("sig_int_truncation",
                                        data = sig_int_truncation)
            pre_run_file.create_dataset("ref_int_truncation", 
                                        data = ref_int_truncation)
        except RuntimeError:
            pre_run_file["sig_int_truncation"][...] = sig_int_truncation
            pre_run_file["ref_int_truncation"][...] = ref_int_truncation
        pre_run_file.close()        
        self.HVI.stop()
        print "Get integration truncation condition, now HVI STOP!"        
        
    def writeTruncationCondition(self, int_start, int_end):
        '''
        Read the truncation condtion from the 'pre_run_info' and write into
        the PC port. Notice here, you can change all the condition manually if 
        you find the result weird.
        Input:
            Integration start and end point.
        '''
        pre_run_file = h5py.File('pre_run_info', 'r')
        sig_truncation = pre_run_file["sig_truncation"].value
        ref_truncation = pre_run_file["ref_truncation"].value
        sig_int_truncation = pre_run_file["sig_int_truncation"].value
        ref_int_truncation = pre_run_file["ref_int_truncation"].value
        
        if not self.Digitizer.FPGAwritePCport(2, [sig_truncation , 
                                                  ref_truncation, 
                                                  int_start/5, int_end/5, 
                                                  sig_int_truncation, 
                                                  ref_int_truncation], 
                                                  0, 0, 0):
            print 'Input truncation point succeed.', [sig_truncation, 
                                                      ref_truncation,
                                                      int_start/5, 
                                                      int_end/5, 
                                                      int(sig_int_truncation), 
                                                      int(ref_int_truncation)]
        else:
            raise NameError('FPGA cannot access')

    def writeWeightFunction(self, I_weight, Q_weight, weight_start = 100, 
                            weight_end = 2099, default = True):
        '''
        Put weight function here. It will take root mean square of the I_weight
        and Q_weight.
        Inpi
        '''
        if default:
            I_weight_w = np.array(np.zeros(len(I_weight)) + (2**15 - 1), 
                                  dtype = int)[::5]
            Q_weight_w = np.array(np.zeros(len(I_weight)) + (2**15 - 1), 
                                  dtype = int)[::5]
        else:      
            temp_weight = np.sqrt(I_weight**2 + Q_weight**2)
            maximum = max(temp_weight)
            I_weight_w = np.array(temp_weight/maximum * (2**15 - 1), 
                                  dtype = int)[::5]
            Q_weight_w = np.array(temp_weight/maximum * (2**15 - 1), 
                                  dtype = int)[::5]
            
        a = self.Digitizer.FPGAwritePCport(2, [weight_start/5 - 6, 
                                               weight_end/5 - 6], 10, 0, 0)        
        b = self.Digitizer.FPGAwritePCport(2, I_weight_w[0:200], 
                                           4096, 0, 0)
        c = self.Digitizer.FPGAwritePCport(2, I_weight_w[200:400], 
                                           4096+200, 0, 0)
        f = self.Digitizer.FPGAwritePCport(2, Q_weight_w[0:200], 
                                           8192, 0, 0)
        g = self.Digitizer.FPGAwritePCport(2, Q_weight_w[200:400], 
                                           8192+200, 0, 0)
        if not (a+b+c+f+g):
            print 'weight function upload succeed'
        else:
            print 'wrong code: ', a,b,c,f,g
            raise NameError('Weight function wrong')
        return I_weight_w, Q_weight_w
    
    def writeFeedbackPoint(self, slope, intercept, k1, geflip, trigger_delay,
                           span):
        """
        if k>1, then k1 = 0
        if k<1, then k1 = 1
        """
        if not self.Digitizer.FPGAwritePCport(2, [slope, intercept, k1, 
                                                  geflip], 6, 0, 0):
            print 'write feed back point succeed'
        else:
            raise NameError('Did not find right address for feedback point')
        if not self.AWG1.FPGAwritePCport(3, [trigger_delay, span], 0, 0, 0):
            print 'write feed back point succeed'
        else:
            raise NameError('Did not find right address for feedback point')
            
    def writeFeedbackPoint_gefh(self, num_state, x_g, y_g, x_e, y_e, x_f, y_f, 
                                ef_start, ef_span, ge_start, ge_span):

        if not self.Digitizer.FPGAwritePCport(2, [num_state, x_g, y_g, x_e, 
                                                  y_e, x_f, y_f], 12, 0, 0):
            print 'write feed back point succeed'
        else:
            raise NameError('Did not find right address for feedback point')
        if not self.AWG1.FPGAwritePCport(3, [ef_start, ef_span, ge_start, 
                                             ge_span], 0, 0, 0):
            print 'write feed back point succeed'
        else:
            raise NameError('Did not find right address for feedback point') 
            
            
    def openHVI(self, filename):
        '''
        Open the HVI file here. Notice, you need to change the corresponding 
        module. However, we don't know if this is the must.
        '''
        HVI_ID = self.HVI.open(filename)
        if HVI_ID != -8031:
            raise NameError("HVI Wrong!")
        else:
            print filename + ' open succeed'
        self.HVI.assignHardwareWithIndexAndSlot(2, self.SLOT_NUM["CHASSIS"], 
                                                self.SLOT_NUM["AWG1"])
        self.HVI.assignHardwareWithIndexAndSlot(1, self.SLOT_NUM["CHASSIS"], 
                                                self.SLOT_NUM["MARK1"])
        self.HVI.assignHardwareWithIndexAndSlot(0, self.SLOT_NUM["CHASSIS"], 
                                                self.SLOT_NUM["DIG"])
        self.HVI.compile()
        self.HVI.load()        
    
    def digitizerInit(self, fullscale = 0.125):
        '''
        Initialize the digitizer here, set the prescaler and coupling if you
        need.
        Input:
            fullscale: prescaler of the input
        '''
        for i in range(4):
            # channelInputConfig(self, channel, fullScale(in Volt), 
            # impedance(0 is HiZ, 1 is 50ohm), coupling(0 is DC, 1 is AC))
            self.Digitizer.channelInputConfig(i+1, fullscale, 1, 1) 
            self.Digitizer.channelPrescalerConfig(i, 0)

    def digitizerRead(self, points_per_cycle, cycles, multi = 1, 
                      data_read_mask = "1111", trigger_delay = 0, 
                      timeout = 1000):
        '''
        Read all the data coming out from the DAQ.
        Input:
            point_per_cycle: integer
            cycles: integer
            multi: integer (how many times you want to repeat whole read)
            data_read_mask: '1111', corresponding to the channel you want to 
                            read. eg: 'DAQ1 and DAQ2': '0011'
            trigger_delay: # of samples you want to delay
            timeout: integer (it should be longer than the data acquisition)
        '''        
        if multi == 1:
            for i in range(4):
                self.Digitizer.DAQconfig(i+1, points_per_cycle, cycles, 
                                         trigger_delay, 1)
            print 'HVI reset'
            self.HVI.reset()
            print 'Digitizer start waiting Trigger'
            self.Digitizer.DAQstartMultiple(int(data_read_mask,2))
            data_read = np.zeros((4, points_per_cycle * cycles))
            print 'HVI start'
            self.HVI.start()
            for i in range(4):    
                if int(data_read_mask[-i+3]):
                    data_read[i] = self.Digitizer.DAQread(i+1, 
                                            points_per_cycle * cycles, timeout)
        
        else:
            data_read = np.zeros((4, points_per_cycle * cycles * multi))
            print 'Start taking data'
            for j in range(multi):
                print 'Multi ' + str(j+1) + '/' + str(multi) + ' read'
                for i in range(4):
                    self.Digitizer.DAQconfig(i+1, points_per_cycle, cycles, 
                                             trigger_delay, 1)
                self.HVI.reset()
                self.Digitizer.DAQstartMultiple(int(data_read_mask,2))
                self.HVI.start()
                for i in range(4):
                    if int(data_read_mask[-i+3]):
                        data_read[i, j * int(points_per_cycle * cycles): \
                        (j+1) * int(points_per_cycle * cycles)] = 
                        self.Digitizer.DAQread(i+1, points_per_cycle * cycles, 
                                               timeout)
            
        return data_read
               
    def dataProcess(self, data_read, points_per_cycle, cycles, multi, 
                    method = 1, wave_num = 100, fit = 0, lim = 10000, 
                    int_start=250, int_end=1500, filename='test'):
        '''
        Data Processing
        method=1: for the pre-run firmware, the rotation and integration will 
                  happen in the PC;
        method=2: for testing feedback, it will automatically plot two 
                  histogram, one is preaparation and second is after feedback.
        method=3: fitting one 2d gaussian.
        '''
        array1 = []
        array2 = []        
        if method == 1:
            num_records = cycles * multi
            num_points = points_per_cycle 
            I_data = np.zeros((num_records, num_points))
            Q_data = np.zeros((num_records, num_points))
            for i in range(num_records):
                S_I = data_read[0][i*num_points : (i+1)*num_points]
                S_Q = data_read[1][i*num_points : (i+1)*num_points]
                R_I = np.mean(data_read[2][i*num_points : (i+1)*num_points])
                R_Q = np.mean(data_read[3][i*num_points : (i+1)*num_points])
                R_mag = np.sqrt(R_I**2 + R_Q**2)        
                I_data[i, :] =  (S_I*R_I + S_Q*R_Q) / R_mag
                Q_data[i, :] = (-S_I*R_Q + S_Q*R_I) / R_mag        
                
            I_trace = np.mean(I_data, axis = 0)
            Q_trace = np.mean(Q_data, axis = 0)
            
            plt.figure('cavity response')
            plt.title('cavity response')
            plt.plot(I_trace)
            plt.plot(Q_trace)
            plt.xlabel('points')    
            
            
            plt.figure('IQ trace')
            plt.title('IQ trace')
            plt.plot(I_trace, Q_trace)
            plt.xlim([-1.1*lim, 1.1*lim])
            plt.ylim([-1.1*lim, 1.1*lim])               
            
            
            array1 = np.mean(I_data[:,int_start:int_end], axis = 1)
            array2 = np.mean(Q_data[:,int_start:int_end], axis = 1)    
            
            plt.figure('IQ Histogram')
            plt.title('IQ Histogram')
            result = plt.hist2d(array1, array2, bins = 101, 
                                range = [[-lim, lim], [-lim, lim]])
            
            I_data = I_trace
            Q_data = Q_trace
        
        elif method == 2: # feedback
            lim = lim
            I_data = data_read[2][0::2]
            Q_data = data_read[3][0::2]
            plt.figure()
            result = plt.hist2d(I_data, Q_data, bins = 101, 
                                range = [[-lim, lim], [-lim, lim]])
            plt.colorbar()
            I_data = data_read[2][1::2]
            Q_data = data_read[3][1::2]
            plt.figure()
            result = plt.hist2d(I_data, Q_data, bins = 101, 
                                range = [[-lim, lim], [-lim, lim]])
            plt.colorbar()
            
        elif method == 3: # fit one gaussian
            I_data = data_read[2]
            Q_data = data_read[3]
            xdata = 1
            lim = lim
            plt.figure()

            if fit:
                result = plt.hist2d(I_data, Q_data, bins = 101, 
                                    range = [[-lim, lim], [-lim, lim]])
                x1 = result[1][0:-1]
                y1 = result[2][0:-1]
                z1 = result[0]
                initial_guess = (1000, 1000)
                popt = DF.fit_2d_gaussian(x1,y1,z1,initial_guess)
                print popt

            else:
                plt.hist2d(I_data, Q_data, bins = 101, 
                           range = [[-lim, lim], [-lim, lim]])
             
        return I_data, Q_data

    def advancedDataProcess(self, xdata, data_read, average_num,
                            fridge_cooldown_date, project_name, 
                            msmt_name, file_name, angle = 0.0):
        '''
        Fitting the specific experiment and get the results.
        '''
        num_points = len(data_read[2])
        def data_rotate(I_data, Q_data, alpha = 0):
        
            temp = I_data + 1j*Q_data
            temp = temp*np.exp(1j*alpha)    
            
            return (temp.real, temp.imag)        
            
        if msmt_name is 'pi_pulse':
            I_data = np.mean(data_read[2].reshape(average_num,
                             num_points/average_num), axis=0)
            Q_data = np.mean(data_read[3].reshape(average_num,
                             num_points/average_num), axis=0)
            FA.pi_pulse_tune_up(I_data, Q_data, xdata)
        elif msmt_name is 't1':
            I_data = np.mean(data_read[2].reshape(average_num,
                             num_points/average_num), axis=0)
            Q_data = np.mean(data_read[3].reshape(average_num,
                             num_points/average_num), axis=0)
            FA.t1_fit(I_data, Q_data, xdata)
        elif msmt_name is 't2R':
            I_data = np.mean(data_read[2].reshape(average_num,
                             num_points/average_num), axis=0)
            Q_data = np.mean(data_read[3].reshape(average_num,
                             num_points/average_num), axis=0)
            FA.t2_ramsey_fit(I_data, Q_data, xdata)
        elif msmt_name is 't2E':
            I_data = np.mean(data_read[2].reshape(average_num,
                             num_points/average_num), axis=0)
            Q_data = np.mean(data_read[3].reshape(average_num,
                             num_points/average_num), axis=0)
            FA.t2_echo_fit(I_data, Q_data, xdata)
        elif msmt_name is 'allxy':
            I_data = np.mean(data_read[2][:average_num*42].reshape(average_num,
                         num_points/average_num), axis=0)
            Q_data = np.mean(data_read[3][:average_num*42].reshape(average_num,
                         num_points/average_num), axis=0)
            FA.allxy(I_data, Q_data, xdata)
        
        elif msmt_name is 'science_protocol':
            I_data = data_read[2][:average_num*9*20].reshape(average_num*60,
                             num_points/average_num/60)
            Q_data = data_read[3][:average_num*9*20].reshape(average_num*60,
                             num_points/average_num/60)
            msmt_name = 'test'
                             
        elif msmt_name is 'ef_transition':
            I_data = np.mean(data_read[2].reshape(average_num,
                             num_points/average_num), axis=0)
            Q_data = np.mean(data_read[3].reshape(average_num,
                             num_points/average_num), axis=0)
            plt.figure()
            plt.plot(xdata, I_data)
            plt.plot(xdata, Q_data)
            msmt_name = 'test'
            
        elif msmt_name is 'ef_pi_pulse':
            I_data = np.mean(data_read[2].reshape(average_num,
                             num_points/average_num), axis=0)
            Q_data = np.mean(data_read[3].reshape(average_num,
                             num_points/average_num), axis=0)
            FA.ef_pi_pulse_tune_up(I_data, Q_data, xdata)

            msmt_name = 'test'            
        return I_data, Q_data
        
    def moduleClose(self):
        '''
        Close all module
        '''
        self.AWG1.close()
        self.MARK1.close()
        self.Digitizer.close()
        self.HVI.stop()
        self.HVI.close()



