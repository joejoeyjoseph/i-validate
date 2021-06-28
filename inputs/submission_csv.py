# This is a parser for benchmark exercise submissions in csv format

import os
import pathlib
import pandas as pd


class submission_csv:

    def __init__(self, info, conf):

        self.path = str(pathlib.Path(os.getcwd()).parent)+'/'+str(info['path'])
        self.nature = info['nature']

    def get_ts(self, lev):

        df_all = pd.read_csv(self.path+'/'+'benchmark_ICON2km_wfip2_sodar.csv')

        if self.nature == 'ws':
            nature = 'speed'

        col = [s for s in df_all.columns if str(lev) in s and nature in s]

        df = df_all[col]

        df.set_index(df_all['time'], inplace=True)
        df.index.rename('t', inplace=True)
        df.index = pd.to_datetime(df.index)

        return df
