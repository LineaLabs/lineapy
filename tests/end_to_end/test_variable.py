from lineapy.data.types import NodeType


def test_node_variables(execute):
    """
    Test

    """
    code = """import lineapy
a=1
b=a+2
c=b*3
d=a*4
e=d+5
art_a = lineapy.save(a, "a")
art_c = lineapy.save(c, "c")
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
    assert len(node_with_variablename) == 9
    # Only variable 'a' is an LiteralNode; others are all CallNodes
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

    walrus_code = """import lineapy
seal = (b:='seal')
art_seal = lineapy.save(seal, "seal")
    """
    warlus_res = execute(walrus_code, snapshot=False)
    warlus_art = warlus_res.values["art_seal"]
    warlus_code_variables = [
        x[1]
        for x in warlus_art.db.get_variables_for_session(
            warlus_art._session_id
        )
    ]

    assert len(warlus_code_variables) == 4
    assert ["lineapy" in warlus_code_variables]
    assert ["b" in warlus_code_variables]
    assert ["seal" in warlus_code_variables]
    assert ["art_seal" in warlus_code_variables]
