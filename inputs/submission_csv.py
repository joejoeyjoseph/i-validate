# This is a parser for benchmark exercise submissions in csv format

import os
import pathlib
import pandas as pd


class submission_csv:

    def __init__(self, info, conf):

        self.path = str(pathlib.Path(os.getcwd()).parent)+'/'+str(info['path'])
        self.file = info['file']
        self.nature = info['nature']
        self.target_var = info['target_var']
        self.freq = info['freq']

    def get_ts(self, lev):

        df_all = pd.read_csv(self.path+'/'+self.file)

        if self.nature == 'ws':
            nature = 'speed'

        col = [s for s in df_all.columns if str(lev) in s and nature in s]

        df = df_all[col]

        if len(col) > 1:
            print()
            print('!!!!!!!!!!')
            print('ERROR: SELECTING MULTIPLE COLUMNS')
            print('!!!!!!!!!!')

        df = df.rename(columns={col[0]: self.target_var})

        df = df.set_index(df_all['time']).sort_index()
        df.index.rename('t', inplace=True)
        df.index = pd.to_datetime(df.index)

        # Does not need check_input_data.verify_data_file_count()
        # because 1 csv file contains all data points

        return df