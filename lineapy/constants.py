import os.path as path
import sys
from enum import Enum

lineapy_module = sys.modules[__name__]
_base = path.split(path.abspath(path.dirname(lineapy_module.__file__)))[0]

PROD_ENV = "production"
PROD_DEBUG = False
PROD_TESTING = False
PROD_DATABASE_URI = f"sqlite:///{path.join(_base, 'prod.sqlite')}"

# persistent tests
DEV_ENV = "development"
DEV_DEBUG = True
DEV_TESTING = False
DEV_DATABASE_URI = f"sqlite:///{path.join(_base, 'dev.sqlite')}"

TEST_ENV = "test"
TEST_DEBUG = True
TEST_TESTING = True
TEST_DATABASE_URI = f"sqlite:///{path.join(_base, 'test.sqlite')}"

MEMORY_DATABASE_URI = "sqlite:///:memory:"

SQLALCHEMY_ECHO = "SQLALCHEMY_ECHO"

LINEAPY_TRACER_CLASS = "Tracer"
LINEAPY_TRACER_NAME = "lineapy_tracer"
LINEAPY_IMPORT_LIB_NAME = "lineapy"
LINEAPY_SESSION_TYPE = "SessionType"
LINEAPY_SESSION_TYPE_JUPYTER = "JUPYTER"
LINEAPY_SESSION_TYPE_SCRIPT = "SCRIPT"
LINEAPY_EXECUTION_MODE = "ExecutionMode"

# no addressable file location
DB_DATA_ASSET_MANAGER = "virtual"

# HTTP constants
BACKEND_REQUEST_HOST = "http://localhost:4000"

LATEST_NODE_VERSION = "LATEST"


class ExecutionMode(Enum):
    """
    This is not a constant because this is for runtime configuration
    """

    TEST = 0
    DEV = 1
    PROD = 2
    MEMORY = 3
