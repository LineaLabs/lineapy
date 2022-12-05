import pytest


@pytest.mark.parametrize(
    "literal_value",
    [
        # Need to escape quotes since formatted string will strip these
        # and test this as an integer otherwise.
        pytest.param("'10'", id="String"),
        pytest.param(False, id="Boolean"),
        pytest.param(10, id="Int"),
        pytest.param(10.0, id="Float"),
        pytest.param(None, id="None"),
        pytest.param(b"10", id="Bytes"),
    ],
)
def test_literal_node_value(execute, literal_value):
    """
    Test that the literal node is serialized and deserialized correctly
    to the DB for supported types.

    TODO: Add test case for ellipses.
    """
    code = f"""import lineapy
val={literal_value}
art = lineapy.save(val, "val")
"""
    res = execute(
        code,
        snapshot=False,
    )

    art = res.values["art"]
    art_val = art.db.get_node_by_id(art.node_id).value
    expected_val = res.values["val"]
    assert art_val == expected_val
