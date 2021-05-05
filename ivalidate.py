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

    print('validation start time:', conf['time']['window']['start'])
    print('validation end time:', conf['time']['window']['end'])
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

            if 'ramps' in conf:

                ramp_data = cal_print_metrics.remove_na(
                    combine_df, ramp_txt=True
                    )

                ramp_method = [eval_tools.get_module_class(
                    'ramps', r)(conf, ramp_data)
                    for r in conf['ramps']['definition']
                    ]
                # print(ramps)

                for r in ramp_method:

                    ramp_df = r.get_df()

                    process_ramp = eval_tools.get_module_class(
                        'ramps', 'process_rampdf')(ramp_df)

                    ramp_df = process_ramp.run()

                    print(ramp_df.head())
                    ramp_df['time'] = ramp_df.index
                    # ramp_df.loc[ramp_df['true_negative'] == False, 'true_negative'] = np.NaN
                    ramp_df['value_grp'] = (ramp_df.true_negative.diff(1) != 0).astype('int').cumsum()
                    print(ramp_df.head(20))
                    # print(ramp_df.groupby('value_grp'))
                    
                    print(ramp_df.loc[ramp_df['true_negative'] == True].groupby('value_grp')['time'].first())

                    plotting.plot_ts_line(combine_df, lev)

                    import matplotlib.pyplot as plt

                    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

                    # print(ramp_df.index)
                    ramp_df.index = ramp_df.index + (pd.to_timedelta(
                        str(conf['ramps']['duration']))/2)
                    # print(ramp_df.index)

                    ramp_df.loc[ramp_df['abs_diff_base'] == 0, 'abs_diff_base'] = np.NaN
                    ramp_df.loc[ramp_df['abs_diff_comp'] == 0, 'abs_diff_comp'] = np.NaN
                    ramp_df['abs_diff_comp'] = ramp_df['abs_diff_comp'] - 0.1

                    for col in combine_df.columns:
                        ax1.plot(combine_df.index, combine_df[col], label=col)

                    ax2.tick_params(left=False, labelleft=False)

                    # ax1 = plotting.plot_ts_line(combine_df, lev)

                    ax2.scatter(ramp_df.index, ramp_df['abs_diff_base'])
                    ax2.scatter(ramp_df.index, ramp_df['abs_diff_comp'])

                    axvspan

                    ax2.set_ylim([0.8, 1.1])
                    # ax2.set_xticklabels(ax2.get_xticks(), rotation=90)
                    ax2.tick_params(axis='x', labelrotation=90)
                    # ax2.set_xticks(rotation=90)

                    plt.show()

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

            print()
            print('not deriving power for '+c['name']+',')
            print('either baseline and compare data are not wind speed,\n'
                  + 'or hub height does not exist in validation data,\n'
                  + 'hence power curve is not derived'
                  )
