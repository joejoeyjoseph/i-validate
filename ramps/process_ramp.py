# Ramp processing
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd


class process_ramp:

    def __init__(self, ramp_df):

        self.df = ramp_df

    def run(self):

        false_col = np.zeros(len(self.df), dtype=bool)
        self.df['true_positive'] = false_col
        self.df['false_positive'] = false_col
        self.df['false_negative'] = false_col
        self.df['true_negative'] = false_col

        # NEED to add flexibility to abs_diff_base
        self.df.loc[((self.df['abs_diff_base'] != 0)
                    & (self.df['abs_diff_comp'] != 0)),
                    ['true_positive']] = True
        self.df.loc[((self.df['abs_diff_base'] == 0)
                    & (self.df['abs_diff_comp'] != 0)),
                    ['false_positive']] = True
        self.df.loc[((self.df['abs_diff_base'] != 0)
                    & (self.df['abs_diff_comp'] == 0)),
                    ['false_negative']] = True
        self.df.loc[((self.df['abs_diff_base'] == 0)
                    & (self.df['abs_diff_comp'] == 0)),
                    ['true_negative']] = True

        for i, row in self.df.iterrows():
            assert np.sum([row['true_positive'], row['false_positive'],
                   row['false_negative'], row['true_negative']]) == 1

        self.true_pos = self.df['true_positive'].sum()
        self.false_pos = self.df['false_positive'].sum()
        self.false_neg = self.df['false_negative'].sum()
        self.true_neg = self.df['true_negative'].sum()

        assert self.true_pos+self.false_pos
        + self.false_neg+self.true_neg == len(self.df)

        return self.df

    def cal_print_scores(self):

        print()

        pod = self.true_pos/(self.true_pos+self.false_neg)
        print('Probability of detection, or Ramp capture, or Hit percentage')
        print('(the fraction of observed ramp events that are actually')
        print('forecasted): '+str(np.round(pod, 3)))
        # print(np.round(pod, 3))
        print()

        csi = self.true_pos/(self.true_pos+self.false_pos+self.false_neg)
        print('Critical success index (the fraction of observed and/or')
        print('forecasted events that are correctly predicted), where')
        print('1 is perfect prediction: '+str(np.round(csi, 3)))
        # print(np.round(csi, 3))
        print()

        fbias = (self.true_pos+self.false_pos)/(self.true_pos+self.false_neg)
        print('Frequency bias score (the ratio of the frequency of forecasted')
        print('ramp events to the frequency of observed ramp events),')
        print('where a negative value represents the system tends to')
        print('underforecast and a positive value represents the system')
        print('tends to overforecast: '+str(np.round(fbias, 3)))
        # print(np.round(fbias, 3))
        print()

        far = self.false_pos/(self.true_pos+self.false_pos)
        print('False alarm ratio (the fraction of predicted ramp events')
        print('that did not occur):')
        print(np.round(far, 3))
        print()

        fa = self.true_pos/(self.true_pos+self.false_pos)
        print('Forecast accuracy, or Success ratio (the fraction of ')
        print('predicted YES events that occurred): '+str(np.round(fa, 3)))
        # print(np.round(fa, 3))

        pss = ((self.true_pos*self.true_neg)
               - (self.false_pos*self.false_neg))\
            / ((self.true_pos+self.false_neg)
               * (self.false_pos+self.true_neg))
        # print()