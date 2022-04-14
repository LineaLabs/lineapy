from lineapy.plugins.task import TaskGraph


def test_task_graph():
    g1 = TaskGraph(
        ["a", "b", "c"],
        {"a": "a_p", "b": "b_p", "c": "c_p"},
        [(("a", "b"), "c")],
    )
    g2 = TaskGraph(
        ["a", "b", "c"],
        {"a": "a_p", "b": "b_p", "c": "c_p"},
        {"c": {"a", "b"}},
    )
    expected_orders = [["a_p", "b_p", "c_p"], ["b_p", "a_p", "c_p"]]
    assert g1.get_taskorder() in expected_orders
    assert g2.get_taskorder() in expected_orders
    expected_airflows = ["a_p>> c_p\nb_p>> c_p", "b_p>> c_p\na_p>> c_p"]
    assert g1.get_airflow_dependency() in expected_airflows
    assert g2.get_airflow_dependency() in expected_airflows
