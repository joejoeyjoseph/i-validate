# This script runs unit tests for metrics files.

import importlib
import pandas as pd
import math

from tools import eval_tools

test_dir = 'metrics'

# Example data series
x_eg = pd.Series([2, 2, 2, 2, 16])
y_eg = pd.Series([4, 5, 6, -7, 8])


def test_bias():

    metric_obj = eval_tools.get_module_class(test_dir, 'bias')()

    assert metric_obj.compute(5, 4) == -1


def test_series_bias():

    metric_obj = eval_tools.get_module_class(test_dir, 'bias')()

    assert metric_obj.compute(x_eg, y_eg) == -1.6


def test_bias_pct():

    metric_obj = eval_tools.get_module_class(test_dir, 'bias_pct')()

    assert metric_obj.compute(5, 4) == -20


def test_series_bias_pct():

    metric_obj = eval_tools.get_module_class(test_dir, 'bias_pct')()

    assert metric_obj.compute(x_eg, y_eg) == -10


def test_mae():

    metric_obj = eval_tools.get_module_class(test_dir, 'mae')()

    assert metric_obj.compute(5, 4) == 1


def test_series_mae():

    metric_obj = eval_tools.get_module_class(test_dir, 'mae')()

    assert metric_obj.compute(x_eg, y_eg) == 5.2


def test_mae_pct():

    metric_obj = eval_tools.get_module_class(test_dir, 'mae_pct')()

    assert metric_obj.compute(5, 4) == 20


def test_series_mae_pct():

    metric_obj = eval_tools.get_module_class(test_dir, 'mae_pct')()

    assert metric_obj.compute(x_eg, y_eg) == 190


def test_series_rmse():

    metric_obj = eval_tools.get_module_class(test_dir, 'rmse')()

    result = metric_obj.compute(x_eg, y_eg)

    assert math.isclose(result, 5.899, rel_tol=1e-4)


def test_series_crmse():

    metric_obj = eval_tools.get_module_class(test_dir, 'crmse')()

    result = metric_obj.compute(x_eg, y_eg)

    assert math.isclose(result, 5.678, rel_tol=1e-4)
