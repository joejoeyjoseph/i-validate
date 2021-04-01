# Metrics

This directory contains algorithms to compute timeseries comparison metrics.

A metric file reads in time series `x` and `y` and compute, where `x` is the baseline (truth or observed) dataset and `y` is the comparison (model) dataset.

To add your own, simply copy an existing file or use the following template:

```
# The world's best metric.
#
# Daenerys Targaryen <daenerys.targaryen@kingslanding.got>

class dracarys:

    def compute(self, x, y):
      return None

```

Please also add unit tests to `test_metrics.py`, as follows:

```
def test_dracarys():

    metric_obj = eval_tools.get_module_class(test_dir, 'dracarys')()

    assert metric_obj.compute(0, 0) == 0
```