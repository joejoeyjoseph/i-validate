# This is a parser for FINO2 data.

import os
import pathlib
import pandas as pd
import numpy as np
import glob


class fino2_dat:
    """FINO2
    """

    def __init__(self, info, conf):

        self.path = str(pathlib.Path(os.getcwd()).parent)+'/'+str(info['path'])
        self.var = info['var']

    def get_ts(self, lev):

        file_list = glob.glob(self.path+'/*.dat')

        if len(file_list) == 1:

            dat_file = file_list[0]

            df_all = pd.read_csv(dat_file)

            var_name = df_all.iloc[0][0].split(': ', 1)[1]
            col_names = df_all.iloc[3][0].split('\t')[1:]

            df = pd.read_csv(dat_file, skiprows=6, sep='\s+')

            # turn column names into 1st row
            df = pd.DataFrame(np.vstack([df.columns, df]))

            # combine 2 time columns
            df['t'] = df[0].map(str)+' '+df[1]

            # drop duplicating columns
            df.pop(0)
            df.pop(1)

            for i in range(len(col_names)):

                df[col_names[i]] = df[i+2]
                df.pop(i+2)

            df = df.set_index('t').sort_index()

            df.index = pd.to_datetime(df.index)

            out_df = df.loc[:, [self.var]]

            out_df.rename(columns={self.var: var_name}, inplace=True)

            out_df = out_df.astype(float)

            return out_df
