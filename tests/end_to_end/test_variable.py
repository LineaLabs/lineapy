import sys

from lineapy.data.types import NodeType


def test_variable_assign_to_node(execute):
    """
    Test general case for variable assignment
    """
    code = """import lineapy
a=1
b=a+2
e=a+3
art_e = lineapy.save(e, "e")
"""
    res = execute(
        code,
        snapshot=False,
    )

    art_e = res.values["art_e"]
    node_with_variablename = art_e.db.get_variables_for_session(
        art_e._session_id
    )
    # All variables are captured in the node
    # including the import lineapy and all artifacts
    assert len(node_with_variablename) == 5
    # Only variable 'a' is an LiteralNode; others are all CallNodes in this case
    for node_id, variable_name in node_with_variablename:
        if variable_name == "a":
            assert (
                art_e.db.get_node_by_id(node_id).node_type
                == NodeType.LiteralNode
            )
        else:
            assert (
                art_e.db.get_node_by_id(node_id).node_type == NodeType.CallNode
            )

    if sys.version_info.minor >= 8:
        walrus_code = """import lineapy
seal = (b:='seal')
art_seal = lineapy.save(seal, "seal")
        """
        warlus_res = execute(walrus_code, snapshot=False)
        warlus_art = warlus_res.values["art_seal"]
        node_with_variablename = warlus_art.db.get_variables_for_session(
            warlus_art._session_id
        )
        warlus_code_variables = [x[1] for x in node_with_variablename]

        assert len(warlus_code_variables) == 4
        assert "lineapy" in warlus_code_variables
        assert "b" in warlus_code_variables
        assert "seal" in warlus_code_variables
        assert "art_seal" in warlus_code_variables
        # walrus operator will assign two variables to same node
        assert [n[0] for n in node_with_variablename if n[1] == "seal"][0] == [
            n[0] for n in node_with_variablename if n[1] == "b"
        ][0]


def test_variable_assign_from_other_variable(execute):
    """
    Test variable assignment from existing variables
    """
    code = """import lineapy
a=[]
b = a
c = 1
art = lineapy.save(c,'c')
    """
    res = execute(code, snapshot=False)
    art = res.values["art"]
    node_with_variablename = art.db.get_variables_for_session(art._session_id)
    variable_list = [n[1] for n in node_with_variablename]
    assert len(node_with_variablename) == 5
    assert "a" in variable_list
    assert "b" in variable_list


def test_variable_assign_tuple(execute):
    """
    Test tuple assignment to variables
    """
    code = """import lineapy
a, b = (1,2)
c, d = [3,4]
z = 1
art = lineapy.save(z,'z')
    """
    res = execute(code, snapshot=False)
    art = res.values["art"]
    node_with_variablename = art.db.get_variables_for_session(art._session_id)
    variable_list = [n[1] for n in node_with_variablename]
    assert len(node_with_variablename) == 7
    assert "a" in variable_list
    assert "b" in variable_list
    assert "c" in variable_list
    assert "d" in variable_list
