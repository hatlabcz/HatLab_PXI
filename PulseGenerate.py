# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 16:32:19 2018

I tried my best keep the rules following pep-8, if you have any suggestions,
please contact the author.

@author: Pinlei Lu (Hat Lab)
email: pil9@pitt.edu
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

#########################   Define All Pulses  ################################

class Pulse(object): # Pulse.data_list, Pulse.I_data, Pulse.Q_data
    def __init__(self, name, width, ssb_freq, iqscale, phase, skew_phase):
        self.vmax = 1.0         # The max voltage that AWG is using
        self.name = name        # The name of each pulse. It is an integer number, more like a serial number for different type of pulse
        self.width = width      # How long the pulse is going to be. It is an integer number. 
        self.ssb_freq = ssb_freq    # The side band frequency, in order to get rid of the DC leakage from the mixer. Units: GHz.
        self.iqscale= iqscale       # The voltage scale for different channels (i.e. the for I and Q signals). It is a floating point number.
        self.phase = phase          # The phase difference between I and Q channels.
        self.skew_phase = skew_phase        
        self.Q_data = None          # The I and Q data that will has the correction of IQ scale
        self.I_data = None          # and phase. Both of them will be an array with floating number.
         
    def iq_generator(self, data):   
        # This method is taking "raw pulse data" and then adding the correction of IQ scale and phase to it.
        # The input is an array of floating point number.
        # For example, if you are making a Gaussain pulse, this will be an array with number given by exp(-((x-mu)/2*sigma)**2)
        # It generates self.Q_data and self.I_data which will be used to create waveform data in the .AWG file        
        # For all the pulse that needs I and Q correction, the method needs to be called after doing in the data_generator after 
        # you create the "raw pulse data"
    
    
        # Making I and Q correction
        tempx = np.arange(self.width)
        self.I_data = data * np.cos(tempx*self.ssb_freq*2*np.pi + self.phase)
        self.Q_data = data * np.sin(tempx*self.ssb_freq*2*np.pi + self.phase + self.skew_phase) * self.iqscale  
        
    def data_generator():
        pass

class Gaussian(Pulse):
    def __init__(self, name, width, ssb_freq, iqscale, phase, skew_phase, amp, deviation):
        super(Gaussian, self).__init__(name, width, ssb_freq, iqscale, phase, skew_phase)
        self.data_list = amp * signal.gaussian(width, deviation)
        self.iq_generator(self.data_list)

class Square(Pulse):
    def __init__(self, name, width, ssb_freq, iqscale, phase, skew_phase, height):
        super(Square, self).__init__(name, width, ssb_freq, iqscale, phase, skew_phase)
        x = np.arange(width)
        self.data_list = 0.5 * height * (np.tanh(x/2. - 5) - np.tanh(x/2. - width/2. + 5))
        self.iq_generator(self.data_list)

class Marker(Pulse):
    def __init__(self, name, width):
        super(Marker, self).__init__(name, width, 0, 1, 0, 0)
        x = np.zeros(width) + 1
        x[1] = 0.5
        x[-3] = 0.5
        x[0] = 0.1
        x[-2] = 0.1
        self.data_list = x
        self.I_data = self.data_list  
        self.Q_data = self.data_list
        
class Sin():
    def __init__(self, name, width, amp, freq, phase, smooth=False):
        phase = phase/180. * np.pi
        x = np.arange(width)
        y = amp * np.sin(x/(1000./freq) * 2.0 * np.pi + phase)
        data_out = y
        if smooth:
            data_out[0:11] = y[0:11] * np.exp(np.linspace(-5, 0, 11))
            data_out[-11:] = y[-11:] * np.exp(np.linspace(0, -5, 11)) 
            data_out[11:-11] = y[11:-11]
        self.width = width
        self.data_list = data_out
        self.I_data = data_out
        self.Q_data = data_out
        
class DC_Pulse(Pulse):
    def __init__(self, name, width, ssb_freq, iqscale, phase, skew_phase, height):
        super(DC_Pulse, self).__init__(name, width, ssb_freq, iqscale, phase, skew_phase)
        self.data_list = height + np.zeros(width)       
        self.iq_generator(self.data_list)
        
###############################################################################

