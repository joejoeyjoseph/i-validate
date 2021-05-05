# Ramp magnitude
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd

from tools import cal_print_metrics


class r_magnitude:

    def __init__(self, conf, ramp_data):

        self.conf = conf
        self.ramp_data = ramp_data

    def get_df(self):

        ramp_data_dn = self.ramp_data.copy()
        ramp_data_dn.index = ramp_data_dn.index - pd.to_timedelta(
            str(self.conf['ramps']['duration']))

        ramp_df = (ramp_data_dn - self.ramp_data).dropna()
        zeros_col = np.zeros(len(ramp_df))
        ramp_df['abs_diff_base'] = zeros_col
        ramp_df['abs_diff_comp'] = zeros_col

        ramp_df.loc[abs(ramp_df['sodar_ws'])
                    > self.conf['ramps']['magnitude'], ['abs_diff_base']] = 1
        ramp_df.loc[abs(ramp_df['wrf_ws'])
                    > self.conf['ramps']['magnitude'], ['abs_diff_comp']] = 1

        return ramp_df
