from pytest import fixture

from lineapy.data.types import ImportNode, LiteralNode, LookupNode, SessionType
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


def test_import_alias(tracer: Tracer):
    tracer.trace_import("json", attributes={"my_loads": "loads"})
    assert tracer.lookup_node("my_loads")
