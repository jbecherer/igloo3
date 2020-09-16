import tkinter as tk
from tkinter import filedialog 
import numpy as np
import matplotlib.pylab as plt
import sys
import os
import datetime as dt
import scipy.io
import dbdreader




class fileFrame(): # {{{

    def __init__(self, rootW):
        self.Frame = tk.LabelFrame(rootW, text='files', padx=10, pady=10, borderwidth=2)

        self.addFileBut = tk.Button(self.Frame, text='add file', command=self.addF2List)
        self.addFileBut.grid(row=0, column=0)
        self.loadFilesBut = tk.Button(self.Frame, text='update file and variable list', command=self.load_files, bg='lightblue')
        self.loadFilesBut.grid(row=100, column=0, columnspan=2)

        self.fileList = []
        self.parameterList = []


        self.varF = varFrame(rootW)
        self.varF.Frame.grid(row=0, column=2, padx=5,  pady=5)


    def addF2List(self):
        # file dialog
        fname = filedialog.askopenfilename(initialdir='./test_data_files/', title='choose file', 
                                            filetypes=(('full science' ,'*.ebd'), ('sience data' ,'*.tbd'),  ('eng data' ,'*.sbd'), ('full eng' ,'*.dbd'), ('all', '*.*')))
        
        # List index
        ItemInd = len(self.fileList)

        # add fid to fileList
        newLab = tk.Label( self.Frame, text=os.path.basename(fname) )
        rmBot  = tk.Button(self.Frame, text='remove', command= lambda: self.removeItemFromList(ItemInd) )
        self.fileList.append([fname, newLab, rmBot])

        # put new fname in Frame
        self.fileList[-1][1].grid(row=ItemInd+1, column=0)
        self.fileList[-1][2].grid(row=ItemInd+1, column=1)


    def removeItemFromList(self, ItemInd):
        #print('remove ' + self.fileList[ItemInd][0])

        # destroy Item
        self.fileList[ItemInd][1].destroy()
        self.fileList[ItemInd][2].destroy()
        self.fileList.pop(ItemInd)

        # repack all other Items
        newLLen = len(self.fileList)
        for i in range(newLLen):
            self.fileList[i][1].grid_forget()
            self.fileList[i][2].grid_forget()

        for i in range(newLLen):
            self.fileList[i][1].grid(row=i+1, column=0)
            #  del bottom
            self.fileList[i][2].config(command= lambda: self.removeItemFromList(i))
            self.fileList[i][2].grid(row=i+1, column=1)


    def load_files(self):
        #self.Frame.grid_forget()
        D = dbdreader.DBD(self.fileList[0][0])
        self.parameterList = D.parameterNames
        self.varF.update_dropdown( self.parameterList)
        self.varF.fileList = self.fileList
        self.varF.updateFileListLabel()

# }}}


class varFrame(): # {{{
    def __init__(self, rootW):
        self.Frame = tk.LabelFrame(rootW, text='variables', padx=10, pady=10)

        # dropdown 
        self.optionList = ['sci_water_temp', 'sci_water_cond'] # option list
        self.newOption = tk.StringVar()  # initialize option variable
        self.newOption.set(self.optionList[0]) # default option
        self.dropdown = tk.OptionMenu(self.Frame, self.newOption, *self.optionList)
        self.dropdown.grid(row=0,column=0, columnspan=1)

        self.addVarBut = tk.Button(self.Frame, text='add var', command=self.addVar2List)
        self.addVarBut.grid(row=0, column=1)
        self.UpdatePlotListBut = tk.Button(self.Frame, text='Load Data (update plot List)', 
                                            bg='lightblue', command=self.loadData)
        self.UpdatePlotListBut.grid(row=100, column=0, columnspan=2)

        
        tk.Label( self.Frame, text='time' ).grid(row=1,column=0)
        self.varList = []
        self.createVarListItem(self.optionList[0])
        self.createVarListItem(self.optionList[1])
        self.plotVarList()

        self.fileList = []
        self.FileLab = tk.Label( self.Frame, text='files to load: ' + str(len(self.fileList)) )
        self.FileLab.grid(row=99, column=0, columnspan=2)

        
        self.plotF = plotFrame(rootW)
        self.plotF.Frame.grid(row=0, column=3, padx=5,  pady=5)

    def loadData(self):
        # update variable list in plotting frame
        self.plotF.varList = ['time']
        for i in range(len(self.varList)):
            self.plotF.varList.append(self.varList[i][0])
        self.plotF.update_frame()

        # initialize data structure
        self.plotF.Data = []
        for i in range(len(self.plotF.varList)):
            self.plotF.Data.append(np.array([]))

        # load data
        for f in range(len(self.fileList)):
            tmpdbd = dbdreader.DBD(self.fileList[f][0])  # just file name
            tmpvarList = self.plotF.varList[1:] # all but time array
            tmpdata = tmpdbd.get_sync( *tmpvarList ) 
            for i in range(len(tmpdata)):
                self.plotF.Data[i] = np.concatenate( (self.plotF.Data[i],tmpdata[i]) )
               #print(len(self.plotF.Data))
               #print(self.plotF.Data[i])
        
        # convert time data
        self.plotF.Data[0] = np.asarray([dt.datetime.utcfromtimestamp(t) for t in self.plotF.Data[0]])


            

    def updateFileListLabel(self):
        self.FileLab.config(text='files to load: ' + str(len(self.fileList)))

    def addVar2List(self):
        #print('new option ' + self.newOption.get())
        self.createVarListItem(self.newOption.get())
        LLen = len(self.varList)
        self.varList[LLen-1][1].grid(row=LLen+1, column=0)
        self.varList[LLen-1][2].grid(row=LLen+1, column=1)


    def createVarListItem(self, VarName):
        ItemInd = len(self.varList)
        newLab = tk.Label( self.Frame, text=VarName )
        rmBot  = tk.Button(self.Frame, text='remove', command= lambda: self.removeItemFromList(ItemInd) )
        self.varList.append([VarName, newLab, rmBot])

    def plotVarList(self):
        LLen = len(self.varList)
        for i in range(LLen):
            self.varList[i][1].grid(row=i+2, column=0)
            self.varList[i][2].grid(row=i+2, column=1)

    def update_dropdown(self, varNames):
        self.optionList = varNames
        self.newOption.set(varNames[0]) # default option
        self.dropdown.destroy()
        self.dropdown = tk.OptionMenu(self.Frame, self.newOption, *self.optionList)
        self.dropdown.grid(row=0,column=0, columnspan=1)
        
    def removeItemFromList(self, ItemInd):
        # destroy Item
        self.varList[ItemInd][1].destroy()
        self.varList[ItemInd][2].destroy()
        self.varList.pop(ItemInd)

        # repack all other Items
        newLLen = len(self.varList)
        for i in range(newLLen):
            self.varList[i][1].grid_forget()
            self.varList[i][2].grid_forget()

        for i in range(newLLen):
            self.varList[i][1].grid(row=i+2, column=0)
            self.varList[i][2].grid(row=i+2, column=1)
            #  del bottom needs to be redirected
            self.varList[i][2].config(command= lambda: self.removeItemFromList(i))

