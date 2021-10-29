import pytest


def test_basic_classdef(execute):
    code = """class A():
    def __init__(self, varname:str):
        self.varname = varname
a = A("myclass")
"""
    res = execute(code)
    assert res.values["a"].varname == "myclass"


GLOBAL_MUTATE_CODE = """new_value="newval"
class A():
    def __init__(self, initialname:str):
        self.varname = initialname
    def update_name(newname:str):
        self.varname = newname

class Modifier():
    def modify_A(self,classinstance:A):
        classinstance.varname = new_value

a = A("origvalue")
b = Modifier()
b.modify_A(a)
"""


def test_mutate_classvar_values(execute):
    res = execute(GLOBAL_MUTATE_CODE)
    assert res.values["a"].varname == "newval"


@pytest.mark.xfail(
    reason="slicing calls to class's functions arent parsed \
since classes are blackboxes right now."
)
def test_mutate_classvar_slice(execute):
    res = execute(GLOBAL_MUTATE_CODE, artifacts=["a", "b"])
    assert res.artifacts["a"] == GLOBAL_MUTATE_CODE
    assert res.artifacts["b"] == GLOBAL_MUTATE_CODE
