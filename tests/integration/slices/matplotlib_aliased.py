# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/matplotlib-tutorial/scripts/aliased.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[matplotlib_aliased]'

import matplotlib.pyplot as plt

size = 128, 16
dpi = 72.0
figsize = size[0] / float(dpi), size[1] / float(dpi)
fig = plt.figure(figsize=figsize, dpi=dpi)
fig.patch.set_alpha(0)
plt.axes([0, 0, 1, 1], frameon=False)
plt.rcParams["text.antialiased"] = False
plt.text(0.5, 0.5, "Aliased", ha="center", va="center")
plt.xlim(0, 1), plt.ylim(0, 1)
plt.xticks([]), plt.yticks([])
plt.savefig("../figures/aliased.png", dpi=dpi)
