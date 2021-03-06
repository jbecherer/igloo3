import tkinter as tk
from tkinter import filedialog 
from tkinter import ttk 
import numpy as np
import matplotlib.pylab as plt
import sys
import os
import datetime as dt
import scipy.io
import dbdreader
from backend import * 
import FigurePlots





class fileFrame(): # {{{


    def __init__(self, rootW, Dcont):
        # create main frame
        self.Frame = tk.LabelFrame(rootW, text='files', padx=10, pady=10, borderwidth=2)
        
        # internal pointer to dat structure
        self.Dcont = Dcont

        # generate variable frame 
        self.varF = varFrame(rootW, Dcont)
        self.varF.Frame.grid(row=0, column=2, padx=5,  pady=5)

        # add main buittoms 
        self.addFileBut = tk.Button(self.Frame, text='add file', command=self.addF2List)
        self.addFileBut.grid(row=0, column=0)
        self.clearFileBut = tk.Button(self.Frame, text='clear list', command=self.clearList)
        self.clearFileBut.grid(row=0, column=1)
        self.loadFilesBut = tk.Button(self.Frame, text='update file and variable list', command=self.load_files, bg='lightblue')
        self.loadFilesBut.grid(row=100, column=0, columnspan=2)

        # List of filenames + remove buttons
        self.labRMList = []

        # inital path to look for files
        self.init_path = './'


    def addF2List(self):
        # file dialog
        fnames  = filedialog.askopenfilenames(initialdir=self.init_path, title='choose file', 
                                            filetypes=(('full science' ,'*.ebd'), ('sience data' ,'*.tbd'),  
                                                        ('eng data' ,'*.sbd'), ('full eng' ,'*.dbd'), ('all', '*.*')))
        
        for fname in fnames: # loop through all files to be opened

            # get new index at the end of the List 
            ItemInd = len(self.labRMList)

            # set new search path for next open file dialog
            self.init_path = os.path.dirname(fname)

            # add filename to file List
            self.Dcont.addItem2FileList(fname)

            # front end List of filelabels and remove buttons
            newLab = tk.Label( self.Frame, text=os.path.basename(fname) )
            rmBot  = tk.Button(self.Frame, text='remove', command= lambda: self.removeItemFromList(ItemInd) )
            self.labRMList.append([ItemInd, newLab, rmBot])

            # put new fname and remove button in frame
            self.labRMList[-1][1].grid(row=ItemInd+1, column=0)
            self.labRMList[-1][2].grid(row=ItemInd+1, column=1)

    def clearList(self):
        for i in range(len(self.labRMList)-1, -1, -1): # pop items backwards
            self.labRMList[i][1].destroy()
            self.labRMList[i][2].destroy()
            self.Dcont.rmItemFileList(i)
            self.labRMList.pop(i)

    def removeItemFromList(self, ItemInd):

        # remove old file item 
        # remove from front end list
        self.labRMList[ItemInd][1].destroy()
        self.labRMList[ItemInd][2].destroy()
        self.labRMList.pop(ItemInd)
        # remove from file data structure
        self.Dcont.rmItemFileList(ItemInd)

        # update the rest of the items
        newLLen = len(self.labRMList)
        for i in range(newLLen):
            self.labRMList[i][1].grid_forget()
            self.labRMList[i][2].grid_forget()

        for i in range(newLLen):
            self.labRMList[i][1].grid(row=i+1, column=0)

            # redirect del button to new index
            self.labRMList[i][2].config(command= lambda: self.removeItemFromList(i))
            self.labRMList[i][2].grid(row=i+1, column=1)


    def load_files(self):
        self.Dcont.updateParameterList()
        self.varF.update_dropdown( self.Dcont.parameterList)
        self.varF.updateFileListLabel()

# }}}


