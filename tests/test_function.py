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

    # No input parameters
    code = "import lineapy\nft = lineapy.get_function(['prod_p'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2

    # One input parameters
    code = "import lineapy\nft = lineapy.get_function(['prod_p'], input_parameters=['a'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2  # Default value for a
    assert ft(a=5)["prod_p"] == 10  # New value for a

    # Multiple input parameters
    code = "import lineapy\nft = lineapy.get_function(['prod_p'], input_parameters=['a', 'p'])"
    res = execute(code, snapshot=False)
    ft = res.values["ft"]
    assert ft()["prod_p"] == 2  # Default value for a and p
    assert ft(a=5)["prod_p"] == 10  # New value for a, default value for p
    assert ft(a=5, p=3)["prod_p"] == 15  # New value for a, new value for p
