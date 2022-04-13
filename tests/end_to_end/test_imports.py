def test_basic_import(execute):
    code = """import math
x = math.sqrt(64)
"""
    res = execute(code)
    assert res.values["x"] == 64

# import x
# import x as a
# import x.y.z
# import x.y.*
# import x.y.z as a
# from x import y
# from x import *
# from x import y as a
# from x.y import z
# from x.y import *
# from x.y import z as a
