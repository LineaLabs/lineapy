import datetime
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas
import PIL
import pytest
from click.testing import CliRunner

import lineapy
from lineapy.cli.cli import linea_cli
from lineapy.constants import ExecutionMode
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from tests.util import CSV_CODE, IMAGE_CODE, reset_test_db

publish_name = "testing artifact publish"
PUBLISH_CODE = f"""import {lineapy.__name__}
a = abs(11)
{lineapy.__name__}.{lineapy.linea_publish.__name__}(a, '{publish_name}')
"""


STRING_FORMAT = """a = '{{ {0} }}'.format('foo')"""


PANDAS_RANDOM_CODE = """from pandas import DataFrame
v = 4
df = DataFrame([[1,2], [3,v]])
df[0].astype(str)
assert df.size == 4
new_df = df.iloc[:, 1]
assert new_df.size == 2
"""

DICTIONARY_SUPPORT = """import pandas as pd
df = pd.DataFrame({"id": [1,2]})
df["id"].sum()
"""


PRINT_CODE = """a = abs(11)
b = min(a, 10)
print(b)
"""

IMPORT_CODE = """from math import pow as power, sqrt as root
from PIL.Image import open, new
import pandas, numpy, os
a = power(5, 2)
b = root(a)
c = pandas.DataFrame()
d = numpy.array([1,2,3])
new_img = new("RGB", (4,4))
new_img.save("test.png", "PNG")
e = open("test.png")
"""

# also tests for float
VARIABLE_ALIAS_CODE = """a = 1.2
b = a
"""

ALIAS_BY_REFERENCE = """a = [1,2,3]
b = a
a.append(4)
c = 2
r1 = c in a
r2 = c not in a
s = sum(b)
"""

ALIAS_BY_VALUE = """a = 0
b = a
a = 2
"""

MESSY_NODES = """import lineapy
a = 1
b = a + 2
c = 2
d = 4
e = d + a
f = a * b * c
10
e
g = e

lineapy.linea_publish(f, 'f')
"""


FUNCTION_DEFINITION_CODE = """def foo(a, b):
    return a - b
c = foo(b=1, a=2)
d = foo(5,1)
"""

CONDITIONALS_CODE = """bs = [1,2]
if len(bs) > 4:
    print("True")
else:
    bs.append(3)
    print("False")
"""

FUNCTION_DEFINITION_GLOBAL_CODE = """import math
import lineapy
a = 0
def my_function():
    global a
    a = math.factorial(5)
my_function()
lineapy.linea_publish(a, 'mutated a')
"""

LOOP_CODE = """import lineapy
a = []
b = 0
for x in range(9):
    a.append(x)
    b+=x
x = sum(a)
y = x + b
lineapy.linea_publish(y, 'y')
"""

SIMPLE_SLICE = """import lineapy
a = 2
b = 2
c = min(b,5)
b
lineapy.linea_publish(c, 'c')
"""

SUBSCRIPT = """
ls = [1,2,3,4]
ls[0] = 1
a = 4
ls[1] = a
ls[2:3] = [30]
ls[3:a] = [40]
"""

NESTED_CALL = "a = min(abs(11), 10)"

BINOPS = """a = 11
b = 2

r1 = a + b
r2 = a - b
r3 =a * b
r4 =a / b
r5 =a // b
r6 =a % b
r7 =a ** b
r8 =a << b
r9 =a >> b
r10 =a | b
r11 =a ^ b
r12 =a & b
"""

LOGICAL_BINOPS = """a = 1
b = 2
r1 = a == b
r2 = a != b
r3 = a < b
r4 = a <= b
r5 = a > b
r6 = a >= b
"""


