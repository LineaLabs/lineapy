import pytest

from lineapy.exceptions.user_exception import UserException


@pytest.mark.parametrize(
    "code, input, expected",
    [
        pytest.param(
            "import lineapy\nx = 1\nlineapy.save(x,'x')\nft = lineapy.get_function(['x'], input_parameters=['x'])",
            {"x": 1},
            1,
            id="identity",
        ),
        pytest.param(
            "import lineapy\nx = 1\nx = x+1\nlineapy.save(x,'x')\nft = lineapy.get_function(['x'], input_parameters=['x'])",
            {"x": 1},
            2,
            id="mutated",
        ),
    ],
)
def test_same_name_for_artifact_and_input(execute, code, input, expected):
    """
    Test lineapy.get_function
    """
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft(**input)["x"] == expected  # x==x


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


def test_reuse_pre_computed_artifacts_with_version(execute):
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
    "code, message",
    [
        pytest.param(
            "import lineapy\nft = lineapy.get_function(['a'], input_parameters=['a','a'])",
            "Duplicated input parameters detected in ['a', 'a']",
            id="duplicated_input_vars",
        ),
        pytest.param(
            "import lineapy\nft = lineapy.get_function(['a'], input_parameters=['a','x'])",
            "The following variables do not have references in any session code: {'x'}",
            id="nonexisting_input_vars",
        ),
        pytest.param(
            "import lineapy\nft = lineapy.get_function(['b'], input_parameters=['b'])",
            "LineaPy only supports input parameters without dependent variables for now. b has dependent variables: a, c.",
            id="non_literal_assignment",
        ),
        pytest.param(
            # Variable c will affect both artifact b and c
            "import lineapy\nft = lineapy.get_function(['b','c'], input_parameters=['c'])",
            "Variable c, is defined more than once",
            id="duplicated_literal_assignment",
        ),
        pytest.param(
            # Variable e is a list, cannot be an input parameter
            "import lineapy\nft = lineapy.get_function(['e'], input_parameters=['e'])",
            "LineaPy only supports primitive types as input parameters for now. e in e = [] is a <class 'list'>.",
            id="non_primitive_input_parameters",
        ),
        pytest.param(
            # Variable d has a literal and non-literal assignment, code should default correctly to literal, does not error
            "import lineapy\nft = lineapy.get_function(['b','d'], input_parameters=['d'])",
            "",
            id="default_to_literal_assignment",
        ),
    ],
)
def test_get_function_error(execute, code, message):
    """
    Sanity check for lineapy.get_function
    """
    art_code = """\n
import lineapy
a = 1
lineapy.save(a,'a')
c = 1
b = c+a
lineapy.save(b,'b')
c = 2
c = 3
lineapy.save(c,'c')
d = 1
d = d + 1
lineapy.save(d, 'd')
e = []
e.append(1)
lineapy.save(e, 'e')
"""
    res = execute(art_code, snapshot=False)
    # Check exception is raised and error message matches
    if message:
        with pytest.raises(UserException) as e_info:
            res = execute(code, snapshot=False)
        assert message in str(e_info.value)
    # Run as is, no error message expected
    else:
        res = execute(code, snapshot=False)
