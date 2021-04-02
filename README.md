# i-validate

This infrastructure code enables comparison of time series from arbitrary data sources using user-defined metrics. The tool is designed to be simple, modulized, and extensible.

## Installation

### Cloning this repo to your machine

For Mac users, in Terminal, `cd` to a destinated directory, then

`git clone https://github.com/joejoeyjoseph/i-validate.git`

For Windows users, [Git for Windows](https://gitforwindows.org/) or running Linux Bash Shell on Windows is an option. 

Alternatively, you can also use GitHub clients like [GitHub Desktop](https://desktop.github.com/) to clone this repo to your local machine.

### Installing Python

This tool is built on Python 3.8. If you do not have Python on your machine, you can install [Python](https://www.python.org/) directly, or you can use package management software like [Anaconda](https://www.anaconda.com/). You can use this tool with your "root" Python, or you can use package and environment management systems like virtual environment or conda environment. Then in Terminal, 

`$ pip install -r requirements.txt`

This would download and install all the Python packages you need for this tool. 

If `pip` is not installed on your machine, you can visit the [pip website](https://pip.pypa.io/en/stable/installing/).

## Configuration

We use the YAML format for configuration. An example configuration is provided in `config.yaml`. Explanations are embedded in `config.yaml`, in which the comments started with `#`.

First, you need to specify the `location` (assumed to be the WGS84 latitude, `lat`, and longitude, `lon`, coordinates) as well as the evaluation duration in `time` (the `start` and `end` times).

To do a comparison, you will need at least one baseline dataset (called `base`) and one or more datasets to make comparisons to (called `comp`). Each dataset has a data directory (`path`), data parser (`function`), and variable (`var`). The `function` string must match one of the classes in the `inputs` directory.

If the nature of the variable of interest is wind speed (`ws`), you can choose a wind turbine power curve, specify its data directory (`path`), power curve file (`file`), and data parser (`function`), and the tool will compute metrics based on derived wind power.

Evaluation at different height levels above ground level is available, as long as the height levels exist in the baseline and comparison datasets.

Beyond the datasets, you can list which metrics to compute. Each must correspond to a metric class in the `metrics` directory. You can also specify the variable names (`var`) and units (`units`) to be displayed in the plots. 

Currently, only local datasets are supported. Future versions will fetch data over SFTP (i.e., PNNL DAP) and other protocols.

## Adding Metrics

To add a new metric, create a new file in the metrics folder. The filename must match the class name, so if you wanted to write a script that computes MAE, you might call the file metrics/mae.py and the class inside would also be called mae.

The metric class interface is simple, it defines a single method called 'compute' which takes two variables x (left) and y (right). Both are datetime-indexed pandas dataframes.

The function compute() must return a float (single, scalar number).

## Adding Inputs

To add a new data format (or source), create a new file in the inputs folder. As with metrics, the filename must match the class name. So, if you wanted to parse an HDF5 file you might call it hdf5.py and the class name in the file would also be hdf5.

The input class interface expects a constructor that takes the path and variable and a single method called get_ts() which takes a location hash with a lat and lon and returns the timeseries (datetime-indexed Pandas dataframe).

## Adding Preprocessors

To add a new preprocessor or QA/QC routine that operates on each timeseries, take a look in the 'prepare' directory.

## Parallelism

The current implementation is serial, however future versions may exploit local or distributed parallelism by:

  * Loading timeseries data from files (or cache) in parallel
  * Computing metrics for each pair of timeseries in parallel

## Contact information

Please contact Joseph Lee at <joseph.lee at pnnl.gov> for questions and comments. 