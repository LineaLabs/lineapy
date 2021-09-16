import operator
import os.path as path
import sys
from ast import Name, Load
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


# Transformer related
GET_ITEM = operator.__getitem__.__name__
SET_ITEM = operator.__setitem__.__name__
BUILTIN_OPERATOR = operator.__name__
OPERATOR_MODULE = Name(id=BUILTIN_OPERATOR, ctx=Load())

# BinOPs
ADD = operator.__add__.__name__
SUB = operator.__sub__.__name__
MULT = operator.__mul__.__name__
DIV = operator.__truediv__.__name__
FLOORDIV = operator.__floordiv__.__name__
MOD = operator.__mod__.__name__
POW = operator.__pow__.__name__
LSHIFT = operator.__lshift__.__name__
RSHIFT = operator.__rshift__.__name__
BITOR = operator.__or__.__name__
BITXOR = operator.__xor__.__name__
BITAND = operator.__and__.__name__
MATMUL = operator.__matmul__.__name__
