from lineapy.plugins.task import TaskGraph


def test_task_graph():
    g = TaskGraph(
        ["a", "b", "c"],
        {"c": {"a", "b"}},
    )
    g = g.remap_nodes({"a": "a_p", "b": "b_p", "c": "c_p"})
    expected_orders = [["a_p", "b_p", "c_p"], ["b_p", "a_p", "c_p"]]
    assert g.get_taskorder() in expected_orders
