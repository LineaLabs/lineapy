# import pytest


def test_PIL_import_fs_artifact(execute):
    code = """import lineapy

from PIL.Image import open, new

new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")

lineapy.save(e, "testme")
"""
    res = execute(code)
    print(res.artifacts["testme"])
    assert (
        res.artifacts["testme"]
        == """from PIL.Image import open, new
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")
"""
    )
