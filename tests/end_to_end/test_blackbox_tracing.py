import pytest

LINEA_CODE = """import lineapy
"""
CODE = """import matplotlib.pyplot as plt
import numpy as np

size = 256, 16
dpi = 72.0
figsize = size[0] / float(dpi), size[1] / float(dpi)
fig = plt.figure(figsize=figsize, dpi=dpi)
plt.axes([0, 0, 1, 1], frameon=False)

dash_styles = ["miter", "bevel", "round"]

for i in range(3):
    plt.plot(
        i * 4 + np.arange(3),
        [0, 1, 0],
        color="blue",
        dashes=[12, 5],
        linewidth=8,
        dash_joinstyle=dash_styles[i],
    )

plt.xlim(0, 12), plt.ylim(-1, 2)
plt.xticks([]), plt.yticks([])
plt.savefig("output/dash_joinstyle.png", dpi=dpi)

"""

ARTIFACT_CODE = """
artifact = lineapy.save(lineapy.file_system, "test_mplt")
"""


@pytest.mark.xfail("libraries used inside a blackbox are not captured")
def test_mplt_inside_blackbox_does_not_fail(execute):
    # simply a test to check if the code runs without exceptions.
    # Later on this will be edited to ensure that the slice is accurate.
    res = execute(LINEA_CODE + CODE + ARTIFACT_CODE, snapshot=False)
    assert res.values["artifact"].get_code() == CODE
    # assert res.values["fig"] is not None
