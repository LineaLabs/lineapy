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
"""


def test_mplt_inside_blackbox_does_not_fail(execute):
    res = execute(CODE)
    assert res.success
    # assert res.values["fig"] is not None
