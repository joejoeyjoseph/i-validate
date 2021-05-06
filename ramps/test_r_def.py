# This script runs unit tests for ramp definition files.

import importlib
import pandas as pd
import numpy as np
import math
from pandas._testing import assert_frame_equal

from tools import eval_tools

test_dir = 'ramps'

# Example data series
x_eg = pd.Series([2, 2, 2, 2, 16])
y_eg = pd.Series([4, 5, 6, -7, 8])

conf_eg = {'base': {'target_var': 'base_col'},
           'ramps': {'duration': '2 hours', 'magnitude': 2}
           }
c_eg = {'target_var': 'comp_col'}

index_eg = pd.to_datetime(pd.Series(
    ['2020-10-31 00:00', '2020-10-31 01:00',
     '2020-10-31 02:00', '2020-10-31 03:00',
     '2020-10-31 04:00', '2020-10-31 05:00',
     '2020-10-31 06:00', '2020-10-31 07:00']))

data_eg = {
    'base_col': [60, 59, 40, 41, 42, 43, 20, 21],
    'comp_col': [20, 21, 22, 23, 40, 41, 40, 41],
}
ramp_data_eg = pd.DataFrame(data_eg, index=index_eg)


def read_ramp_def(ramp_def):

    return eval_tools.get_module_class(test_dir, ramp_def)


def test_r_magnitude():

    r = read_ramp_def('r_magnitude')(conf_eg, c_eg, ramp_data_eg)

    ramp_df_eg = ramp_data_eg.copy()
    ramp_df_eg = ramp_df_eg.iloc[:-2]
    ramp_df_eg['base_col'] = np.array([-20, -18, 2, 2, -22, -22], float)
    ramp_df_eg['comp_col'] = np.array([2, 2, 18, 18, 0, 0], float)
    ramp_df_eg['abs_diff_base'] = np.array([1, 1, 0, 0, 1, 1], float)
    ramp_df_eg['abs_diff_comp'] = np.array([0, 0, 1, 1, 0, 0], float)

    assert_frame_equal(r.get_rampdf(), ramp_df_eg)
