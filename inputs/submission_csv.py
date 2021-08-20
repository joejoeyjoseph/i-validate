# This is a parser for benchmark exercise submissions in csv format

import collections
import os
import pathlib
import pandas as pd


class submission_csv:

    def __init__(self, info, conf):

        self.path = os.path.join(
            (pathlib.Path(os.getcwd()).parent), str(info['path'])
            )
        self.file = info['file']
        self.nature = info['nature']
        self.target_var = info['target_var']
        self.freq = info['freq']

    def get_ts(self, lev):

        df_all = pd.read_csv(os.path.join(self.path, self.file))

        if self.nature == 'ws':
            nature = 'speed'
        if self.nature == 'power':
            nature = 'power'

        if lev.is_integer() is False:
            lev_str = str(lev).replace('.', '-')
        else:
            lev_str = str(lev)

        col = [s for s in df_all.columns if lev_str in s and nature in s]
        
        # when col is an empty list
        if not col:
            lev_str = str(int(float(lev)))
            col = [s for s in df_all.columns if lev_str in s and nature in s]
        print(col)

        df = df_all[col]

        if len(col) > 1:
            print()
            print('!!!!!!!!!!')
            print('ERROR: SELECTING MULTIPLE COLUMNS')
            print('!!!!!!!!!!')

        df = df.rename(columns={col[0]: self.target_var})

        if 'time' in df_all.columns:
            t_col = 'time'
        if 'time (UTC)' in df_all.columns:
            t_col = 'time (UTC)'
        if 'Date & Time (UTC)' in df_all.columns:
            t_col = 'Date & Time (UTC)'

        df = df.set_index(df_all[t_col]).sort_index()
        df.index.rename('t', inplace=True)
        df.index = pd.to_datetime(df.index)

        # Does not need check_input_data.verify_data_file_count()
        # because 1 csv file contains all data points

        return df
