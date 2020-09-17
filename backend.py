import dbdreader
import datetime as dt
import numpy as np

class DataContainer(): # {{{
    def __init__(self):
        self.fileList = []
        self.parameterList = ['sci_water_temp', 'sci_water_cond']
        self.varList = []
        self.Data = []
    # }}}
    


    def addItem2VarList(self, varName):
        self.varList.append(varName)

    def rmItemVarList(self, ind):
        self.varList.pop(ind)

    def addItem2FileList(self, fname):
        self.fileList.append(fname)

    def rmItemFileList(self, ind):
        self.fileList.pop(ind)

    def clearFileList(self):
        self.fileList = []


    def updateParameterList(self):
        dbd = dbdreader.DBD(self.fileList[0])
        self.parameterList = dbd.parameterNames


    def loadData(self):
        # initialize data structure
        self.Data = []
        for i in range(len(self.varList)+1): # +1 is for time dimension
            self.Data.append(np.array([]))

        # load data
        for f in range(len(self.fileList)):
            tmpdbd = dbdreader.DBD(self.fileList[f])  # just file name
            tmpdata = tmpdbd.get_sync( *self.varList ) 
            for i in range(len(tmpdata)):
                self.Data[i] = np.concatenate( (self.Data[i],tmpdata[i]) )
        
        # convert time data
        self.Data[0] = np.asarray([dt.datetime.utcfromtimestamp(t) for t in self.Data[0]])