#####################  Define All Sequences  ##################################
class SequenceEasy():
    """
    This class is easy mode of pulse generation, but make sure, no pulse
    superposition.
    """
    def __init__(self, num_shot, sequence_length = 1000):
        self.num_shot = num_shot
        self.sequence_length = sequence_length
        self.temp_sequence = {}        
        for i in range(8):
            self.temp_sequence[str(i+1)] = []            
        self.sequence_list = []
        self.waveform_list = []
        self.length_of_list = int((num_shot) * sequence_length) 
    
    def addPulseBoth(self, pulse, time, channel, trigger = 0):
        if channel in (1,3):
            I_value = pulse.I_data
            Q_value = pulse.Q_data
            waveform_num = self.updateWaveform(I_value)
            self.temp_sequence[str(channel)].append((waveform_num, time, trigger))
            waveform_num = self.updateWaveform(Q_value)
            self.temp_sequence[str(channel+1)].append((waveform_num, time, trigger))
        else:
            raise NameError("Wrong channel")
        return
    
    def addPulse(self, pulse, time, channel, trigger = 0):
        pulse_data = pulse.I_data
        waveform_num = self.updateWaveform(pulse_data)
        self.temp_sequence[str(channel)].append((waveform_num, time, trigger))
        return
    
    def updateWaveform(self, waveform):
        count = 0
        for i in range(len(self.waveform_list)):
            if np.sum(waveform != self.waveform_list[i]):
                pass
            else:
                count += 1
                waveform_num = i
        if count == 0:
            self.waveform_list.append(waveform)
            waveform_num = len(self.waveform_list) - 1
        return waveform_num
        
    def checkFormat(self):
        for i in range(8):
            self.sequence_list.append(self.temp_sequence[str(i+1)])
        return
    
    def show_pulse(self):
        plt.figure()
        for i in range(8):
            ydata = np.zeros(self.length_of_list)
            trigger_time = 0
            for k in range(len(self.sequence_list[i])):
                if i >= 4:
                    temp = np.zeros(self.length_of_list)
                    temp[self.sequence_list[i][k][1]:(self.sequence_list[i][k][1]+len(self.waveform_list[self.sequence_list[i][k][0]]) * 2)] =  1
                    ydata += temp
                else:
                    temp = np.zeros(self.length_of_list)
                    temp[self.sequence_list[i][k][1]:self.sequence_list[i][k][1]+len(self.waveform_list[self.sequence_list[i][k][0]])] =  self.waveform_list[self.sequence_list[i][k][0]]
                    ydata += temp
                if self.sequence_list[i][k][2]:
                    plt.subplot(8, 1, i+1)
                    plt.arrow(trigger_time,1,0,-0.5, width = 10, head_width = 30, head_length = 0.5, fc = 'k', ec = 'k')
                    trigger_time += self.sequence_length
            plt.subplot(8, 1, i+1)
            plt.subplots_adjust(hspace = 0)
            plt.plot(ydata)
            plt.tick_params(axis = 'y', labelsize = 10)
            plt.ylim(-1.2,1.2)
        plt.xlabel('time / ns')    
    
