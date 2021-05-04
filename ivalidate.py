# This script runs the comparison between timeseries data,
# as specified in config.yaml. This is the main routine for i-validate.
#
# config_test.yaml contains erroneous data that are designed for testing
# this code.
#
# Joseph Lee <joseph.lee at pnnl.gov>

import yaml
import sys
import importlib
import os
import pathlib
import numpy as np
import pandas as pd

from tools import eval_tools, cal_print_metrics


def compare(config=None):

    config_dir = str(pathlib.Path(os.getcwd()).parent)+'/config/'

    if config is None:
        config_file = config_dir+'config.yaml'
    else:
        config_file = config_dir+config

    sys.path.append('.')

    conf = yaml.load(open(config_file), Loader=yaml.FullLoader)

    base = conf['base']
    comp = conf['comp']
    p_curve = conf['power_curve']

    if 'ramps' in conf:
        print(conf['ramps']['definition'])
        # eval_tools.get_module_class('ramps', 'crosscheck_ts')(conf)
        ramps = [eval_tools.get_module_class('ramps', r)()
                 for r in conf['ramps']['definition']]
        print(ramps)
    # print((conf['ramps']))
    # print(conf in globals())

    print('validation start time:', conf['time']['window']['start'])
    print('validation end time:', conf['time']['window']['end'])
    print('location:', conf['location'])
    print('baseline dataset:', base['name'])
    print('variable:', conf['plot']['var'])

    # Load modules
    metrics = [eval_tools.get_module_class('metrics', m)()
               for m in conf['metrics']]
    print(metrics)
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
        base['input'] = eval_tools.get_module_class(
            'inputs', base['function'])(base, conf)

        base['data'] = base['input'].get_ts(lev)

        # For each specified comparison dataset
        for ind, c in enumerate(comp):

            print()
            print('********** for '+c['name']+': **********')

            # Run __init__
            c['input'] = eval_tools.get_module_class(
                'inputs', c['function'])(c, conf)

            c['data'] = c['input'].get_ts(lev)

            results = eval_tools.append_results(results, base, c, conf)

            # Crosscheck between datasets
            combine_df = crosscheck_ts.align_time(base['data'], c['data'])

            cal_print_metrics.run(
                combine_df, metrics, results, ind, c, conf, base, lev
                )

            plotting.plot_ts_line(combine_df, lev)
            plotting.plot_histogram(combine_df, lev)
            plotting.plot_pair_scatter(combine_df, lev)

            # import datetime
            ramp_data = cal_print_metrics.remove_na(combine_df, ramp_txt=True)

            ramp_data_dn = ramp_data.copy()
            ramp_data_dn.index = ramp_data_dn.index - pd.to_timedelta(
                str(conf['ramps']['duration']))

            ramp_df = (ramp_data_dn - ramp_data).dropna()
            zeros_col = np.zeros(len(ramp_df))
            ramp_df['abs_diff_base'] = zeros_col
            ramp_df['abs_diff_comp'] = zeros_col

            ramp_df.loc[abs(ramp_df['sodar_ws'])
                > conf['ramps']['magnitude'], ['abs_diff_base']] = 1
            ramp_df.loc[abs(ramp_df['wrf_ws'])
                > conf['ramps']['magnitude'], ['abs_diff_comp']] = 1

            false_col = np.zeros(len(ramp_df), dtype=bool)
            ramp_df['true_positive'] = false_col
            ramp_df['false_positive'] = false_col
            ramp_df['false_negative'] = false_col
            ramp_df['true_negative'] = false_col

            ramp_df.loc[((ramp_df['abs_diff_base'] != 0) & (ramp_df['abs_diff_comp'] != 0)), ['true_positive']] = True
            ramp_df.loc[((ramp_df['abs_diff_base'] == 0) & (ramp_df['abs_diff_comp'] != 0)), ['false_positive']] = True
            ramp_df.loc[((ramp_df['abs_diff_base'] != 0) & (ramp_df['abs_diff_comp'] == 0)), ['false_negative']] = True
            ramp_df.loc[((ramp_df['abs_diff_base'] == 0) & (ramp_df['abs_diff_comp'] == 0)), ['true_negative']] = True

            for i, row in ramp_df.iterrows():
                assert np.sum([row['true_positive'], row['false_positive'], row['false_negative'], row['true_negative']]) == 1

            true_pos = ramp_df['true_positive'].sum()
            false_pos = ramp_df['false_positive'].sum()
            false_neg = ramp_df['false_negative'].sum()
            true_neg = ramp_df['true_negative'].sum()

            assert true_pos+false_pos+false_neg+true_neg == len(ramp_df)

            pod = true_pos/(true_pos+false_neg)
            print(pod)
            csi = true_pos/(true_pos+false_pos+false_neg)
            print(csi)
            fbias = (true_pos+false_pos)/(true_pos+false_neg)
            far = false_pos/(true_pos+false_pos)
            print(fbias, far)

            fa = true_pos/(true_pos+false_pos)

            # TF = true_pos, FF = false_pos, MR = false_neg, TN = true_neg
            pss = ((true_pos*true_neg) - (false_pos*false_neg)) / ((true_pos+false_neg) * (false_pos+true_neg))
            print(fa, pss)

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
                  + str(p_curve['hub_height'])
                  + ' '+conf['levels']['height_units']
                  + ' #########################')
            print()
            print('use power curve: '+p_curve['file'])

            hh = p_curve['hub_height']

            hhws_df = all_lev_df.xs(hh, level=0, axis=1)

            pc_csv = eval_tools.get_module_class(
                'inputs', p_curve['function'])(
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
