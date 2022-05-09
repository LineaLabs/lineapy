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
