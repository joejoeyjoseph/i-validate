# This script contains ramp plotting functions.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools


class plot_ramp:
    """Class for plotting 1 dimensional data at 1 height level."""

    def __init__(self, ramp_df, combine_df, conf, lev):

        self.df = ramp_df
        self.combine_df = combine_df
        self.duration = conf['ramps']['duration']
        self.var = conf['reference']['plot_var']
        self.lev_units = conf['levels']['height_units']
        self.lev = lev

        if conf['reference']['units'] == 'ms-1':
            self.units = r'm $s^{-1}$'
        else:
            self.units = conf['reference']['units']

    def get_duration_df(self, col):

        self.df['col_group'] = (
            self.df[col].diff(1) != 0).astype('int').cumsum()
        col_true = self.df.loc[self.df[col] == True]

        out_df = pd.DataFrame(
            {'start': col_true.groupby('col_group')['time'].first(),
             'end': col_true.groupby('col_group')['time'].last()}
            )

        return out_df

    def plot_ts_contingency(self):
        """
        """

        self.df.index = self.df.index + (pd.to_timedelta(
            str(self.duration))/2)

        self.df['time'] = self.df.index

        tp_df = self.get_duration_df('true_positive')
        fp_df = self.get_duration_df('false_positive')
        fn_df = self.get_duration_df('false_negative')
        tn_df = self.get_duration_df('true_negative')

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

        self.df.loc[self.df['abs_diff_base'] == 0, 'abs_diff_base'] = np.NaN
        self.df.loc[self.df['abs_diff_comp'] == 0, 'abs_diff_comp'] = np.NaN
        self.df['abs_diff_comp'] = self.df['abs_diff_comp'] - 0.1

        for col in self.combine_df.columns:
            ax1.plot(self.combine_df.index, self.combine_df[col], label=col)

        ax1.set_title('comparison at '+str(self.lev)+' '+self.lev_units)
        ax1.set_ylabel(self.var+' ('+self.units+')')
        ax1.legend()

        ax2.tick_params(left=False, labelleft=False)

        ax2.scatter(self.df.index, self.df['abs_diff_base'],
                    label='baseline ramp')
        ax2.scatter(self.df.index, self.df['abs_diff_comp'],
                    label='comparison ramp')

        def plot_duration_df(df, y_min, y_max, color):
            for i, row in df.iterrows():
                ax2.axvspan(row['start'], row['end'], y_min, y_max,
                            color=color, alpha=0.7)

        plot_duration_df(tp_df, 0.8, 1, 'dodgerblue')
        plot_duration_df(tn_df, 0.8, 1, 'navy')

        plot_duration_df(fp_df, 0, 0.2, 'red')
        plot_duration_df(fn_df, 0, 0.2, 'purple')

        ax2.set_ylim([0.7, 1.2])
        ax2.set_ylabel('periods of classified ramps & forecast results')
        ax2.tick_params(axis='x', labelrotation=90)
        ax2.set_xlabel('time')
        ax2.legend()

        ax2_fs = 12
        ax2.text(0.1, 0.7, 'true positive/hits', color='dodgerblue',
                 transform=ax2.transAxes, fontsize=ax2_fs)
        ax2.text(0.5, 0.7, 'true negative', color='navy',
                 transform=ax2.transAxes, fontsize=ax2_fs)
        ax2.text(0.1, 0.25, 'false positive/false alarm', color='red',
                 transform=ax2.transAxes, fontsize=ax2_fs)
        ax2.text(0.5, 0.25, 'false negative/misses', color='purple',
                 transform=ax2.transAxes, fontsize=ax2_fs)

        plt.show()
