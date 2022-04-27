# This is the manual slice of:
#  apple_months
# from file:
#  sources/pandas_exercises/09_Time_Series/Apple_Stock/Exercises-with-solutions-code.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[pandas_timeseries]'

import pandas as pd

url = "https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/09_Time_Series/Apple_Stock/appl_1980_2014.csv"
apple = pd.read_csv(url)
apple.Date = pd.to_datetime(apple.Date)
apple = apple.set_index("Date")
apple_months = apple.resample("BM").mean()
linea_artifact_value = apple_months
