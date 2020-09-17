from itertools import chain

import logging

import dbdreader

logger = logging.getLogger("data_manager")
logger.setLevel(logging.DEBUG)

class Dataset(object):
    '''General dataset containing a number of glider dbd files

    Parameters
    ----------
    filenames : list of str
        filenames (can be unsorted) of dbd/ebd files or friends.

    The Dataset class provides a structure for containing dbd data, as
    well as the interface to query the filenames and parameters
    available, as well as methods to retrieve data.
    '''
    def __init__(self, filenames):
        self.dbds = self._load_dbs(filenames)
        
    def delete_filenames(self, filenames):
        # to be done. MultiDBD has no way to remove files yet.
        # best to provide MultiDBD with this feature.
        pass

    def get_filenames(self):
        '''
        Return a list of filenames in this data set.

        Returns
        -------
        list of str
        '''
        return self.dbds.filenames

    def get_parameters(self):
        '''
        Return a list of parameters available in this dataset
        
        Returns 
        -------
        list of str
        '''
        parameters = self.dbds.parameterNames
        return parameters['eng']+parameters['sci']

    def _get_info(self, dbd, field):
        if field == "file_open":
            info = dbd.get_fileopen_time()
        elif field == "mission":
            info = dbd.get_mission_name()
        else:
            info = None
        return info
    
    def get_file_info(self, filename, field):
        '''
        Get file information
        
        Parameters
        ----------
        filename : str
            name of file
        field : str {"file_open", "mission"}
            qualifier to select what information is to be returned.

        Returns
        -------
        int or str or None:
            open time of file (s since Epoch) or mission name
            Returns None if file or field is not found.
        '''
        info = None
        for dbd in chain(self.dbds.dbds['eng'], self.dbds.dbds['sci']):
            if dbd.filename == filename:
                info = self._get_info(dbd, field)
                break
        return info
    
    def _load_dbs(self, filenames):
        # loads all dbd files.
        logger.debug("Reading dbd files...")
        fns = dbdreader.DBDList(filenames)
        fns.sort()
        dbds = dbdreader.MultiDBD(filenames=fns)
        logger.debug("All dbd files read.")
        return dbds

    # Three methods to retreive data. Still to do is error handling.
    def get_timeseries(self, parameter):
        ''' Get a time series for parameter

        Parameters
        ----------
        parameter : str
            name of parameter

        Returns
        -------
        tuple of (np.array, np.array)
            time and parameter value vectors
        '''
        t, v = self.dbds.get(parameter)
        return t, v

    def get_xy(self, parameter, coparameter):
        '''Get two colocated parameters

        Parameters
        ----------
        parameter : str
            name of parameter
        coparameter : str
            name of second parameter

        Returns
        -------
        tuple of (np.array, np.array)
            parameter and coparameter value vectors

        Notes
        -----

        If the time base of the second parameter is different from the
        first parameter, the second parameter is interpolated onto the
        time base of the first parameter.
        '''

        x, y = self.dbds.get_xy(parameter, coparameter)
        return x, y

    def get_scatter(self, parameter, depth_parameters = "sci_water_pressure m_pressure m_depth"):
        ''' Get data for a scatter plot

        Parameters
        ----------
        parameter : str
            name of parameter 
        depth_parameters : str, default : "sci_water_pressure m_pressure m_depth"
            parameters that serve as depth reference, in order of preference, separated by a space.
        
        Returns
        -------
        tuple of (np.array, np.array, np.array)
            time, depth and parameter vectors.

        '''
        for dp in depth_parameters.split():
            try:
                t, v, p = self.dbds.get_sync(parameter, dp)
            except dbdreader.DbdError as e:
                if e.value == dbdreader.DBD_ERROR_NO_VALID_PARAMETERS and dp in e.mesg:
                    pass
                else:
                    raise e
            else:
                if dp == "m_depth":
                    p/=10
                break
        return t, p, v

    
class DataManager(object):

    def __init__(self):
        self.datasets = []
        

    def add_dataset(self, filenames):
        pass

    def delete_files_from_dataset(self, dataset_id, *filenames):
        pass

    def delete_dataset(self, dataset_id):
        pass

    def get_filenames(self):
        pass

    def get_parameters(self):
        pass

    def get_file_info(self, dataset_id, filename, info_field):
        pass


if __name__ == "__main__":
    import glob
    import os
    path = "~/gliderdata/nsb3_201907/ld/comet*.[st]bd"
    fns = glob.glob(os.path.expanduser(path))
    
    ds = Dataset(fns)

    