class Sequence():
    """
    This class is for fancy sequence generation, but may cost more time to
    analyze pulse behavior.
    """
    def __init__(self, num_shot, sequence_length = 1000, *args, **kwargs):
        self.num_shot = num_shot
        self.sequence_length = sequence_length
        self.length_of_list = int((num_shot) * sequence_length) 
        self.data_list = np.zeros((8, int(self.length_of_list)))
        self.waveform_list = [] # the list of all different waveform(go to the RAM)
        self.marker_list = [] # the list of marker going to RAM
        self.sequence_list = []
        self.test_list = np.zeros((8, int(self.length_of_list)))
        self.trigger_time = np.empty(0, dtype = int)

    def addPulseBoth(self, pulse, time, channel, trigger = 0, *args, **kwargs):
        if channel in (1,3):
            temp = np.zeros(self.length_of_list)
            temp[time:time + pulse.width] = pulse.I_data
            self.data_list[channel-1,:] += temp
            
            temp[time:time + pulse.width] = 1
            self.test_list[channel-1,:] += temp
            self.test_list[channel,:] += temp
            
            temp = np.zeros(self.length_of_list)
            temp[time:time + pulse.width] = pulse.Q_data
            self.data_list[channel,:] += temp
            

        elif channel in (2,4):
            raise NameError('Wrong Input')
            
        else:
            temp = np.zeros(self.length_of_list)
            temp[time:time + pulse.width] = pulse.data_list   
            self.data_list[channel-1,:] += temp
            
            temp[time:time + pulse.width] = 1
            self.test_list[channel-1,:] += temp
            
        if trigger:
            self.trigger_time = np.append(self.trigger_time, time)
        return      
        
    def addPulse(self, pulse, time, channel, trigger = 0, *args, **kwargs):
        temp = np.zeros(self.length_of_list)
        if channel in (1,3):
            temp[time:time + pulse.width] = pulse.I_data
            self.data_list[channel-1,:] += temp            
            temp[time:time + pulse.width] = 1
            self.test_list[channel-1,:] += temp
            
        elif channel in (2,4):
            temp[time:time + pulse.width] = pulse.I_data
            self.data_list[channel-1,:] += temp                  
            temp[time:time + pulse.width] = 1
            self.test_list[channel-1,:] += temp
            
        else:
            temp[time:time + pulse.width] = pulse.data_list   
            self.data_list[channel-1,:] += temp
            temp[time:time + pulse.width] = 1
            self.test_list[channel-1,:] += temp
            
        if trigger:
            self.trigger_time = np.append(self.trigger_time, time)
        return
        
    def updateWaveform(self, waveform):
        count = 0
        for i in range(len(self.waveform_list)):
            if np.sum(waveform != self.waveform_list[i]):
                pass
            else:
                count += 1
                waveform_num = i
        if count == 0:
            self.waveform_list.append(waveform)
            waveform_num = len(self.waveform_list) - 1
        
        return waveform_num
        
    def checkFormat(self):
        waveform_point = np.zeros((8, self.num_shot * 100), dtype = int) # the point of wave start and end
        waveform_count = 0 # num of waveform in one sequence
        for k in range(8):
            diff_list = [] # the list of all the points having value
            sequence_per_cycle = [] # the whole sequence in each channel
            if np.sum(self.data_list[k]):
                for i in range(len(self.data_list[k])):
                    if self.test_list[k,i] != 0:
                        diff_list.append(i)
                point_index = 0
                waveform_point[k, 0] = diff_list[0]   # We put all points which has value together
                
                for j in range(len(diff_list)-1):
                    if diff_list[j+1] - diff_list[j] > 10:
                        point_index += 1
                        waveform_point[k, point_index] = diff_list[j]
                        
                        temp = self.data_list[k, waveform_point[k,point_index-1]:waveform_point[k,point_index]]
                        waveform_num = self.updateWaveform(temp)
                    
                        if diff_list[j]-len(self.waveform_list[waveform_num]) in self.trigger_time: 
                            trigger_mode = 1                           
                        else: trigger_mode = 0

                        sequence_per_cycle.append((waveform_num, diff_list[j]-len(self.waveform_list[waveform_num]), trigger_mode))
                        
                        point_index += 1
                        waveform_point[k, point_index] = diff_list[j+1]
                        waveform_count += 1
                        
                waveform_point[k, point_index+1] = diff_list[-1]
                temp = self.data_list[k, waveform_point[k,point_index]:waveform_point[k,point_index+1]]
                waveform_num = self.updateWaveform(temp)
                if diff_list[j+1]-len(self.waveform_list[waveform_num]) in self.trigger_time: trigger_mode = 1                           
                else: trigger_mode = 0
                sequence_per_cycle.append((waveform_num, diff_list[j+1]-len(self.waveform_list[waveform_num]), trigger_mode))
            self.sequence_list.append(sequence_per_cycle)
        return
            
    def show_pulse(self):
        plt.figure()
        for i in range(8):
            ydata = np.zeros(self.length_of_list)
            trigger_time = 0
            for k in range(len(self.sequence_list[i])):
                if i >= 4:
                    temp = np.zeros(self.length_of_list)
                    temp[self.sequence_list[i][k][1]:(self.sequence_list[i][k][1]+len(self.waveform_list[self.sequence_list[i][k][0]]) * 2)] =  1
                    ydata += temp
                else:
                    temp = np.zeros(self.length_of_list)
                    temp[self.sequence_list[i][k][1]:self.sequence_list[i][k][1]+len(self.waveform_list[self.sequence_list[i][k][0]])] =  self.waveform_list[self.sequence_list[i][k][0]]
                    ydata += temp
                if self.sequence_list[i][k][2]:
                    plt.subplot(8, 1, i+1)
                    plt.arrow(trigger_time,1,0,-0.5, width = 10, head_width = 30, head_length = 0.5, fc = 'k', ec = 'k')
                    trigger_time += self.sequence_length
            plt.subplot(8, 1, i+1)
            plt.subplots_adjust(hspace = 0)
            plt.plot(ydata)
            plt.tick_params(axis = 'y', labelsize = 10)
            plt.ylim(-1.2,1.2)
        plt.xlabel('time / ns')

###############################################################################
       


    
if __name__ == '__main__':
    print 'Hello World'

    