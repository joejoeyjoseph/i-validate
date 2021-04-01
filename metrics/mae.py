# This is a simple average mae calculation, mae = mean(|x - y|).

import numpy as np


class mae:

    def compute(self, x, y):

        return float(np.mean(abs(x - y)))
