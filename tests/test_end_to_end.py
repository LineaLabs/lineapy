from tempfile import NamedTemporaryFile
from click.testing import CliRunner
import pytest
from os import chdir, getcwd

import lineapy
from lineapy.execution.executor import Executor
from lineapy.cli.cli import linea_cli
from lineapy.data.types import SessionType
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import get_current_time, info_log

from tests.util import (
    IMAGE_CODE,
    CSV_CODE,
    reset_test_db,
)

publish_name = "testing artifact publish"
PUBLISH_CODE = f"""import {lineapy.__name__}
a = abs(11)
{lineapy.__name__}.{lineapy.linea_publish.__name__}(a, '{publish_name}')
"""


STRING_FORMAT = """a = '{{ {0} }}'.format('foo')"""


PANDAS_RANDOM_CODE = """from pandas import DataFrame
df = DataFrame([[1,2], [3,4]])
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
a = power(5, 2)
b = root(a)
"""

VARIABLE_ALIAS_CODE = """a = 1
b = a
"""

ALIAS_BY_REFERENCE = """a = [1,2,3]
b = a
a.append(4)
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
res = my_function()
lineapy.linea_publish(res, 'res')
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


NESTED_CALL = "a = min(abs(11), 10)"


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
        self.db = RelationalLineaDB()
        self.db.init_db(config)

    def test_pandas(self, execute):
        res = execute(PANDAS_RANDOM_CODE)
        assert res.values["new_df"].size == 2

    def test_string_format(self, execute):
        res = execute(STRING_FORMAT)
        assert res.values["a"] == "{ foo }"

    @pytest.mark.parametrize(
        "session_type",
        [
            SessionType.SCRIPT,
            SessionType.STATIC,
        ],
    )
    def test_end_to_end_simple_graph(self, session_type, execute):
        res = execute(PUBLISH_CODE, session_type=session_type)
        if session_type == SessionType.SCRIPT:
            assert res.values["a"] == 11
        # TODO: testing publish artifact

    def test_variable_alias(self, execute):
        res = execute(VARIABLE_ALIAS_CODE)
        assert res.values["a"] == 1
        assert res.values["b"] == 1

    def test_chained_ops(self, execute):
        code = "b = 1 < 2 < 3\nassert b"
        execute(code)

    def test_import_name(self, execute):
        code = "import pandas as pd\nassert pd.__name__ == 'pandas'"
        execute(code)

    def test_fake_attribute(self, execute):
        code = "a = 1\nb=a.imag == 1"
        res = execute(code)
        assert res.values["b"] == False

    def test_publish(self, execute):
        """
        testing something super simple
        """
        res = execute(PUBLISH_CODE)

        artifacts = res.artifacts

        assert len(artifacts) == 1
        artifact = artifacts[0]

        info_log("logged artifact", artifact)
        assert artifact.name == publish_name
        time_diff = get_current_time() - artifact.date_created
        assert time_diff < 1000

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

    @pytest.mark.parametrize(
        "session_type",
        [
            SessionType.SCRIPT,
            SessionType.STATIC,
        ],
    )
    def test_function_definition_without_side_effect(
        self, session_type: SessionType, execute
    ):
        res = execute(FUNCTION_DEFINITION_CODE, session_type=session_type)
        if session_type == SessionType.SCRIPT:
            assert res.values["c"] == 1

    @pytest.mark.xfail(reason="Mutations ##221")
    def test_dictionary_support(self, execute):
        res = execute(DICTIONARY_SUPPORT)

    def test_graph_with_basic_image(self, execute, tmpdir):
        """
        Changes the directory of the execution to make sure things are working.

            NOTE:
        - We cannot assert on the nodes being equal to what's generated yet
          because DataSourceSode is not yet implemented.
        """

        res = execute(IMAGE_CODE)

        # TODO: Verify artifact was added as well

        # Then try in a random directory, to make sure its preserved when executing
        chdir(tmpdir.mkdir("tmp"))
        e = Executor()
        e.execute_program(res.graph)

        # TODO: add some assertion, but for now it's sufficient that it's
        #       working

    def test_import(self, execute):
        res = execute(IMPORT_CODE)
        assert res.values["b"] == 5

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
        code = "b = 1 + 2\nassert b == 3"
        execute(code)

    def test_subscript(self, execute):
        code = "ls = [1,2]\nassert ls[0] == 1"
        execute(code)

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
        res = execute("import altair; altair.data_transformers.enable('json')")
        assert altair.data_transformers.active == "json"

    def test_lookup_undefined_global_call(self, execute):
        """
        Even though get_ipython isn't defined when executing normally,
        we can still create a graph for it if we don't try to execute it
        outside of ipython.
        """
        execute("get_ipython().system('')", session_type=SessionType.STATIC)

    def test_subscript_call(self, execute):
        execute("[0][abs(0)]", session_type=SessionType.STATIC)

    # @pytest.mark.xfail(reason="Mutations #197")
    def test_alias_by_reference(self, execute):
        res = execute(ALIAS_BY_REFERENCE)
        print(res)
        assert res.values["s"] == 10

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

    @pytest.mark.xfail
    def test_conditionals(self, execute):
        res = execute(CONDITIONALS_CODE)
        assert res.stdout == "False\n"
        assert res.values["bs"] == [1, 2, 3]

    @pytest.mark.xfail
    def test_function_definition_global(self, execute):
        res = execute(FUNCTION_DEFINITION_GLOBAL_CODE)
        assert res.values["a"] == 120

    @pytest.mark.xfail
    def test_function_definition_global_slice(self, execute):
        """
        Verify code is the same
        """
        res = execute(
            FUNCTION_DEFINITION_GLOBAL_CODE,
            compare_snapshot=False,
        )
        assert res.slice("res") == FUNCTION_DEFINITION_GLOBAL_CODE

    @pytest.mark.xfail
    def test_loop_code(self, execute):
        res = execute(LOOP_CODE)

        assert len(res.values["a"]) == 9
        assert res.values["y"] == 72
        assert res.values["x"] == 36

    @pytest.mark.xfail
    def test_loop_code_slice(self, execute):
        res = execute(
            LOOP_CODE,
            compare_snapshot=False,
        )

        assert res.slice("y") == LOOP_CODE

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


class TestUnaryOp:
    def test_sub(self, execute):
        res = execute("x = 1\ny=-x")
        assert res.values["y"] == -1

    def test_add(self, execute):
        """
        Weird test case from https://stackoverflow.com/a/16819334/907060
        """
        res = execute(
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
            "import lineapy\ny = range(3)\nx = [i + 1 for i in"
            " y]\nlineapy.linea_publish(x, 'x')",
            compare_snapshot=False,
        )
        # Verify that i isn't set in the local scope
        assert res.values == {"x": [1, 2, 3], "y": range(3)}
        assert execute(res.slice("x")).values["x"] == [1, 2, 3]


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
