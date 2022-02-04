# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/xgboost/demo/guide-python/sklearn_examples.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[xgboost_sklearn_examples]'

"""
Collection of examples for using sklearn interface
==================================================

Created on 1 Apr 2015

@author: Jamie Hall
"""
import pickle
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import fetch_california_housing

X, y = fetch_california_housing(return_X_y=True)
xgb_model = xgb.XGBRegressor(n_jobs=1)
clf = GridSearchCV(
    xgb_model,
    {"max_depth": [2, 4, 6], "n_estimators": [50, 100, 200]},
    verbose=1,
    n_jobs=1,
)
clf.fit(X, y)
pickle.dump(clf, open("best_calif.pkl", "wb"))
