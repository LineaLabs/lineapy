import os.path as path
from ast import AST, dump
from datetime import datetime
from os import remove
from typing import Optional, List
from re import sub
from tempfile import NamedTemporaryFile
from pydantic import BaseModel
from os import getcwd

from lineapy.transformer.transformer import ExecutionMode, Transformer
from lineapy.data.types import (
    SessionContext,
    SessionType,
)
from lineapy.db.base import get_default_config_by_environment
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.utils import get_new_id, internal_warning_log

TEST_ARTIFACT_NAME = "Graph With CSV Import"


def compare_pydantic_objects_without_keys(
    a: BaseModel,
    b: BaseModel,
    keys: List[str],
    log_diff=False,
):
    a_d = a.dict()
    b_d = b.dict()
    for k in keys:
        del a_d[k]
        del b_d[k]
    diff = a_d == b_d
    if log_diff:
        internal_warning_log(f"{a_d}\ndifferent from\n{b_d}")
    return diff


def strip_non_letter_num(s: str):
    return sub("[\\s+]", "", s)


def are_str_equal(
    s1: str,
    s2: str,
    remove_all_non_letter=False,
    find_diff=False,
):
    if remove_all_non_letter:
        return strip_non_letter_num(s1) == strip_non_letter_num(s2)
    if s1.strip() == s2.strip():
        return True
    if find_diff:
        splitS1 = set(s1.split("\n"))
        splitS2 = set(s2.split("\n"))

        diff = splitS2.difference(splitS1)
        diff = ", ".join(diff)
        print("Difference:", diff)
        return False




def reset_test_db(sqlite_uri: str):
    """ """
    try:
        r = sqlite_uri.split("///")
        remove(r[1])
        return True
    except:
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


def setup_db(mode: ExecutionMode, reset: bool) -> RelationalLineaDB:
    db_config = get_default_config_by_environment(mode)
    if reset:
        reset_test_db(db_config.database_uri)

    run_code(CSV_CODE, mode)
    run_code(IMAGE_CODE, mode)

    db = RelationalLineaDB()
    db.init_db(db_config)
    return db


def run_code(code: str, mode: ExecutionMode):
    """
    Saves code in a temporary file and executes it
    """
    with NamedTemporaryFile() as tmp:
        tmp.write(str.encode(code))
        tmp.flush()
        transformer = Transformer()
        transformer.transform(
            code,
            session_type=SessionType.SCRIPT,
            session_name=tmp.name,
            execution_mode=mode,
        )


def get_project_directory():
    return path.abspath(path.join(__file__, "../.."))
