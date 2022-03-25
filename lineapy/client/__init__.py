from logging import Logger

from lineapy.db.db import RelationalLineaDB
from lineapy.instrumentation.tracer import Tracer


class LineaClient(object):
    _db: RelationalLineaDB
    _tracer: Tracer
    _logger: Logger

    def __init__(self) -> None:
        self._db = RelationalLineaDB.from_environment()
        pass

    def transform(self):
        pass

    def run(self):
        pass
