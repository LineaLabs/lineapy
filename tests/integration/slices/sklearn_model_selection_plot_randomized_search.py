# This is the manual slice of:
#  grid_search
# from file:
#  sources/scikit-learn/examples/model_selection/plot_randomized_search.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[sklearn_model_selection_plot_randomized_search]'

import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

X, y = load_digits(return_X_y=True, n_class=3)
clf = SGDClassifier(loss="hinge", penalty="elasticnet", fit_intercept=True)
param_grid = {
    "average": [True, False],
    "l1_ratio": np.linspace(0, 1, num=10),
    "alpha": np.power(10, np.arange(-2, 1, dtype=float)),
}
grid_search = GridSearchCV(clf, param_grid=param_grid)
grid_search.fit(X, y)
linea_artifact_value = grid_search
