# This is the manual slice of:
#  weekly
# from file:
#  sources/pandas_exercises/06_Stats/Wind_Stats/Exercises_with_solutions.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[pandas_stats]'

import datetime

import pandas as pd

data_url = "https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/06_Stats/Wind_Stats/wind.data"
data = pd.read_csv(data_url, sep="\\s+", parse_dates=[[0, 1, 2]])


def fix_century(x):
    year = x.year - 100 if x.year > 1989 else x.year
    return datetime.date(year, x.month, x.day)


data["Yr_Mo_Dy"] = data["Yr_Mo_Dy"].apply(fix_century)
data["Yr_Mo_Dy"] = pd.to_datetime(data["Yr_Mo_Dy"])
data = data.set_index("Yr_Mo_Dy")
weekly = data.resample("W").agg(["min", "max", "mean", "std"])
linea_artifact_value = weekly
