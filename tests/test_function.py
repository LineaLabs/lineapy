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
lineapy.save(p, 'multiplier')
b = a*p
lineapy.save(b,'prod_p')
"""
    res = execute(code, snapshot=False)

    # No input parameters
    code = "import lineapy\nft = lineapy.get_function(['prod_p'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2

    # One input parameters
    code = "import lineapy\nft = lineapy.get_function(['prod_p'], input_parameters=['a'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2  # Default value for a; i.e., 1x2
    assert ft(a=5)["prod_p"] == 10  # New value for a; i.e., 5x2

    # Multiple input parameters
    code = "import lineapy\nft = lineapy.get_function(['prod_p'], input_parameters=['a', 'p'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2  # Default value for a and p; i.e., 1x2
    assert (
        ft(a=5)["prod_p"] == 10
    )  # New value for a, default value for p; i.e., 5x2
    assert (
        ft(a=5, p=3)["prod_p"] == 15
    )  # New value for a, new value for p;  i.e., 5x3

    # use cache
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


def test_get_function_sanity(execute):
    """
    Sanity check for lineapy.get_function
    """
    code = """\n
import lineapy
a = 1
lineapy.save(a,'a')
b = a
lineapy.save(b,'b')
c = 2
c = 3
lineapy.save(c,'c')
"""
    res = execute(code, snapshot=False)

    # No input parameters
    code = "import lineapy\nft = lineapy.get_function(['a'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["a"] == 1

    # Identity function
    code = "import lineapy\nft = lineapy.get_function(['a'], input_parameters=['a'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft(a=2)["a"] == 2  # Default value for a and p

    # Duplicated input variables shoud raise an error
    code = "import lineapy\nft = lineapy.get_function(['a'], input_parameters=['a','a'])"
    with pytest.raises(UserException) as e_info:
        res = execute(code, snapshot=False)

    # Inconsist input variables shoud raise an error
    code = "import lineapy\nft = lineapy.get_function(['a'], input_parameters=['a','x'])"
    with pytest.raises(UserException) as e_info:
        res = execute(code, snapshot=False)

    # First variable b is not a literal assignment shoud raise an error
    code = "import lineapy\nft = lineapy.get_function(['b'], input_parameters=['b'])"
    with pytest.raises(UserException) as e_info:
        res = execute(code, snapshot=False)

    # Duplicated literal assignment shoud raise an error
    code = "import lineapy\nft = lineapy.get_function(['c'], input_parameters=['c'])"
    with pytest.raises(UserException) as e_info:
        res = execute(code, snapshot=False)

    # Unused cache should raise an error
    code = "import lineapy\nft = lineapy.get_function(['b'], use_cache=['x'])"
    with pytest.raises(UserException) as e_info:
        res = execute(code, snapshot=False)
