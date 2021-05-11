# Ramps

This directory contains code relating to ramp classification. 

The script started with `r_` are ramp methods, and each script contains one method that classifies ramp events according to a specific algorithm or definition. Each ramp method must
  * generate a output dataframe via a `get_rampdf` function.
  * classify ramp events in the baseline dataset as `base_ramp` and ramp events in the comparison dataset as `comp_ramp`.

To add your own, simply copy an existing file or use the following template:

```
# The loftiest ramp defintion in Westeros.
#
# Daenerys Targaryen <daenerys.targaryen@motherofdragons.got>

class sōvētēs:

    def get_rampdf(self):

        ramp_df = None

        return ramp_df

```

The `process_ramp.py` script compares baseline and comparison ramps and categorize results based on a 2x2 contingency table, calculate ramp skill scores, etc.

Please also add unit tests to `test_r_def.py`. 