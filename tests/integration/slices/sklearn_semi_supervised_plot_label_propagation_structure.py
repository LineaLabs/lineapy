# This is the manual slice of:
#  label_spread
# from file:
#  sources/scikit-learn/examples/semi_supervised/plot_label_propagation_structure.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[sklearn_semi_supervised_plot_label_propagation_structure]'

import numpy as np
from sklearn.datasets import make_circles
from sklearn.semi_supervised import LabelSpreading

n_samples = 200
X, y = make_circles(n_samples=n_samples, shuffle=False)
outer, inner = 0, 1
labels = np.full(n_samples, -1.0)
labels[0] = outer
labels[-1] = inner
label_spread = LabelSpreading(kernel="knn", alpha=0.8)
label_spread.fit(X, labels)
linea_artifact_value = label_spread
