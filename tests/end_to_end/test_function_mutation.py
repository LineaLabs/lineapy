import pytest

from lineapy.utils.utils import prettify


def test_mutation(execute):
    """
    Verify that mutating an item wil cause a dependency on the mutation.
    """
    source = "x = {}\nx['a'] = 3\n"
    res = execute(source, artifacts=["x"])
    assert res.artifacts["x"] == prettify(source)


def test_mutation_of_view(execute):
    """
    Verify that mutating a view will update the original.
    """
    source = """x = {}
y = {}
x['y'] = y
y['a'] = 1
"""
    res = execute(source, artifacts=["x", "y"])
    assert res.artifacts["x"] == prettify(source)
    assert res.artifacts["y"] == 'y = {}\ny["a"] = 1\n'


def test_before_after_mutation(execute):
    """
    Verify that references to an object before its mutated are different
    than after
    """
    source = """x = {}
before = str(x)
x['a'] = 1
after = str(x)
"""
    res = execute(source, artifacts=["x", "before", "after"])
    assert res.artifacts == {
        "x": prettify("x = {}\nx['a'] = 1\n"),
        "before": prettify("x = {}\nbefore = str(x)\n"),
        "after": prettify(
            "x = {}\nx['a'] = 1\nafter = str(x)\n",
        ),
    }


def test_view_of_view(execute):
    """
    Verify that mutating a view of a view will update the original.
    """
    source = """x = {}
y = {}
z = {}
x['y'] = y
y['z'] = z
z['a'] = 1
"""
    res = execute(source, artifacts=["x", "y", "z"])

    assert res.artifacts["z"] == prettify("z = {}\nz['a'] = 1\n")
    assert res.artifacts["y"] == prettify(
        "y = {}\nz = {}\ny['z'] = z\nz['a'] = 1\n"
    )
    assert res.artifacts["x"] == prettify(source)


def test_delitem(execute):
    """
    Verify that mutating a view of a view will update the original.
    """
    source = """x = {1: 1}
del x[1]
"""
    res = execute(source, artifacts=["x"])

    assert res.artifacts["x"] == source


@pytest.mark.slow
def test_self_return_loop(execute):
    """
    Verifies that if we return a value that is the same as the self arg,
    they will both be dependent on one another.
    """
    # From https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html
    code = """import numpy as np
from sklearn.dummy import DummyClassifier
X = np.array([-1, 1, 1, 1])
y = np.array([0, 1, 1, 1])
clf = DummyClassifier(strategy="most_frequent")
new_clf = clf.fit(X, y)
clf.fit(X, y)
new_clf.fit(X, y)
"""
    res = execute(code, artifacts=["new_clf", "clf"])
    assert res.artifacts["new_clf"] == prettify(code)
    assert res.artifacts["clf"] == prettify(code)