class TestEndToEnd:
    """
    This Cli test serves as one end to end test and covers the
      following components:
    - LineaCli
    - transformer
    - tracer
    - LineaDB
    """

    def setup(self):
        """
        Reference https://github.com/pallets/flask/blob/
        afc13b9390ae2e40f4731e815b49edc9ef52ed4b/tests/test_cli.py

        TODO
        - More testing of error cases and error messages
        """
        self.runner = CliRunner()
        # FIXME: test harness cli, extract out magic string
        # FIXME: add methods instead of accessing session
        config = get_default_config_by_environment(ExecutionMode.DEV)
        # also reset the file
        reset_test_db(config.database_uri)
        self.db = RelationalLineaDB(config)

    def test_function_definition_without_side_effect(self, execute):
        res = execute(FUNCTION_DEFINITION_CODE)
        assert res.values["c"] == 1
        assert res.values["d"] == 4

    @pytest.mark.xfail(reason="exec scope is weird")
    def test_function_definition_global(self, execute):
        res = execute(FUNCTION_DEFINITION_GLOBAL_CODE)
        assert res.values["a"] == 120

    @pytest.mark.xfail
    def test_function_definition_global_slice(self, execute, python_snapshot):
        """
        Verify code is the same
        """
        res = execute(
            FUNCTION_DEFINITION_GLOBAL_CODE,
            compare_snapshot=False,
        )
        assert res.slice("a") == python_snapshot

    def test_loop_code(self, execute):
        res = execute(LOOP_CODE)

        assert len(res.values["a"]) == 9
        assert res.values["x"] == 36
        assert res.values["b"] == 36
        assert res.values["y"] == 72

    def test_loop_code_slice(self, execute, python_snapshot):
        res = execute(
            LOOP_CODE,
            compare_snapshot=False,
        )

        assert res.slice("y") == python_snapshot

    def test_loop_code_export_slice(self, execute, python_snapshot):
        res = execute(LOOP_CODE)

        assert res.sliced_func("y", "loop") == python_snapshot

    def test_conditionals(self, execute):
        res = execute(CONDITIONALS_CODE)
        assert res.stdout == "False\n"
        assert res.values["bs"] == [1, 2, 3]

    def test_pandas(self, execute):
        res = execute(PANDAS_RANDOM_CODE)
        assert res.values["new_df"].size == 2

    def test_string_format(self, execute):
        res = execute(STRING_FORMAT)
        assert res.values["a"] == "{ foo }"

    def test_end_to_end_simple_graph(self, execute):
        res = execute(PUBLISH_CODE)
        assert res.values["a"] == 11
        # TODO: testing publish artifact

    def test_variable_alias(self, execute):
        res = execute(VARIABLE_ALIAS_CODE)
        assert res.values["a"] == 1.2
        assert res.values["b"] == 1.2

    def test_chained_ops(self, execute):
        code = "b = 1 < 2 < 3\nassert b"
        execute(code)

    def test_import_name(self, execute):
        code = "import pandas as pd\nassert pd.__name__ == 'pandas'"
        execute(code)

    def test_fake_attribute(self, execute):
        code = "a = 1\nb=a.imag == 1"
        res = execute(code)
        assert res.values["b"] is False

    def test_publish(self, execute):
        """
        testing something super simple
        """
        res = execute(PUBLISH_CODE)

        artifact = res.db.get_artifact_by_name(publish_name)

        assert artifact.name == publish_name
        time_diff = (
            datetime.datetime.now() - artifact.date_created
        ).total_seconds()
        assert time_diff < 1

    def test_publish_via_cli(self):
        """
        same test as above but via the CLI
        """
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(PUBLISH_CODE))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            result = self.runner.invoke(
                linea_cli, ["--mode", "dev", tmp_file_name]
            )
            assert result.exit_code == 0
            return tmp_file_name

    def test_dictionary_support(self, execute):
        execute(DICTIONARY_SUPPORT)

    def test_graph_with_basic_image(self, execute):
        execute(IMAGE_CODE)

    def test_import(self, execute):
        res = execute(IMPORT_CODE)
        assert res.values["b"] == 5
        assert (res.values["d"] == [1, 2, 3]).all()
        assert res.values["c"].__class__ == pandas.core.frame.DataFrame
        assert res.values["e"].__class__ == PIL.PngImagePlugin.PngImageFile

    def test_no_script_error(self):
        # TODO
        # from lineapy.cli import cli

        # runner = CliRunner(mix_stderr=False)
        # result = runner.invoke(cli, ["missing"])
        # assert result.exit_code == 2
        # assert "Usage:" in result.stderr
        pass

    def test_compareops(self, execute):
        code = "b = 1 < 2 < 3\nassert b"
        execute(code)

    def test_binops(self, execute):
        res = execute(BINOPS)
        assert res.values["r1"] == 13
        assert res.values["r2"] == 9
        assert res.values["r3"] == 22
        assert res.values["r4"] == 5.5
        assert res.values["r5"] == 5
        assert res.values["r6"] == 1
        assert res.values["r7"] == 121
        assert res.values["r8"] == 44
        assert res.values["r9"] == 2
        assert res.values["r10"] == 11
        assert res.values["r11"] == 9
        assert res.values["r12"] == 2

    def test_logical_binops(self, execute):
        res = execute(LOGICAL_BINOPS)
        assert res.values["r1"] is False
        assert res.values["r2"] is True
        assert res.values["r3"] is True
        assert res.values["r4"] is True
        assert res.values["r5"] is False
        assert res.values["r6"] is False

    def test_subscript(self, execute):
        res = execute(SUBSCRIPT)
        assert len(res.values["ls"]) == 4
        assert res.values["ls"][0] == 1
        assert res.values["ls"][1] == 4
        assert res.values["ls"][2] == 30
        assert res.values["ls"][3] == 40

    def test_simple(self, execute):
        assert execute("a = abs(11)").values["a"] == 11

    def test_print(self, execute):
        assert execute(PRINT_CODE).stdout == "10\n"

    def test_chained_attributes(self, execute):
        """
        https://github.com/LineaLabs/lineapy/issues/161
        """
        import altair

        assert altair.data_transformers.active != "json"
        execute("import altair; altair.data_transformers.enable('json')")
        assert altair.data_transformers.active == "json"

    @pytest.mark.xfail(reason="get_ipython not defined in tests")
    def test_lookup_undefined_global_call(self, execute):
        """
        Even though get_ipython isn't defined when executing normally,
        we can still create a graph for it if we don't try to execute it
        outside of ipython.
        """
        execute("get_ipython().system('')")

    def test_subscript_call(self, execute):
        execute("[0][abs(0)]")

    def test_alias_by_reference(self, execute):
        res = execute(ALIAS_BY_REFERENCE)
        assert res.values["s"] == 10
        assert res.values["r1"] is True
        assert res.values["r2"] is False

    def test_alias_by_value(self, execute):
        res = execute(ALIAS_BY_VALUE)
        print(res.graph)
        assert res.values["a"] == 2
        assert res.values["b"] == 0

    def test_csv_import(self, execute):
        res = execute(CSV_CODE)
        assert res.values["s"] == 25

    def test_messy_nodes(self, execute, python_snapshot):
        res = execute(MESSY_NODES)
        assert res.values["g"] == 5
        assert res.slice("f") == python_snapshot

    def test_messy_nodes_slice(self, execute, python_snapshot):
        res = execute(MESSY_NODES, compare_snapshot=False)
        assert res.slice("f") == python_snapshot

    def test_simple_slice(self, execute, python_snapshot):
        res = execute(
            SIMPLE_SLICE,
            compare_snapshot=False,
        )

        assert res.slice("c") == python_snapshot

    def test_nested_call_graph(self, execute):
        res = execute(NESTED_CALL)
        assert res.values["a"] == 10

    def test_assignment_destructuring(self, execute):
        res = execute("a, b = (1, 2)")
        assert res.values["a"] == 1
        assert res.values["b"] == 2

    def test_housing(self, execute, python_snapshot):
        tests_dir = Path(__file__).parent

        # Change directory to tests dir before executing
        os.chdir(tests_dir)

        code = (tests_dir / "housing.py").read_text()
        res = execute(code)
        assert res.slice("p value") == python_snapshot


