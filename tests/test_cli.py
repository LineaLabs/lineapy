from click.testing import CliRunner
from tempfile import NamedTemporaryFile

from lineapy.instrumentation.instrumentation_util import (
    get_linea_db_config_from_execution_mode,
)
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import info_log
from lineapy.db.relational.schema.relational import CallNodeORM
from lineapy.db.base import LineaDBConfig
from lineapy.db.db import LineaDB
from lineapy.data.types import SessionType
from lineapy.graph_reader.graph_util import are_nodes_conetent_equal
from lineapy.cli.cli import linea_cli
from tests.stub_data.simple_graph import simple_graph_code


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
        self.db = LineaDB(config)

    def test_end_to_end(self):
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(simple_graph_code))
            # might also need os.path.dirname() in addition to file name
            result = self.runner.invoke(linea_cli, [tmp.name])
            assert result.exit_code == 0
            call_nodes = self.db.session.query(CallNodeORM).all()
            for c in call_nodes:
                processed_call_node = self.db.get_node_by_id(c.id)
                info_log("found_call_node", processed_call_node)

    def test_no_script_error(self):
        # TODO
        # from lineapy.cli import cli

        # runner = CliRunner(mix_stderr=False)
        # result = runner.invoke(cli, ["missing"])
        # assert result.exit_code == 2
        # assert "Usage:" in result.stderr
        pass

    def test_no_server_error():
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
    tester.test_end_to_end()
