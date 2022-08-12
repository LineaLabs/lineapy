from pytest import fixture

from lineapy.data.types import (
    CallNode,
    ElseNode,
    GlobalNode,
    IfNode,
    LiteralNode,
    LookupNode,
    NodeType,
    SessionType,
)
from lineapy.instrumentation.tracer import Tracer
from lineapy.utils.utils import get_new_id


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


def test_control_node_if(tracer: Tracer):
    test = tracer.literal(True)
    context = tracer.get_control_node(
        NodeType.IfNode,
        get_new_id(),
        get_new_id(),
        None,
        test.id,
    )
    assert isinstance(context.control_node, IfNode)


def test_control_node_else(tracer: Tracer):
    test = tracer.literal(False)
    if_id = get_new_id()
    else_id = get_new_id()
    context_If = tracer.get_control_node(
        NodeType.IfNode,
        if_id,
        else_id,
        None,
        test.id,
    )
    context = tracer.get_control_node(
        NodeType.ElseNode,
        else_id,
        if_id,
        None,
        test.id,
    )
    assert isinstance(context.control_node, ElseNode)
