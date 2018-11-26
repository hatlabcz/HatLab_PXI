# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 11:22:23 2018

@author: Pinlei Lu
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

def gaussian_2d(x, y, amp, xm, ym, sigma_x, sigma_y):
    z = np.zeros((len(x), len(y)))
    for i in range(len(x)):
        for j in range(len(y)):
            z[i, j] = amp * np.exp(-(x[i] - xm)**2 / (2 * sigma_x**2)) * np.exp(-(y[j] - ym)**2 / (2 * sigma_y**2))
    return z 

def twoDGaussian((x, y), amplitude, sigma_x, sigma_y, xo, yo):
    xo = float(xo)
    yo = float(yo)
    g = amplitude * np.exp(-(x-xo)**2/(2*sigma_x**2)) * np.exp(-(y-yo)**2/(2*sigma_y**2))
    return g.ravel()   
    
def fit_2d_gaussian(xdata,ydata,zdata,initial_guess):
    before_fit = zdata.transpose().ravel()
    x = xdata
    y = ydata
    x, y = np.meshgrid(x, y)
    xindex, yindex = np.where(zdata == np.max(zdata))
    xycor = (xdata[xindex[0]], ydata[yindex[0]])
    amp = np.max(zdata)
    initial_guess += xycor
    initial_guess = (amp,) + initial_guess    
    popt, pcov = opt.curve_fit(twoDGaussian, (x, y), before_fit, p0 = initial_guess, maxfev = 10000)
    
    fig, ax = plt.subplots(1, 1)
    cax = ax.imshow(before_fit.reshape(101, 101), cmap=plt.cm.jet, origin='bottom',
        extent=(x.min(), x.max(), y.min(), y.max()))

    data_fitted = twoDGaussian((x,y), *popt)
    ax.contour(x, y, data_fitted.reshape(101, 101), 8, colors='w')
    fig.colorbar(cax)
    plt.show()       
    return popt

if __name__ == '__main__':
         

    initial_guess = (2, 2)

    x1 = np.linspace(-10, 10, 201)
    y1 = np.linspace(-10, 10, 201)
    z1 = gaussian_2d(x1, y1, 20.0, 0, -5, 2, 2) + np.random.normal(0, 0.2, (len(x1), len(y1))) + gaussian_2d(x1, y1, 20.0, 0, 5, 2, 2)

        
    popt = fit_2d_gaussian(x1,y1,z1,initial_guess)
    print 'x,y', popt[-2], popt[-1]
    print 'sigma', popt[1], popt[2]
    
    xvalue = np.random.rand(500) * 20 - 10
    yvalue = np.random.rand(500) * 20 - 10
    plt.figure()
    plt.plot(xvalue,yvalue, '*')
    g_count = 0
    e_count = 0
    for i in range(len(xvalue)):
        if np.sqrt(xvalue[i]**2 + (yvalue[i] - 5)**2) < 2:
            g_count += 1
        elif np.sqrt(xvalue[i]**2 + (yvalue[i] + 5)**2) < 2:
            e_count += 1
    print g_count,e_count