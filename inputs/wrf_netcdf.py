# This is a basic parser for WRF NetCDF data.
#
# This input parser expects to be given a directory filled with netcdf
# files - each a grid at one particular time.
#
# We expect that the file has a field called XLAT which is a matrix of
# latitude values for the grid and XLONG which is a matrix of longitude
# values for the grid.

import os
import pathlib
from datetime import datetime
from netCDF4 import Dataset
import numpy as np
import pandas as pd

from qc import check_input_data


class wrf_netcdf:
    """WRF data class, using data from NetCDF files.
    Each NetCDF file should contain 1 time step of data.
    """

    def __init__(self, path, var, target_var):

        self.path = str(pathlib.Path(os.getcwd()).parent)+'/'+str(path)
        self.var = var
        self.target_var = target_var

    # For WRF mountain wave demo case
    def get_ij(self, ih, loc):
        """Return data index (i and j) for nc file at a specified target
        location.
        """

        lat = np.array(ih['XLAT'])
        lon = np.array(ih['XLONG'])

        # If lat/lon were arrays (instead of matrixes)
        # something like this would work:
        # d = np.fromfunction(lambda x,y: (lon[x] - loc['lon'])**2
        # + (lat[y] - loc['lat'])**2, (len(lon), len(lat)), dype=float)

        # This is most appropriate for Equator coordinates
        d = (lat - loc['lat'])**2 + (lon - loc['lon'])**2

        i, j = np.unravel_index(np.argmin(d), d.shape)

        return i, j

    def get_ts(self, loc, lev, freq, flag):
        """Get time series at a location at a certain height."""

        df = pd.DataFrame({'t': [], self.target_var: []})

        # To print an empty line before masked value error messages
        mask_i = 0

        for file in os.listdir(self.path):

            data = Dataset(self.path+'/'+file, 'r')
            i, j = self.get_ij(data, loc)

            s = file.split('_')[2]+'_'+file.split('_')[3].split('.')[0]+':'\
                + file.split('_')[4]+':'+file.split('_')[5].split('.')[0]
            t = datetime.strptime(s, '%Y-%m-%d_%H:%M:%S')

            height_ind = np.where(data['level'][:].data == lev)[0][0]

            u = data.variables[self.var[0]][height_ind][i][j]
            v = data.variables[self.var[1]][height_ind][i][j]
            ws = np.sqrt(u**2 + v**2)

            ws, mask_i = check_input_data.convert_mask_to_nan(ws, t, mask_i)
            ws = check_input_data.convert_flag_to_nan(ws, flag, t)

            data.close()

            df = df.append([{'t': t, self.target_var: ws}])

        df = df.set_index('t').sort_index()

        df = check_input_data.verify_data_file_count(df, self.target_var,
                                                     self.path, freq
                                                     )

        return df
