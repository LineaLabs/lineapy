# This is the manual slice of:
#  iris
# from file:
#  sources/pandas_exercises/10_Deleting/Iris/Exercises_with_solutions_and_code.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[pandas_deleting]'

import numpy as np
import pandas as pd

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
iris = pd.read_csv(url)
iris.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]
iris.iloc[10:30, 2:3] = np.nan
iris.petal_length.fillna(1, inplace=True)
del iris["class"]
iris.iloc[0:3, :] = np.nan
iris = iris.dropna(how="any")
iris = iris.reset_index(drop=True)
linea_artifact_value = iris
