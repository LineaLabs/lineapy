from tempfile import NamedTemporaryFile
from click.testing import CliRunner

import lineapy
from lineapy.cli.cli import linea_cli
from lineapy.data.types import NodeType, SessionType
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.graph_reader.graph_util import are_nodes_content_equal
from lineapy.transformer.transformer import ExecutionMode, Transformer
from lineapy.utils import get_current_time, info_log
from tests.stub_data.simple_graph import simple_graph_code, line_1, arg_literal

from tests.stub_data.graph_with_simple_function_definition import (
    definition_node,
    assignment_node,
    code as function_definition_code,
)
from tests.util import reset_test_db


publish_name = "testing artifact publish"
publish_code = (
    f"import {lineapy.__name__}\na ="
    f" abs(-11)\n{lineapy.__name__}.{lineapy.linea_publish.__name__}(a,"
    f" '{publish_name}')\n"
)


class TestCli:
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

    def _run_code(self, original_code: str, test_name: str) -> str:
        """
        Returns file name
        """
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(original_code))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            file_name = tmp.name
            transformer = Transformer()
            new_code = transformer.transform(
                original_code,
                session_type=SessionType.SCRIPT,
                session_name=file_name,
                execution_mode=ExecutionMode.DEV,
            )
            exec(new_code)
        return file_name

    def test_end_to_end_simple_graph(self):
        tmp_file_name = self._run_code(simple_graph_code, "simple graph code")
        nodes = self.db.get_nodes_by_file_name(tmp_file_name)
        # there should just be two
        info_log("nodes", len(nodes), nodes)
        assert len(nodes) == 2
        for c in nodes:
            if c.node_type == NodeType.CallNode:
                assert are_nodes_content_equal(
                    c, line_1, self.db.get_context(nodes[0].session_id).code
                )
            if c.node_type == NodeType.ArgumentNode:
                assert are_nodes_content_equal(
                    c,
                    arg_literal,
                    self.db.get_context(nodes[0].session_id).code,
                )
            info_log("found_call_node", c)

    def test_publish(self):
        """
        testing something super simple
        """
        _ = self._run_code(publish_code, publish_name)
        artifacts = self.db.get_all_artifacts()
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
            tmp.write(str.encode(publish_code))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            result = self.runner.invoke(linea_cli, ["--mode", "dev", tmp_file_name])
            assert result.exit_code == 0
            return tmp_file_name

    def test_function_definition_without_side_effect(self):
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(function_definition_code))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            # FIXME: make into constants
            result = self.runner.invoke(
                linea_cli,
                ["--mode", "dev", tmp_file_name],
            )
            assert result.exit_code == 0
            nodes = self.db.get_nodes_by_file_name(tmp_file_name)
            assert len(nodes) == 2
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
            return

    def test_no_script_error(self):
        # TODO
        # from lineapy.cli import cli

        # runner = CliRunner(mix_stderr=False)
        # result = runner.invoke(cli, ["missing"])
        # assert result.exit_code == 2
        # assert "Usage:" in result.stderr
        pass

    def test_compareops(self):
        code = "b = 1 < 2 < 3\nassert b"
        self._run_code(code, "chained ops")

    def test_binops(self):
        code = "b = 1 + 2\nassert b == 3"
        self._run_code(code, "binop")

    def test_subscript(self):
        code = "ls = [1,2]\nassert ls[0] == 1"
        self._run_code(code, "subscript")
