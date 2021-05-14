# Ramp processing
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd


class process_ramp:
    """Class to process ramp results."""

    def __init__(self, ramp_df):

        self.df = ramp_df

    def add_contingency_table(self):
        """Categorize ramp forecast accuracy between baseline ramps
        and comparison ramps based on a 2x2 contingency table.
        """

        false_col = np.zeros(len(self.df), dtype=bool)
        self.df['true_positive'] = false_col
        self.df['false_positive'] = false_col
        self.df['false_negative'] = false_col
        self.df['true_negative'] = false_col

        self.df.loc[((self.df['base_ramp'] != 0)
                    & (self.df['comp_ramp'] != 0)),
                    ['true_positive']] = True
        self.df.loc[((self.df['base_ramp'] == 0)
                    & (self.df['comp_ramp'] != 0)),
                    ['false_positive']] = True
        self.df.loc[((self.df['base_ramp'] != 0)
                    & (self.df['comp_ramp'] == 0)),
                    ['false_negative']] = True
        self.df.loc[((self.df['base_ramp'] == 0)
                    & (self.df['comp_ramp'] == 0)),
                    ['true_negative']] = True

        # Confirm that only 1 of 4 categories contains a True signal
        # for each time step
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

    def print_contingency_table(self):
        """Print 2x2 contingency table"""

        data = [
            ['|', 'true positive: '+str(self.true_pos),
             '|', 'false positive: '+str(self.false_pos),
             '|', self.true_pos+self.false_pos],
            ['|', 'false negative: '+str(self.false_neg),
             '|', 'true negative: '+str(self.true_neg),
             '|', self.false_neg+self.true_neg],
            ['|', self.true_pos+self.false_neg, '|',
             self.false_pos+self.true_neg,
             '|', len(self.df)]
            ]

        print_df = pd.DataFrame(
            data,
            columns=['|', 'Benchmark: ramps', '|', 'Benchmark: no ramps',
                     '|', 'Total'],
            index=['Comparison: ramps', 'Comparison: no ramps', 'Total']
            )

        print('2x2 contingency table:')
        print(print_df)
        print()

    def cal_pod(self):

        pod = self.true_pos/(self.true_pos+self.false_neg)
        print('Probability of detection, or Ramp capture, or Hit percentage '
              + '(the fraction of ')
        print('observed ramp events that are actually forecasted): '
              + str(np.round(pod, 3)))
        print()

        return pod

    def cal_csi(self):

        csi = self.true_pos/(self.true_pos+self.false_pos+self.false_neg)
        print('Critical success index (the fraction of observed and/or '
              + 'forecasted events ')
        print('that are correctly predicted), where 1 is perfect prediction: '
              + str(np.round(csi, 3)))
        print()

        return csi

    def cal_fbias(self):

        fbias = (self.true_pos+self.false_pos)/(self.true_pos+self.false_neg)
        print('Frequency bias score (the ratio of the frequency of forecasted '
              + 'ramp events to the ')
        print('frequency of observed ramp events), where a negative value '
              + 'represents the system ')
        print('tends to underforecast and a positive value represents '
              + 'the system tends to ')
        print('overforecast: '+str(np.round(fbias, 3)))
        print()

        return fbias

    def cal_far(self):

        far = self.false_pos/(self.true_pos+self.false_pos)
        print('False alarm ratio (the fraction of predicted ramp events '
              + 'that did not occur): '+str(np.round(far, 3)))
        print()

        return far

    def cal_fa(self):

        fa = self.true_pos/(self.true_pos+self.false_pos)
        print('Forecast accuracy, or Success ratio (the fraction of '
              + 'predicted YES events ')
        print('that occurred): '+str(np.round(fa, 3)))

        return fa

    def cal_css(self):

        pss = ((self.true_pos*self.true_neg)
               - (self.false_pos*self.false_neg))\
            / ((self.true_pos+self.false_neg)
               * (self.false_pos+self.true_neg))

        return pss

    def cal_print_scores(self):
        """Calculate and print different skill scores."""

        print('ramp skill scores:')
        print()
        self.cal_pod()
        self.cal_csi()
        self.cal_fbias()
        self.cal_far()
        self.cal_fa()