class TestUnaryOp:
    def test_sub(self, execute):
        res = execute("x = 1\ny=-x")
        assert res.values["y"] == -1

    def test_add(self, execute):
        """
        Weird test case from https://stackoverflow.com/a/16819334/907060
        """
        execute(
            """from decimal import Decimal
obj = Decimal('3.1415926535897932384626433832795028841971')
assert +obj != obj"""
        )

    def test_invert(self, execute):
        """
        https://stackoverflow.com/q/7278779/907060
        """
        res = execute("a = 1\nb=~a")
        assert res.values["b"] == -2

    def test_not(self, execute):
        res = execute("a = 1\nb=not a")
        assert res.values["b"] is False


class TestDelete:
    """
    Test the three parts of #95, to cover the Delete AST node

    https://docs.python.org/3/library/ast.html#ast.Delete
    """

    @pytest.mark.xfail(reason="dont support deleting a variable")
    def test_del_var(self, execute):

        res = execute("a = 1; del a")
        assert "a" not in res.values

    def test_del_subscript(self, execute):
        """
        Part of #95
        """
        res = execute("a = [1]; del a[0]")
        assert res.values["a"] == []

    def test_set_attr(self, execute):
        res = execute("import types; x = types.SimpleNamespace(); x.hi = 1")
        assert res.values["x"].hi == 1

    def test_del_attribute(self, execute):
        """
        Part of #95
        """
        res = execute(
            "import types; x = types.SimpleNamespace(); x.hi = 1; del x.hi",
        )
        x = res.values["x"]
        assert not hasattr(x, "hi")


