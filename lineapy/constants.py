from enum import Enum

PROD_ENV = "production"
PROD_DEBUG = False
PROD_TESTING = False
PROD_DATABASE_URI = "sqlite:///local.db"

# persistent tests
DEV_ENV = "development"
DEV_DEBUG = True
DEV_TESTING = False
DEV_DATABASE_URI = "sqlite:///local.db"

# in memory tests
TEST_ENV = "development"
TEST_DEBUG = True
TEST_TESTING = True
TEST_DATABASE_URI = "sqlite:///:memory:"

LINEAPY_TRACER_CLASS = "Tracer"
LINEAPY_TRACER_NAME = "lineapy_tracer"
LINEAPY_IMPORT_LIB_NAME = "lineapy"
LINEAPY_SESSION_TYPE = "SessionType"
LINEAPY_SESSION_TYPE_JUPYTER = "JUPYTER"
LINEAPY_SESSION_TYPE_SCRIPT = "SCRIPT"
LINEAPY_EXECUTION_MODE = "ExecutionMode"

# no addressable file location
DB_DATA_ASSET_MANAGER = "virtual"


class ExecutionMode(Enum):
    """
    This is not a constant because this is for runtime configuration
    """

    TEST = 0
    DEV = 1
    PROD = 2
