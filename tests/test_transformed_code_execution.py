import logging
import os
from tempfile import NamedTemporaryFile

from lineapy import SessionType, ExecutionMode
from lineapy.constants import SQLALCHEMY_ECHO
from lineapy.transformer.transformer import Transformer

logging.basicConfig()


class TestTransformedCodeExecution:
    def test_chained_ops(self):
        logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
        code = "b = 1 < 2 < 3"
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
