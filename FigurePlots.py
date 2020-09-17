import matplotlib
matplotlib.use("TkAgg")
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm
import os
import sys
import datetime as dt
import scipy.io


class FigureFrame(): # {{{
    def __init__(self, Dcont, dataAxMap):
        fig = plt.figure( figsize = (6, 6), facecolor = (1, 1, 1))
        
        self.Dcont = Dcont
        self.Naxis = len(dataAxMap)
        self.varList = Dcont.varList.copy()
        self.varList.insert(0, 'time') # add time as first item

        p = []
        for ax in range(self.Naxis-1):
            if ax == 0:
                p.append(plt.subplot(self.Naxis-1,1,ax+1)) 
            else:
                p.append(plt.subplot(self.Naxis-1,1,ax+1, sharex=p[0] )) 

            plt.plot(self.Dcont.Data[dataAxMap[0]], self.Dcont.Data[dataAxMap[ax+1]], '.')
            txt = p[ax].text( 0, 1, self.varList[dataAxMap[ax+1]], ha='left', va='top', transform=p[ax].transAxes)
            txt.set_fontsize(12)
            txt.set_backgroundcolor([1, 1, 1, .5])
            
            if ax != self.Naxis-2:
                p[ax].tick_params(labelbottom=False)
            if ax == self.Naxis-2:
                p[ax].set_xlabel(self.varList[dataAxMap[0]], fontsize=14)
            
        
        plt.show()
    
# }}}
