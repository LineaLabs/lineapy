from tempfile import NamedTemporaryFile

from click.testing import CliRunner

from lineapy.cli.cli import linea_cli
from lineapy.data.types import NodeType
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.graph_reader.graph_util import are_nodes_content_equal
from lineapy.instrumentation.instrumentation_util import (
    get_linea_db_config_from_execution_mode,
)
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import info_log
from tests.stub_data.simple_graph import simple_graph_code, line_1, arg_literal


class CliTest:
    """
    This Cli test serves as one end to end test and covers the following components:
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
        config = get_linea_db_config_from_execution_mode(ExecutionMode.TEST)
        self.db = RelationalLineaDB()
        self.db.init_db(config)

    def test_end_to_end_simple_graph(self):
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(simple_graph_code))
            # might also need os.path.dirname() in addition to file name
            tmp_file_name = tmp.name
            result = self.runner.invoke(linea_cli, [tmp_file_name])
            assert result.exit_code == 0
            nodes = self.db.get_nodes_by_file_name(tmp_file_name)
            # there should just be two
            assert len(nodes) == 2
            for c in nodes:
                if c.node_type == NodeType.CallNode:
                    assert are_nodes_content_equal(c, line_1)
                if c.node_type == NodeType.ArgumentNode:
                    assert are_nodes_content_equal(c, arg_literal)
                info_log("found_call_node", c)

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
        When linea is running, there should be a database server that is active and receiving the scripts
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
    tester = CliTest()
    tester.setup()
    tester.test_end_to_end_simple_graph()