class varFrame(): # {{{
    def __init__(self, rootW, Dcont):
        
        # create main frame
        self.Frame = tk.LabelFrame(rootW, text='variables', padx=10, pady=10)

        # local pointer to data container 
        self.Dcont = Dcont

        # create plot frame
        self.plotF = plotFrame(rootW, Dcont)
        self.plotF.Frame.grid(row=0, column=3, padx=5,  pady=5)

        # create  dropdown menue
        self.optionList = self.Dcont.parameterList # get option list
        self.newOption = tk.StringVar()  # initialize option variable
        self.newOption.set(self.optionList[0]) # default option
        # create dropdown
        self.dropdown = ttk.Combobox(self.Frame, textvariable=self.newOption, values=self.optionList)
        self.dropdown.grid(row=0,column=0, columnspan=1)

        # add main buttons
        self.addVarBut = tk.Button(self.Frame, text='add var', command=self.addVar2List)
        self.addVarBut.grid(row=0, column=1)
        self.UpdatePlotListBut = tk.Button(self.Frame, text='Load Data (update plot List)', 
                                            bg='lightblue', command=self.loadData)
        self.UpdatePlotListBut.grid(row=100, column=0, columnspan=2)

        
        # 1st variable in list is always time (also due to dbdreader.get_sync())
        tk.Label( self.Frame, text='time' ).grid(row=1,column=0)

        # list of labels and remove buttom for variables
        self.labRMList = []
        self.createVarListItem(self.optionList[0])
        self.createVarListItem(self.optionList[1])
        self.plotVarList()

        # just a file counter 
        self.FileLab = tk.Label( self.Frame, text='files to load: ' + str(len(self.Dcont.fileList)) )
        self.FileLab.grid(row=99, column=0, columnspan=2)


    def updateFileListLabel(self):
        # update file count 
        self.FileLab.config(text='files to load: ' + str(len(self.Dcont.fileList)))

    def addVar2List(self):
        # create new variable item
        self.createVarListItem(self.newOption.get())

        # get index of new item
        LLen = len(self.labRMList)
        # place new label and button in frame
        self.labRMList[LLen-1][1].grid(row=LLen+1, column=0)
        self.labRMList[LLen-1][2].grid(row=LLen+1, column=1)


    def createVarListItem(self, VarName):
        # last+1 index of list (for new item)
        ItemInd = len(self.labRMList)

        # generate new label + rm button and add to List
        newLab = tk.Label( self.Frame, text=VarName )
        rmBot  = tk.Button(self.Frame, text='remove', command= lambda: self.removeItemFromList(ItemInd) )
        self.labRMList.append([ItemInd, newLab, rmBot])

        # add new itemp to data structure variable list
        self.Dcont.addItem2VarList(VarName)


    def plotVarList(self):
        # plot all variable labels and buttons
        LLen = len(self.labRMList)
        for i in range(LLen):
            self.labRMList[i][1].grid(row=i+2, column=0)
            self.labRMList[i][2].grid(row=i+2, column=1)

    def update_dropdown(self, varNames):
        self.optionList = varNames
        self.newOption.set(varNames[0]) # default option
        self.dropdown.destroy()
        self.dropdown = ttk.Combobox(self.Frame, textvariable=self.newOption, values=self.optionList)
        self.dropdown.grid(row=0,column=0, columnspan=1)
        
    def removeItemFromList(self, ItemInd):
        # destroy Item in Front end
        self.labRMList[ItemInd][1].destroy()
        self.labRMList[ItemInd][2].destroy()
        self.labRMList.pop(ItemInd)

        # remove varialbe from data container List
        self.Dcont.rmItemVarList(ItemInd)

        # re arrange variable list in front end
        newLLen = len(self.labRMList)
        for i in range(newLLen):
            self.labRMList[i][1].grid_forget()
            self.labRMList[i][2].grid_forget()

        for i in range(newLLen):
            self.labRMList[i][1].grid(row=i+2, column=0)
            self.labRMList[i][2].grid(row=i+2, column=1)
            #  del bottom needs to be redirected
            self.labRMList[i][2].config(command= lambda: self.removeItemFromList(i))

    def loadData(self):
        # update variable list in plotting frame
        self.plotF.updateVarList()
        self.plotF.update_frame()

        # load in Data
        self.Dcont.loadData()



# }}}


class plotFrame(): # {{{
    def __init__(self, rootW, Dcont):
        self.Frame = tk.LabelFrame(rootW, text='plotting', padx=10, pady=10, borderwidth=2)
        # container frame
        self.containerFrame = tk.LabelFrame(self.Frame)

        # loca lpointer to data structure
        self.Dcont = Dcont

        # main buttons 
        self.plotBut = tk.Button(self.Frame, text='plot data', command=self.do_plot)
        self.plotBut.grid(row=3, column=1)
        self.addBut = tk.Button(self.Frame, text='add axis', command=self.add_ax)
        self.addBut.grid(row=0, column=0)
        self.rmBut = tk.Button(self.Frame, text='remove axis', state='disabled', command=self.remove_ax)
        self.rmBut.grid(row=0, column=1)

        # initialize local varlist
        self.updateVarList()

        # number of plotting axis
        self.Naxis  = 2
        self.radioList = []
        self.radioVar = []
        self.axLab = ['x', 'y', 'y2', 'y3','y4','y5','y6']

        # update plotting frame
        self.update_frame()


    def updateVarList(self):
        self.varList = ['time']
        for var in self.Dcont.varList:
            self.varList.append(var)

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
        dataAxMap = []
        for ax in range(self.Naxis):
            dataAxMap.append(self.radioVar[ax].get())

        FigurePlots.FigureFrame(self.Dcont, dataAxMap)

# }}}