# }}}


class plotFrame(): # {{{
    def __init__(self, rootW):
        self.Frame = tk.LabelFrame(rootW, text='plotting', padx=10, pady=10, borderwidth=2)
        self.containerFrame = tk.LabelFrame(self.Frame)

        self.plotBut = tk.Button(self.Frame, text='plot data', command=self.do_plot)
        self.plotBut.grid(row=3, column=1)

        self.addBut = tk.Button(self.Frame, text='add axis', command=self.add_ax)
        self.addBut.grid(row=0, column=0)
        self.rmBut = tk.Button(self.Frame, text='remove axis', state='disabled', command=self.remove_ax)
        self.rmBut.grid(row=0, column=1)

        self.varList = ['???','???']
        self.Naxis  = 2
        self.radioList = []
        self.radioVar = []
        self.axLab = ['x', 'y', 'y2', 'y3','y4','y5','y6']
        self.update_frame()

        self.Data = []

    def add_ax(self):
        self.rmBut.config(state='normal')
        self.Naxis = self.Naxis + 1
        if self.Naxis == 6: # if more than 6 axis switch off add axis button
            self.addBut.config(state='disabled')
        self.update_frame()

    def remove_ax(self):
        self.addBut.config(state='normal')
        self.Naxis = self.Naxis -1 
        if self.Naxis == 2: # min 2 axis
            self.rmBut.config(state='disabled')
        self.update_frame()


    def update_frame(self):
        # generate Radiobutton list
        self.containerFrame.destroy() 
        self.containerFrame = tk.LabelFrame(self.Frame)
        self.radioList = []
        self.radioVar = []
        for ax in range(self.Naxis):
            rvar = tk.IntVar()
            RBtmp = []
            for ivar in range(len(self.varList)):
                RBtmp.append( tk.Radiobutton(self.containerFrame, text='', variable=rvar, value=ivar ) )
            
            self.radioList.append(RBtmp)
            self.radioVar.append(rvar)

        # update frame
        for ax in range(self.Naxis):
            tk.Label( self.containerFrame, text=self.axLab[ax] ).grid(row=1, column=ax)
            for ivar in range(len(self.varList)):
                self.radioList[ax][ivar].grid(row=ivar+2, column=ax)

        for ivar in range(len(self.varList)):
            tk.Label( self.containerFrame, text=self.varList[ivar] ).grid(row=ivar+2, column=self.Naxis)
        
        self.containerFrame.grid(row=1,column=0, columnspan=2)


    def do_plot(self):
        p = []
        for ax in range(self.Naxis-1):
            if ax == 0:
                p.append(plt.subplot(self.Naxis-1,1,ax+1)) 
            else:
                p.append(plt.subplot(self.Naxis-1,1,ax+1, sharex=p[0] )) 

            plt.plot(self.Data[self.radioVar[0].get()], self.Data[self.radioVar[ax+1].get()], '.')
            txt = p[ax].text( 0, 1, self.varList[self.radioVar[ax+1].get()], ha='left', va='top', transform=p[ax].transAxes)
            txt.set_fontsize(12)
            txt.set_backgroundcolor([1, 1, 1, .5])
            
            if ax != self.Naxis-2:
                p[ax].tick_params(labelbottom=False)
            if ax == self.Naxis-2:
                p[ax].set_xlabel(self.varList[self.radioVar[0].get()], fontsize=14)
            
        
        plt.show()

# }}}




def main():
    rootWindow = tk.Tk()
    rootWindow.title('igloo3')


    fileF = fileFrame(rootWindow)
    fileF.Frame.grid(row=0, column=0, padx=5,  pady=5)

    rootWindow.mainloop()


if __name__ == "__main__":
        main()
