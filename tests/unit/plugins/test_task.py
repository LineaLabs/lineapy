from lineapy.plugins.task import TaskGraph


def test_task_graph():
    g = TaskGraph(
        ["a", "b", "c"],
        {"a": "a_p", "b": "b_p", "c": "c_p"},
        {"c": {"a", "b"}},
    )
    expected_orders = [["a_p", "b_p", "c_p"], ["b_p", "a_p", "c_p"]]
    assert g.get_taskorder() in expected_orders
    expected_airflows = ["a_p>> c_p\nb_p>> c_p", "b_p>> c_p\na_p>> c_p"]
    assert g.get_airflow_dependency() in expected_airflows
