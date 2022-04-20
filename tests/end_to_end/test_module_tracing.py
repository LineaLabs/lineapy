from syrupy import snapshot


def test_sub(execute):
    code = """import lineapy
import matplotlib.pyplot as plt
for i in range(3):
    plt.plot([i, 2, 3], [10, 20, 30])
plt.savefig("test.png")
art = lineapy.save(lineapy.file_system, "artifact")
"""
    res = execute(code, snapshot=False)
    assert (
        res.slice("artifact")
        == """import matplotlib.pyplot as plt
for i in range(3):
    plt.plot([i, 2, 3], [10, 20, 30])
plt.savefig("test.png")
"""
    )
