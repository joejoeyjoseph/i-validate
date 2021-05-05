# This script contains ramp plotting functions.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools


class plot_ramp:
    """Class for plotting 1 dimensional data at 1 height level."""

    def __init__(self, ramp_df, combine_df, conf):

        self.df = ramp_df
        self.combine_df = combine_df
        self.duration = conf['ramps']['duration']

        # self.var = conf['plot']['var']
        # self.lev_units = conf['levels']['height_units']

        # if conf['plot']['units'] == 'ms-1':
        #     self.units = r'm $s^{-1}$'
        # else:
        #     self.units = conf['plot']['units']

    def plot_ts_contingency(self):
        """
        """

        self.df['time'] = self.df.index

        self.df['tn_group'] = (self.df['true_negative'].diff(1) != 0).astype('int').cumsum()
        tn_true = self.df.loc[self.df['true_negative'] == True]
        
        duration_df = pd.DataFrame(
            {'start': tn_true.groupby('tn_group')['time'].first(),
                'end': tn_true.groupby('tn_group')['time'].last()}
            )

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

        self.df.index = self.df.index + (pd.to_timedelta(
            str(self.duration))/2)

        self.df.loc[self.df['abs_diff_base'] == 0, 'abs_diff_base'] = np.NaN
        self.df.loc[self.df['abs_diff_comp'] == 0, 'abs_diff_comp'] = np.NaN
        self.df['abs_diff_comp'] = self.df['abs_diff_comp'] - 0.1

        for col in self.combine_df.columns:
            ax1.plot(self.combine_df.index, self.combine_df[col], label=col)

        ax2.tick_params(left=False, labelleft=False)

        ax2.scatter(self.df.index, self.df['abs_diff_base'])
        ax2.scatter(self.df.index, self.df['abs_diff_comp'])

        ax2.axvspan(duration_df['start'].iloc[0], duration_df['end'].iloc[0], 0.8, 1)
        ax2.axvspan(duration_df['start'].iloc[1], duration_df['end'].iloc[1], 0.4, 0.5)
        ax2.axvspan(duration_df['start'].iloc[2], duration_df['end'].iloc[2])

        ax2.set_ylim([0.8, 1.1])
        # ax2.set_xticklabels(ax2.get_xticks(), rotation=90)
        ax2.tick_params(axis='x', labelrotation=90)
        # ax2.set_xticks(rotation=90)

        plt.show()

        # for pair in itertools.combinations(df.columns, 2):

        # for col in df.columns:
        #     plt.plot(df.index, df[col], label=col)

        # plt.xticks(rotation=90)
        # plt.legend()

        # plt.xlabel('time')

        # if self_units is True:
        #     plt.ylabel(self.var+' ('+self.units+')')
        # else:
        #     plt.ylabel(self.var)

        # plt.title(self.var+' at '+str(lev)+' m a.g.l.')

        # plt.show()

    def plot_pair_scatter(self, df, lev, self_units=True):
        """Generate scatter plots for each column pair."""

        # 1:1 line and text color
        onetoone_c = 'grey'
        # Best fit line color
        fit_c = 'green'

        for pair in itertools.combinations(df.columns, 2):

            fig, ax = plt.subplots()

            plt.scatter(df[pair[0]], df[pair[1]], c='k')

            line_min = np.nanmin([df[pair[0]], df[pair[1]]])
            line_max = np.nanmax([df[pair[0]], df[pair[1]]])
            xy1to1 = np.linspace(line_min*0.9, line_max*1.1)

            plt.plot(xy1to1, xy1to1, c=onetoone_c, linestyle='--')
            plt.text(0.95, 0.9, '1:1', c=onetoone_c, transform=ax.transAxes)

            if self_units is True:
                plt.xlabel(pair[0]+' ('+self.units+')')
                plt.ylabel(pair[1]+' ('+self.units+')')
            else:
                plt.xlabel(pair[0])
                plt.ylabel(pair[1])

            compute_df = df.dropna()
            x_fit = compute_df[pair[0]]
            y_fit = compute_df[pair[1]]

            # np.polyfit(deg=1) is linear regression
            coeffs = np.polyfit(x_fit, y_fit, 1)
            model_fn = np.poly1d(coeffs)

            # Calculate R^2 for the fit
            yhat = model_fn(x_fit)
            ybar = np.sum(y_fit)/len(y_fit)
            ssreg = np.sum((yhat - ybar)**2)
            sstot = np.sum((y_fit - ybar)**2)
            r2 = ssreg/sstot

            # For linear regression, this works too
            # from scipy import stats
            # slope, intercept, r_value, p_value, std_err = stats.linregress(
            #     x_fit, y_fit)

            x_s = np.arange(compute_df.min().min(), compute_df.max().max())

            plt.plot(x_s, model_fn(x_s), color=fit_c)

            # Linear equation for title
            plt.title(self.var+' at '+str(lev)+' '+self.lev_units
                      + ' a.g.l. \n linear fit: '+pair[0]+' = '
                      + str(round(coeffs[0], 3))
                      + ' * '+pair[1]+' + '+str(round(coeffs[1], 3))
                      + r'$, R{^2} = $'+str(round(r2, 3))
                      )

            plt.show()

    def plot_histogram(self, df, lev):
        """Generate histogram for each data column."""

        for col in df.columns:
            plt.hist(df[col], bins=15, alpha=0.4, label=col)

        plt.legend()

        plt.xlabel(self.var+' ('+self.units+')')
        plt.ylabel('count')
        plt.title(self.var+' at '+str(lev)+' m a.g.l.')

        plt.show()
