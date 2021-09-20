from click.testing import CliRunner

from lineapy.data.types import SessionType
from lineapy.db.relational.db import RelationalLineaDB
from tests.util import reset_test_db
from lineapy.constants import ExecutionMode
from lineapy.db.base import get_default_config_by_environment
from tests.test_end_to_end.end_to_end_shared import (
    simple_graph,
    simple_function_def,
)


class TestStaticEndToEnd:
    def setup(self):
        self.runner = CliRunner()
        config = get_default_config_by_environment(ExecutionMode.DEV)
        # also reset the file
        reset_test_db(config.database_uri)
        self.db = RelationalLineaDB()
        self.db.init_db(config)

    def test_simple(self):
        simple_graph(SessionType.STATIC, self.db)

    def test_simple_func_def(self):
        simple_function_def(SessionType.STATIC, self.db, self.runner)
