# Ramp magnitude
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd

from tools import cal_print_metrics


class r_magnitude:

    def __init__(self, conf, c, ramp_data):

        self.base_var = conf['base']['target_var']
        self.comp_var = c['target_var']
        self.ramps = conf['ramps']
        self.ramp_data = ramp_data
        self.reference = conf['reference']

    def get_rampdf(self):

        print()
        print('classfy as a ramp event when '+self.reference['var']
              + ' exceeds |'+str(self.ramps['magnitude'])
              + '| '+self.reference['units']+' in a window of '
              + self.ramps['duration']
              )

        ramp_data_dn = self.ramp_data.copy()
        ramp_data_dn.index = ramp_data_dn.index - pd.to_timedelta(
            str(self.ramps['duration']))

        ramp_df = (ramp_data_dn - self.ramp_data).dropna()
        zeros_col = np.zeros(len(ramp_df))
        ramp_df['base_ramp'] = zeros_col
        ramp_df['comp_ramp'] = zeros_col

        ramp_df.loc[abs(ramp_df[self.base_var])
                    > self.ramps['magnitude'], ['base_ramp']] = 1
        ramp_df.loc[abs(ramp_df[self.comp_var])
                    > self.ramps['magnitude'], ['comp_ramp']] = 1

        return ramp_df
