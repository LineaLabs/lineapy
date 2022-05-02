# This is the manual slice of:
#  plt.gcf()
# from file:
#  sources/matplotlib-tutorial/scripts/exercice_3.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[matplotlib_exercise_3]'

import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(8, 5), dpi=80)
plt.subplot(111)
X = np.linspace(-np.pi, np.pi, 256, endpoint=True)
C, S = np.cos(X), np.sin(X)
plt.plot(X, C, color="blue", linewidth=2.5, linestyle="-")
plt.plot(X, S, color="red", linewidth=2.5, linestyle="-")
plt.xlim(-4.0, 4.0)
plt.xticks(np.linspace(-4, 4, 9, endpoint=True))
plt.ylim(-1.0, 1.0)
plt.yticks(np.linspace(-1, 1, 5, endpoint=True))
linea_artifact_value = plt.gcf()
