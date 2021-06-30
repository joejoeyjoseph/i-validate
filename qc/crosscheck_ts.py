# Perform crosscheck between two datasets

import pandas as pd
import numpy as np


class crosscheck_ts:
    """Crosscheck time series of two datasets."""

    def __init__(self, conf):

        self.upper = conf['time']['window']['end']
        self.lower = conf['time']['window']['start']

        try:
            self.avg_method = conf['reference']['avg_method']
        except KeyError:
            self.avg_method = None

    def trim_ts(self, ts):
        """Trim time series to within upper and lower limits,
        as declared by users.
        """

        ts = ts.loc[ts.index >= self.lower]
        ts = ts.loc[ts.index <= self.upper]

        return ts

    def align_time(self, base, c):
        """Align datetime indices of baseline and comparison datasets.
        When the length of the resultant combine data frame does not match
        the user-defined, desired data length, print error messages.
        """

        print(self.avg_method)

        base_data = self.trim_ts(base['data'])
        comp_data = self.trim_ts(c['data'])

        # Match time series data frequencies
        # Baseline time series as 1st column

        # If averaging method is not defined, then perform a simple merge
        # according to time indices
        if self.avg_method is None:
            combine_df = pd.merge(
                base_data, comp_data, left_index=True, right_index=True)

        # Calculate mean of data and record at the end of the time step
        elif self.avg_method == 'end':

            if base['freq'] < c['freq']:

                base_data = base_data.resample(
                    str(c['freq'])+'T', label='right', closed='right').mean()

                print()
                print('averaging baseline data of '+str(base['freq'])
                      + ' s to '+str(c['freq'])+' s, at the end of')
                print('the measurement period.')

            if base['freq'] > c['freq']:

                comp_data = comp_data.resample(
                    str(base['freq'])+'T', label='right',
                    closed='right').mean()

            combine_df = pd.merge(
                base_data, comp_data, left_index=True, right_index=True)

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

        # data_len = (diff_minute + freq) / freq

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
