import logging
import os
from tempfile import NamedTemporaryFile

from lineapy import SessionType, ExecutionMode
from lineapy.constants import SQLALCHEMY_ECHO
from lineapy.transformer.transformer import Transformer
import lineapy

logging.basicConfig()


class TestTransformedCodeExecution:
    @staticmethod
    def _run_program(code):
        logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
        execution_mode = ExecutionMode.MEMORY
        os.environ[SQLALCHEMY_ECHO] = "False"
        transformer = Transformer()
        with NamedTemporaryFile() as tmp:
            tmp.write(str.encode(code))
            tmp.flush()
            new_code = transformer.transform(
                code,
                session_type=SessionType.SCRIPT,
                session_name=tmp.name,
                execution_mode=execution_mode,
            )
            exec(new_code)

    def test_chained_ops(self):
        code = "b = 1 < 2 < 3\nassert b"
        self._run_program(code)

    def test_binop(self):
        code = "b = 1 + 2\nassert b == 3"
        self._run_program(code)

    def test_import(self):
        code = "import pandas as pd\nassert pd.__name__ == 'pandas'"
        self._run_program(code)

    def test_import_methods(self):
        code = (
            "import pandas as pd\n"
            "df = pd.DataFrame([1,2])\n"
            "assert df.size == 2"
        )
        self._run_program(code)

    # def test_tmp(self):
    #     code = "import pandas as pd;df = pd.read_csv('simple_data.csv');s = df['a'].sum()"
    #     self._run_program(code)

    def test_attribute(self):
        code = "a = 1\na.imag == 1"
        self._run_program(code)

    def test_linea_publish(self):
        name = "testing artifact publish"
        publish_code = (
            f"import {lineapy.__name__}\na ="
            f" abs(-11)\n{lineapy.__name__}.{lineapy.linea_publish.__name__}(a,"
            f" '{name}')\n"
        )
        print(publish_code)
        self._run_program(publish_code)
