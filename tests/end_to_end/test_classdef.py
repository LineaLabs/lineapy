def test_basic_classdef(execute):
    code = """class A():
    def __init__(self, varname:str):
        self.varname = varname
a = A("myclass")
"""
    res = execute(code)
    assert res.values["a"].varname == "myclass"
