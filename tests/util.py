import os.path as path
from ast import AST, dump
from os import remove
from re import sub
from tempfile import NamedTemporaryFile

from lineapy.constants import ExecutionMode
from lineapy.data.types import SessionType
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB


def reset_test_db(sqlite_uri: str):
    """ """
    try:
        r = sqlite_uri.split("///")
        remove(r[1])
        return True
    except Exception:
        return False


def compare_ast(node1: AST, node2: AST):
    """
    Compare two AST trees, ignoring offset information.
    """
    s1 = dump(node1)
    s2 = dump(node2)
    if s1 != s2:
        print(dump(node1, indent=2))
        print(dump(node2, indent=2))
    return s1 == s2


def compare_code_via_ast(code: str, expected: str) -> bool:
    import ast

    return compare_ast(ast.parse(code), ast.parse(expected))


CSV_CODE = """import pandas as pd
import lineapy

df = pd.read_csv('tests/simple_data.csv')
s = df['a'].sum()

lineapy.linea_publish(s, "Graph With CSV Import")
"""

IMAGE_CODE = """import lineapy
import pandas as pd
import matplotlib.pyplot as plt
from PIL.Image import open

df = pd.read_csv('tests/simple_data.csv')
plt.imsave('simple_data.png', df)

img = open('simple_data.png')
img = img.resize([200, 200])

lineapy.linea_publish(img, "Graph With Image")
"""


def get_project_directory():
    return path.abspath(path.join(__file__, "../.."))
