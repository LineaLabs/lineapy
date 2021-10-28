import traceback
from typing import cast

import pytest

from lineapy.exceptions import UserException


def test_basic_exception(execute):
    code = """def divide_me(a):
    return a/0
x = divide_me(1)
"""
    with pytest.raises(UserException) as e:
        execute(code)

    # Test that the first line of the inner exception is the line in the source
    # file for this call node
    inner_exception = cast(Exception, e.value.__cause__)
    assert (
        traceback.extract_tb(inner_exception.__traceback__)[0].line
        == "x = divide_me(1)"
    )


def test_syntax_error(execute):
    code = """
a = 10
a+++
"""
    with pytest.raises(UserException) as e:
        execute(code)
    inner_exception = cast(Exception, e.value.__cause__)
    assert (
        traceback.extract_tb(inner_exception.__traceback__)[0].line
        == "x = divide_me(1)"
    )
