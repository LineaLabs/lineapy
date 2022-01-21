from pytest import fixture

from lineapy.data.types import (
    CallNode,
    GlobalNode,
    LiteralNode,
    LookupNode,
    SessionType,
)
from lineapy.instrumentation.tracer import Tracer


@fixture
def tracer(linea_db):
    return Tracer(linea_db, SessionType.SCRIPT)


def test_lookup_builtin(tracer: Tracer):
    node = tracer.lookup_node("int")
    assert isinstance(node, LookupNode)


def test_lookup_variable(tracer: Tracer):
    literal_node = tracer.literal(10)
    tracer.assign("a", literal_node)
    result_node = tracer.lookup_node("a")
    assert result_node == literal_node


def test_literal(tracer: Tracer):
    node = tracer.literal(10)
    assert isinstance(node, LiteralNode)


def test_import(tracer: Tracer):
    tracer.trace_import("json")
    assert tracer.lookup_node("json")


def test_import_attributes(tracer: Tracer):
    tracer.trace_import("json", attributes={"my_loads": "loads"})
    assert tracer.lookup_node("my_loads")


def test_import_alias(tracer: Tracer):
    tracer.trace_import("json", alias="my_json")
    assert tracer.lookup_node("my_json")


def test_tuple(tracer: Tracer):
    tuple_node = tracer.tuple(tracer.literal(10))
    assert isinstance(tuple_node, CallNode)


def test_mutate(tracer: Tracer):
    l_list = tracer.lookup_node("l_list")
    my_list = tracer.call(l_list, None)

    tracer.assign("my_list", my_list)
    append_str = tracer.literal("append")
    getattr_ = tracer.lookup_node("getattr")
    append_method = tracer.call(getattr_, None, my_list, append_str)
    one = tracer.literal(1)
    tracer.call(append_method, None, one)

    # TODO: Implement this when lookup_node returns the most recent version
    # Verify that assigned value is mutation
    # my_new_list = tracer.lookup_node("my_list")
    # assert my_list != my_new_list
    # assert isinstance(my_new_list, MutateNode)


def test_exec(tracer: Tracer):
    # Test running an exec node that gets a variable and sets a variable

    tracer.assign("y", tracer.literal(10))
    tracer.call(
        tracer.lookup_node("l_exec_statement"), None, tracer.literal("x = y")
    )
    assert isinstance(tracer.lookup_node("x"), GlobalNode)
    assert set(tracer.values.keys()) == {"x", "y"}


def test_implicit_dependency(tracer: Tracer):

    res = tracer.call(
        tracer.lookup_node("open"), None, tracer.literal("setup.py")
    )
    assert isinstance(res, CallNode)
