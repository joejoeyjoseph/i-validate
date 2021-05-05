# Ramp processing
#
# Joseph Lee <joseph.lee at pnnl.gov>

import numpy as np
import pandas as pd


class process_rampdf:

    def __init__(self, ramp_df):

        self.df = ramp_df

    def run(self):

        false_col = np.zeros(len(self.df), dtype=bool)
        self.df['true_positive'] = false_col
        self.df['false_positive'] = false_col
        self.df['false_negative'] = false_col
        self.df['true_negative'] = false_col

        # NEED to add flexibility to abs_diff_base
        self.df.loc[((self.df['abs_diff_base'] != 0) & (self.df['abs_diff_comp'] != 0)), ['true_positive']] = True
        self.df.loc[((self.df['abs_diff_base'] == 0) & (self.df['abs_diff_comp'] != 0)), ['false_positive']] = True
        self.df.loc[((self.df['abs_diff_base'] != 0) & (self.df['abs_diff_comp'] == 0)), ['false_negative']] = True
        self.df.loc[((self.df['abs_diff_base'] == 0) & (self.df['abs_diff_comp'] == 0)), ['true_negative']] = True

        for i, row in self.df.iterrows():
            assert np.sum([row['true_positive'], row['false_positive'], row['false_negative'], row['true_negative']]) == 1

        true_pos = self.df['true_positive'].sum()
        false_pos = self.df['false_positive'].sum()
        false_neg = self.df['false_negative'].sum()
        true_neg = self.df['true_negative'].sum()

        assert true_pos+false_pos+false_neg+true_neg == len(self.df)

        pod = true_pos/(true_pos+false_neg)
        print(pod)
        csi = true_pos/(true_pos+false_pos+false_neg)
        print(csi)
        fbias = (true_pos+false_pos)/(true_pos+false_neg)
        far = false_pos/(true_pos+false_pos)
        print(fbias, far)

        fa = true_pos/(true_pos+false_pos)

        pss = ((true_pos*true_neg) - (false_pos*false_neg)) / ((true_pos+false_neg) * (false_pos+true_neg))
        print(fa, pss)

        return self.df
