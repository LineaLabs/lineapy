import pytest

from lineapy.exceptions.user_exception import UserException


def test_get_function(execute):
    """
    Test lineapy.get_function
    """

    code = """\n
import lineapy
a = 1
p = 2
b = a*p
lineapy.save(b,'prod_p')
"""
    res = execute(code, snapshot=False)

    code = "import lineapy\nft = lineapy.get_function(['prod_p'], input_parameters=['a', 'p'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2  # Default value for a and p
    assert ft(a=5)["prod_p"] == 10  # New value for a, default value for p
    assert ft(a=5, p=3)["prod_p"] == 15  # New value for a, new value for p


def test_use_cache(execute):
    """
    Test use_cache
    """

    art_code = """\n
import lineapy
a = 1
p = 2
lineapy.save(p, 'multiplier')
b = a*p
lineapy.save(b,'prod_p')
"""
    execute(art_code, snapshot=False)

    code = """\n
import lineapy
ft = lineapy.get_function(['prod_p'], input_parameters=['a', 'p'], use_cache=['multiplier'])
module_def = lineapy.get_module_definition(['prod_p'], input_parameters=['a', 'p'], use_cache=['multiplier'])
assert ft()['prod_p'] == 2
assert ft(a=5)['prod_p'] == 10
assert ft(a=5, p=3)['prod_p'] == 10  # New value for a, cache value for p;  i.e., 5x2
"""
    res = execute(code, snapshot=False)
    module_def = res.values["module_def"]
    assert 'p = lineapy.get("multiplier", None).get_value()' in module_def


@pytest.mark.parametrize(
    "code",
    [
        pytest.param(
            "import lineapy\nft = lineapy.get_function(['a'], input_parameters=['a','a'])",
            id="duplicated_input_vars",
        ),
        pytest.param(
            "import lineapy\nft = lineapy.get_function(['a'], input_parameters=['a','x'])",
            id="nonexisting_input_vars",
        ),
        pytest.param(
            "import lineapy\nft = lineapy.get_function(['b'], input_parameters=['b'])",
            id="non_literal_assignment",
        ),
        pytest.param(
            "import lineapy\nft = lineapy.get_function(['c'], input_parameters=['c'])",
            id="duplicated_literal_assignment",
        ),
    ],
)
def test_get_function_error(execute, code):
    """
    Sanity check for lineapy.get_function
    """
    art_code = """\n
import lineapy
a = 1
lineapy.save(a,'a')
b = a
lineapy.save(b,'b')
c = 2
c = 3
lineapy.save(c,'c')
"""
    res = execute(art_code, snapshot=False)
    with pytest.raises(UserException) as e_info:
        res = execute(code, snapshot=False)
