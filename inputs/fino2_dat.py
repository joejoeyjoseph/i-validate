# This is a parser for FINO2 data.

import os
import pathlib


class fino2_dat:
    """FINO2
    """

    def __init__(self, path, var, target_var):

        self.path = str(pathlib.Path(os.getcwd()).parent)+'/'+str(path)
        self.var = var
        self.target_var = target_var

    def get_ts(self, lev, freq, flag):

        print(self.path)
