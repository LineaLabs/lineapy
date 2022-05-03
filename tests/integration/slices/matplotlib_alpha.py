# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/matplotlib-tutorial/scripts/alpha.py

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[matplotlib_alpha]'

import matplotlib.pyplot as plt

size = 256, 16
dpi = 72.0
figsize = size[0] / float(dpi), size[1] / float(dpi)
fig = plt.figure(figsize=figsize, dpi=dpi)
fig.patch.set_alpha(0)
plt.axes([0, 0.1, 1, 0.8], frameon=False)
for i in range(1, 11):
    plt.axvline(i, linewidth=1, color="blue", alpha=0.25 + 0.75 * i / 10.0)
plt.xlim(0, 11)
plt.xticks([]), plt.yticks([])
plt.savefig("../figures/alpha.png", dpi=dpi)
