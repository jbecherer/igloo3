import dbdreader
import datetime as dt
import numpy as np

class DataContainer(): # {{{
    def __init__(self):
        self.fileList = []
        #self.parameterList = ['sci_water_temp', 'sci_water_cond', 'm_lat', 'm_lon', 'm_gps_lat', 'm_gps_lon', 'm_battpos', 'm_pitch']
        self.parameterList = ['variable']
        self.Data = []
        self.init_path = './'
        self.varList = []
        for par in self.parameterList:
          self.addItem2VarList(par)
    


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
        # loop trough all files until one has a working parameterlist
        for fid in self.fileList :
          dbd = dbdreader.DBD(fid)
          if len(dbd.parameterNames) > 0 :  
            break  # if there are parameters in the list break loop and use those

        if not dbd.parameterNames : # if no file contained proper parameter info
          print('------------------')
          print('!!!!  None of the provided files has sufficient parameter information')
          print('------------------')
        self.parameterList = dbd.parameterNames



    def loadData(self):
        # initialize data structure
        self.Data = []
        for i in range(len(self.varList)+1): # +1 is for time dimension
            self.Data.append(np.array([]))

        # load data
        for f in range(len(self.fileList)):
            tmpdbd = dbdreader.DBD(self.fileList[f])  # just file name
            # check if variables are in the file:
            inorout = np.zeros( (len(self.varList)) )
            loadingList = []
            for i in range(len(self.varList)) :
              if self.varList[i] in tmpdbd.parameterNames :
                inorout[i] = 1
                loadingList.append(self.varList[i])

            #tmpdata = tmpdbd.get_sync( *self.varList ) 
            tmpdata = tmpdbd.get_sync( *loadingList ) 
            cnt = 1  # index 0 is or the time vector
            self.Data[0] = np.concatenate( (self.Data[0],tmpdata[0]) )
            for i in range(len(inorout)):
                if inorout[i] == 1:
                  self.Data[i+1] = np.concatenate( (self.Data[i+1],tmpdata[cnt]) )
                  cnt += 1
                else: # if the variable was not in the file fill with nans
                  self.Data[i+1] = np.concatenate( (self.Data[i+1], np.ones(tmpdata[0].shape)*np.nan ) )
        
        # convert time data
        self.Data[0] = np.asarray([dt.datetime.utcfromtimestamp(t) for t in self.Data[0]])

    # }}}
