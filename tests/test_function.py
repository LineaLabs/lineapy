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
ft = lineapy.get_function(['prod_p'], input_parameters=['a', 'p'])
"""
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2  # Default value for a and p
    assert ft(a=5)["prod_p"] == 10  # New value for a, default value for p
    assert ft(a=5, p=3)["prod_p"] == 15  # New value for a, new value for p


def test_reuse_pre_computed_artifacts(execute):
    """
    Test reuse_pre_computed_artifacts option
    """

    code = """\n
import lineapy
a = 1
p = 2
lineapy.save(p, 'multiplier')
b = a*p
lineapy.save(b,'prod_p')

ft = lineapy.get_function(['prod_p'], input_parameters=['a', 'p'], reuse_pre_computed_artifacts=['multiplier'])
module_def = lineapy.get_module_definition(['prod_p'], input_parameters=['a', 'p'], reuse_pre_computed_artifacts=['multiplier'])
assert ft()['prod_p'] == 2
assert ft(a=5)['prod_p'] == 10
assert ft(a=5, p=3)['prod_p'] == 10  # New value for a, cache value for p;  i.e., 5x2
"""
    res = execute(code, snapshot=False)
    module_def = res.values["module_def"]
    assert (
        'p = lineapy.get("multiplier",' in module_def
        and ").get_value()" in module_def
    )


def test_use_old_cache(execute):
    """
    Test reuse_pre_computed_artifacts specified version
    """

    art_code = """\n
import lineapy
p = 10
art = lineapy.save(p, 'multiplier')
art_version = art._version
"""
    res = execute(art_code, snapshot=False)
    art_version = res.values["art_version"]

    code = f"""\n
import lineapy
a = 1
p = 2
lineapy.save(p, 'multiplier')
b = a*p
lineapy.save(b,'prod_p')

ft = lineapy.get_function(['prod_p'], input_parameters=['a', 'p'], reuse_pre_computed_artifacts=[('multiplier', {art_version})])
ft_with_old_multiplier = ft(a=5)["prod_p"]
"""
    res = execute(code, snapshot=False)
    assert (
        res.values["ft_with_old_multiplier"] == 50
    )  # Use old cache value for p; i.e., 5x10


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
