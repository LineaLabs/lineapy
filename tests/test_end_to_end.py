from lineapy.execution.executor import Executor
from lineapy.graph_reader.graph_util import are_nodes_content_equal
from tempfile import NamedTemporaryFile
from click.testing import CliRunner
import pytest
from os import chdir, getcwd

import lineapy
from lineapy.cli.cli import linea_cli
from lineapy.data.types import NodeType, SessionType
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import get_current_time, info_log

from tests.util import (
    get_project_directory,
    reset_test_db,
)
from tests.stub_data.graph_with_simple_function_definition import (
    definition_node,
    assignment_node,
    code as function_definition_code,
)

from tests.stub_data.graph_with_basic_image import (
    code as graph_with_basic_image_code,
)

publish_name = "testing artifact publish"
PUBLISH_CODE = (
    f"import {lineapy.__name__}\na ="
    f" abs(-11)\n{lineapy.__name__}.{lineapy.linea_publish.__name__}(a,"
    f" '{publish_name}')\n"
)


PRINT_CODE = """a = abs(-11)
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

    @pytest.mark.parametrize(
        "session_type",
        [
            SessionType.SCRIPT,
            SessionType.STATIC,
        ],
    )
    def test_end_to_end_simple_graph(self, session_type, execute):
        res = execute(PUBLISH_CODE, session_type=session_type)

        nodes = res.graph.nodes
        assert len(nodes) == 3

    def test_variable_alias(self, execute):
        res = execute(VARIABLE_ALIAS_CODE)
        assert res.values["a"] == 1
        assert res.values["b"] == 1

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
        self, session_type: SessionType
    ):
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(function_definition_code))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            # FIXME: make into constants
            result = self.runner.invoke(
                linea_cli,
                [
                    "--mode",
                    "dev",
                    "--session",
                    session_type.name,
                    tmp_file_name,
                ],
            )
            assert result.exit_code == 0
            nodes = self.db.get_nodes_by_file_name(tmp_file_name)
            assert len(nodes) == 4
            for c in nodes:
                if c.node_type == NodeType.FunctionDefinitionNode:
                    assert are_nodes_content_equal(
                        c,
                        definition_node,
                        function_definition_code,
                    )
                if c.node_type == NodeType.CallNode:
                    assert are_nodes_content_equal(
                        c,
                        assignment_node,
                        function_definition_code,
                    )

    def test_graph_with_basic_image(self, execute, tmpdir):
        """
        Changes the directory of the execution to make sure things are working.

        NOTE:
        - We cannot assert on the nodes being equal to what's generated yet
          because DataSourceSode is not yet implemented.
        """
        cwd = getcwd()

        # Try running at first from the root directory of the project, so the
        # read csv can find the right file
        chdir(get_project_directory())
        res = execute(graph_with_basic_image_code)

        # Then try in a random directory, to make sure its preserved when executing
        chdir(tmpdir.mkdir("tmp"))
        e = Executor()
        e.execute_program(res.graph)
        # TODO: add some assertion, but for now it's sufficient that it's
        #       working

        chdir(cwd)  # reset

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
        assert execute("a = abs(-11)").values["a"] == 11

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