class TestListComprehension:
    def test_returns_value(self, execute):
        res = execute("x = [i + 1 for i in range(3)]")
        assert res.values["x"] == [1, 2, 3]

    def test_depends_on_prev_value(self, execute):
        res = execute(
            "y = range(3)\nx = [i + 1 for i in y]",
            compare_snapshot=False,
            artifacts=["x"],
        )
        # Verify that i isn't set in the local scope
        assert res.values["x"] == [1, 2, 3]
        assert res.values["y"] == range(3)
        assert "i" not in res.values
        sliced_code = res.slice("x")
        assert execute(sliced_code).values["x"] == [1, 2, 3]


class TestSlicing:
    def test_empty_slice(self, execute):
        res = execute("x = [1, 2, 3][:]")
        assert res.values["x"] == [1, 2, 3]

    def test_slice_with_step(self, execute):
        res = execute("x = [1, 2, 3][::2]")
        assert res.values["x"] == [1, 3]

    def test_slice_with_step_and_start(self, execute):
        res = execute("x = [1, 2, 3][0::2]")
        assert res.values["x"] == [1, 3]

    def test_slice_with_step_and_stop(self, execute):
        res = execute("x = [1, 2, 3][:2:2]")
        assert res.values["x"] == [1]

    def test_slice_with_step_and_start_and_stop(self, execute):
        res = execute("x = [1, 2, 3][1:2:2]")
        assert res.values["x"] == [2]

    def test_slice_with_start(self, execute):
        res = execute("x = [1, 2, 3][1:]")
        assert res.values["x"] == [2, 3]


class TestDictionary:
    def test_basic_dict(self, execute):
        res = execute("x = {'a': 1, 'b': 2}")
        assert res.values["x"] == {"a": 1, "b": 2}

    def test_splatting(self, execute):
        res = execute("x = {1: 2, 2:2, **{1: 3, 2: 3}, 1: 4}")
        assert res.values["x"] == {1: 4, 2: 3}


class TestFunctionMutations:
    def test_mutation(self, execute):
        """
        Verify that mutating an item wil cause a dependency on the mutation.
        """
        source = "x = {}\nx['a'] = 3\n"
        res = execute(source, artifacts=["x"])
        assert res.artifacts["x"] == source

    def test_mutation_of_view(self, execute):
        """
        Verify that mutating a view will update the original.
        """
        source = """x = {}
y = {}
x['y'] = y
y['a'] = 1
"""
        res = execute(source, artifacts=["x"])
        assert res.artifacts["x"] == source
        # assert res.artifacts["y"] == "y = {}\ny['a'] = 1\n"

    def test_before_after_mutation(self, execute):
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
            "x": "x = {}\nx['a'] = 1\n",
            "before": "x = {}\nbefore = str(x)\n",
            "after": "x = {}\nx['a'] = 1\nafter = str(x)\n",
        }

    def test_view_of_view(self, execute):
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

        assert res.artifacts == {
            "x": source,
            "y": "y = {}\nz = {}\ny['z'] = z\nz['a'] = 1\n",
            "z": "z = {}\nz['a'] = 1\n",
        }

    def test_delitem(self, execute):
        """
        Verify that mutating a view of a view will update the original.
        """
        source = """x = {1: 1}
del x[1]
"""
        res = execute(source, artifacts=["x"])

        assert res.artifacts["x"] == source

    def test_self_return_loop(self, execute):
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
        assert res.artifacts["new_clf"] == code
        assert res.artifacts["clf"] == code
