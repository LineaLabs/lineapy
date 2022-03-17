import os.path as path
import sys
from ast import AST, dump
from dataclasses import dataclass
from os import remove

from lineapy import save


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
        # assuming here that the python version is atleast > 3
        if sys.version_info <= (3, 8):
            print(dump(node1))
            print(dump(node2))
        else:
            print(dump(node1, indent=2))
            print(dump(node2, indent=2))
    return s1 == s2


def compare_code_via_ast(code: str, expected: str) -> bool:
    import ast

    return compare_ast(ast.parse(code), ast.parse(expected))


CSV_CODE = f"""import pandas as pd
import lineapy

df = pd.read_csv('tests/simple_data.csv')
s = df['a'].sum()

lineapy.{save.__name__}(s, "Graph With CSV Import")
"""

IMAGE_CODE = f"""import lineapy
import pandas as pd
import matplotlib.pyplot as plt
from PIL.Image import open

df = pd.read_csv('tests/simple_data.csv')
plt.imsave('simple_data.png', df)

img = open('simple_data.png')
img = img.resize([200, 200])

lineapy.{save.__name__}(img, "Graph With Image")
"""


def get_project_directory():
    return path.abspath(path.join(__file__, "../.."))


@dataclass
class IsType:
    """
    Used in the tests so we can make sure a value has the same type as another, even if it is not equal.
    """

    tp: type

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.tp)
