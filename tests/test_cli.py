from lineapy.data.types import NodeType
from tempfile import NamedTemporaryFile
from click.testing import CliRunner

import lineapy
from lineapy.cli.cli import linea_cli
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import get_current_time, info_log
from lineapy.graph_reader.graph_util import are_nodes_content_equal
from tests.stub_data.simple_graph import simple_graph_code, line_1, arg_literal
from tests.util import reset_test_db


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
        Reference https://github.com/pallets/flask/blob/afc13b9390ae2e40f4731e815b49edc9ef52ed4b/tests/test_cli.py

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

    def test_end_to_end_simple_graph(self):
        with NamedTemporaryFile() as tmp:
            info_log("simple graph code", simple_graph_code)
            tmp.write(str.encode(simple_graph_code))
            tmp.flush()
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            # FIXME: make into constants
            result = self.runner.invoke(linea_cli, ["--mode", "dev", tmp_file_name])
            assert result.exit_code == 0
            info_log("testing file:", tmp_file_name)
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
        name = "testing artifact publish"
        with NamedTemporaryFile() as tmp:
            publish_code = (
                f"import {lineapy.__name__}\na ="
                f" abs(-11)\n{lineapy.__name__}.{lineapy.linea_publish.__name__}(a,"
                f" '{name}')\n"
            )
            info_log("publish code", publish_code)
            tmp.write(str.encode(publish_code))
            tmp.flush()
            result = self.runner.invoke(linea_cli, ["--mode", "dev", tmp.name])
            assert result.exit_code == 0
            artifacts = self.db.get_all_artifacts()
            assert len(artifacts) == 1
            artifact = artifacts[0]
            info_log("logged artifact", artifact)
            assert artifact.name == name
            time_diff = get_current_time() - artifact.date_created
            assert time_diff < 1000

    def test_no_script_error(self):
        # TODO
        # from lineapy.cli import cli

        # runner = CliRunner(mix_stderr=False)
        # result = runner.invoke(cli, ["missing"])
        # assert result.exit_code == 2
        # assert "Usage:" in result.stderr
        pass

    def test_no_server_error(self):
        """
        When linea is running, there should be a database server that is
          active and receiving the scripts
        TODO
        """
        # from lineapy.cli import cli

        # runner = CliRunner(mix_stderr=False)
        # result = runner.invoke(cli, ["missing"])
        # assert result.exit_code == 2
        # assert "FLASK_APP" in result.stderr
        # assert "Usage:" in result.stderr
        pass


if __name__ == "__main__":
    tester = TestCli()
    tester.setup()
    tester.test_end_to_end_simple_graph()
