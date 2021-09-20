from tempfile import NamedTemporaryFile
from click.testing import CliRunner

import lineapy
from lineapy.cli.cli import linea_cli
from lineapy.data.types import SessionType
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.transformer.transformer import ExecutionMode
from lineapy.utils import get_current_time, info_log

from tests.util import reset_test_db, run_code
from tests.test_end_to_end.end_to_end_shared import (
    simple_function_def,
    simple_graph,
)


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

    def test_end_to_end_simple_graph(self):
        simple_graph(SessionType.SCRIPT, self.db)

    def test_publish(self):
        """
        testing something super simple
        """
        _ = run_code(publish_code, publish_name)
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
        simple_function_def(SessionType.SCRIPT, self.db, self.runner)
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
        run_code(code, "chained ops")

    def test_binops(self):
        code = "b = 1 + 2\nassert b == 3"
        run_code(code, "binop")

    def test_subscript(self):
        code = "ls = [1,2]\nassert ls[0] == 1"
        run_code(code, "subscript")
