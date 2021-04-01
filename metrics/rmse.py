# This is a naive root mean squared error (RMSE) calculation,
# rmse = root(mean((x - y)^2))

import numpy as np


class rmse:

    def compute(self, x, y):

        return float(np.sqrt(np.mean((x - y)**2)))
