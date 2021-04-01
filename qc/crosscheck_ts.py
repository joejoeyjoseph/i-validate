# Perform crosscheck of two datasets

import pandas as pd
import numpy as np


class crosscheck_ts:
    """Crosscheck time series of two datasets."""

    def __init__(self, conf):

        self.upper = conf['time']['window']['upper']
        self.lower = conf['time']['window']['lower']

    def trim_ts(self, ts):
        """Trim time series to within upper and lower limits,
        as declared by users.
        """

        ts = ts.loc[ts.index >= self.lower]
        ts = ts.loc[ts.index <= self.upper]

        return ts

    def align_time(self, base, comp):
        """Align datetime indices of baseline and comparison datasets.
        When the length of the resultant combine data frame does not match
        the user-defined, desired data length, print error messages.
        """

        base = self.trim_ts(base)
        comp = self.trim_ts(comp)

        # Match time series data frequencies
        # Baseline time series as 1st column
        combine_df = pd.merge(base, comp, left_index=True, right_index=True)

        t_min = combine_df.index.min()
        t_max = combine_df.index.max()

        freq = (combine_df.index[1] - t_min).total_seconds() / 60.0
        diff_minute = (t_max - t_min).total_seconds() / 60.0

        print()
        print('evaluate '+', '.join(combine_df.columns.values)
              + ' from '+str(t_min)+' to '+str(t_max)
              )
        print('every '+str(freq)+' minutes, total of '+str(len(combine_df))
              + ' time steps')

        data_len = (diff_minute + freq) / freq

        desired_period_minute = (self.upper - self.lower).total_seconds()\
            / 60.0

        desired_len = (desired_period_minute + freq) / freq

        if diff_minute != desired_period_minute:

            print()
            print('!!!!!!!!!!')
            print('WARNING: DESIERED EVALUATION DURATION DOES NOT MATCH '
                  + 'DATA DURATION'
                  )
            print('DESIRED: FROM '+str(self.lower)+' TO '+str(self.upper))
            print('DATA: FROM '+str(t_min)+' TO '+str(t_max))
            print('!!!!!!!!!!')

        # Correct
        if len(combine_df) == desired_len:

            pass

        else:

            print()
            print('!!!!!!!!!!')
            print('WARNING: DATA FREQUENCY DOES NOT MATCH DESIRED '
                  + 'EVALUATION PERIOD FREQUENCY')
            print('SHOULD HAVE '+str(desired_len)+' TIME STEPS IN DATA')
            print('ONLY HAVE '+str(len(combine_df))+' TIME STEPS IN DATA')
            print('!!!!!!!!!!')

        return combine_df
