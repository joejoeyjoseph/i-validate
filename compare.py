# This script runs the comparison between timeseries data,
# as specified in config.yaml. This is the main routine for i-validate.
#
# config_test.yaml contains erroneous data that are designed for testing
# this code.
#
# Joseph Lee <joseph.lee@pnnl.gov>

import yaml
import sys
import importlib
import os
import pathlib
import numpy as np
import pandas as pd

from tools import eval_tools, cal_print_metrics

# config_file = str(pathlib.Path(os.getcwd()).parent)+'/config.yaml'
config_file = str(pathlib.Path(os.getcwd()).parent)+'/config_test.yaml'

sys.path.append('.')

conf = yaml.load(open(config_file), Loader=yaml.FullLoader)

base = conf['base']
comp = conf['comp']
p_curve = conf['power_curve']

print('validation start time:', conf['time']['window']['lower'])
print('validation end time:', conf['time']['window']['upper'])
print('location:', conf['location'])
print('baseline dataset:', base['name'])
print('variable:', conf['plot']['var'])

# Load modules
metrics = [eval_tools.get_module_class('metrics', m)()
           for m in conf['metrics']]
crosscheck_ts = eval_tools.get_module_class('qc', 'crosscheck_ts')(conf)
plotting = eval_tools.get_module_class('plotting', 'plot_data')(conf)

# Data frame containing data at all heights
all_lev_df = pd.DataFrame()

for lev in conf['levels']['height_agl']:

    # For data storage and metrics computation
    results = []

    print()
    print('######################### height a.g.l.: '+str(lev)
          + ' '+conf['levels']['height_units']+' #########################'
          )
    print()
    print('********** for '+base['name']+': **********')

    # Run __init__
    base['input'] = eval_tools.get_module_class('inputs', base['function'])(
        base['path'], base['var'], base['target_var']
        )

    base['data'] = base['input'].get_ts(lev, base['freq'], base['flag'])

    # For each specified comparison dataset
    for ind, c in enumerate(comp):

        print()
        print('********** for '+c['name']+': **********')

        # Run __init__
        c['input'] = eval_tools.get_module_class('inputs', c['function'])(
            c['path'], c['var'], c['target_var']
            )

        c['data'] = c['input'].get_ts(conf['location'], lev, c['freq'],
                                      c['flag']
                                      )

        results = eval_tools.append_results(results, base, c, conf)

        # Crosscheck between datasets
        combine_df = crosscheck_ts.align_time(base['data'], c['data'])

        cal_print_metrics.run(
            combine_df, metrics, results, ind, c, conf, base, lev
            )

        plotting.plot_ts_line(combine_df, lev)
        plotting.plot_histogram(combine_df, lev)
        plotting.plot_pair_scatter(combine_df, lev)

        combine_df.columns = pd.MultiIndex.from_product([[lev],
                                                        combine_df.columns]
                                                        )

        if all_lev_df.empty:
            all_lev_df = all_lev_df.append(combine_df)
        else:
            all_lev_df = pd.concat([all_lev_df, combine_df], axis=1)

# For power curve
for ind, c in enumerate(comp):

    pc_results = []

    # If both variables are wind speeds
    # and hub height exists in user-defined validation levels
    if (
        base['nature'] == 'ws' and c['nature'] == 'ws'
        and p_curve['hub_height'] in all_lev_df.columns.get_level_values(0)
    ):

        print()
        print('######################### deriving wind power at '
              + str(p_curve['hub_height'])+' '+conf['levels']['height_units']
              + ' #########################')
        print()
        print('use power curve: '+p_curve['file'])

        hh = p_curve['hub_height']

        hhws_df = all_lev_df.xs(hh, level=0, axis=1)

        pc_csv = eval_tools.get_module_class('inputs', p_curve['function'])(
            p_curve['path'], p_curve['file'], p_curve['ws'],
            p_curve['power'], hhws_df, hh, conf
            )

        power_df = pc_csv.get_power()

        pc_results = eval_tools.append_results(pc_results, base, c, conf)

        cal_print_metrics.run(
            power_df, metrics, pc_results, ind, c, conf, base, hh
            )

        # Plot simulated power curves, not extremely useful
        # pc_csv.plot_pc()
        pc_csv.plot_power_ts()

        pc_csv.plot_power_scatter()

    else:

        print('not deriving power for '+c['name']+',')
        print('either baseline and compare data are not wind speed,\n'
              + 'or hub height does not exist in validation data,\n'
              + 'hence power curve is not derived'
              )
