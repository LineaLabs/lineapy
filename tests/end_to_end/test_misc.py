import datetime

import pytest

from lineapy.api.api import save
from lineapy.exceptions.user_exception import UserException
from tests.util import CSV_CODE, IMAGE_CODE

publish_name = "testing artifact publish"
PUBLISH_CODE = f"""import lineapy
a = abs(11)
lineapy.{save.__name__}(a, '{publish_name}')
"""

alt_publish_name = "another_import_method"
PUBLISH_ALT_FORMAT_CODE = f"""from lineapy import {save.__name__}
a = 1
{save.__name__}(a, '{alt_publish_name}')
"""

STRING_FORMAT = """a = '{{ {0} }}'.format('foo')"""


PRINT_CODE = """a = abs(11)
b = min(a, 10)
print(b)
"""


MESSY_NODES = f"""import lineapy
a = 1
b = a + 2
c = 2
d = 4
e = d + a
f = a * b * c
10
e
g = e

lineapy.{save.__name__}(f, 'f')
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

    def test_publish_format(self, execute):
        res = execute(PUBLISH_ALT_FORMAT_CODE)
        artifact = res.db.get_artifactorm_by_name(alt_publish_name)
        assert artifact.name == alt_publish_name

    def test_string_format(self, execute):
        res = execute(STRING_FORMAT)
        assert res.values["a"] == "{ foo }"

    def test_end_to_end_simple_graph(self, execute):
        res = execute(PUBLISH_CODE)
        assert res.values["a"] == 11
        # TODO: testing publish artifact

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

        artifact = res.db.get_artifactorm_by_name(publish_name)

        assert artifact.name == publish_name
        time_diff = (
            datetime.datetime.now() - artifact.date_created
        ).total_seconds()
        assert time_diff < 1

    @pytest.mark.slow
    def test_graph_with_basic_image(self, execute):
        execute(IMAGE_CODE)

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

    def test_simple(self, execute):
        assert execute("a = abs(11)").values["a"] == 11

    def test_print(self, execute, capsys):

        execute(PRINT_CODE)
        captured = capsys.readouterr()
        # Shows up twice due to re-exeuction
        assert captured.out == "10\n10\n"

    def test_raise(self, execute, capsys):
        with pytest.raises(UserException):
            RAISE_CODE = "raise OSError()"
            execute(RAISE_CODE)

    def test_chained_attributes(self, execute):
        """
        https://github.com/LineaLabs/lineapy/issues/161
        """
        import altair

        altair.data_transformers.enable("default")
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

    def test_csv_import(self, execute):
        res = execute(CSV_CODE)
        assert res.values["s"] == 25

    def test_messy_nodes(self, execute, python_snapshot):
        res = execute(MESSY_NODES)
        assert res.values["g"] == 5
        assert res.slice("f") == python_snapshot

    def test_messy_nodes_slice(self, execute, python_snapshot):
        res = execute(MESSY_NODES, snapshot=False)
        assert res.slice("f") == python_snapshot

    def test_nested_call_graph(self, execute):
        res = execute(NESTED_CALL)
        assert res.values["a"] == 10

    @pytest.mark.slow
    def test_housing(self, housing_tracer, python_snapshot):
        assert housing_tracer.slice("p value") == python_snapshot
