"""
Unit tests for the executor.

Unfortunately, the executor requires passing in the database, since
that is used when executing certain nodes which use the database, like call node's
which call `linea.publish`.

This should cover `execution/executor.py`
"""

import operator

from pytest import fixture, mark, param, raises

from lineapy.data.types import ImportNode, Library
from lineapy.exceptions.user_exception import UserException
from lineapy.execution.executor import Executor
from lineapy.utils.lineabuiltins import l_list


@fixture
def executor(linea_db):
    """
    Creates a new executor with the default globals
    """

    return Executor(db=linea_db, _globals=globals())


def test_execute_import(executor: Executor):
    """
    Verify that executing an import gives a value, timing information, and no side effects.
    """
    node = ImportNode(
        id="a_",
        session_id="unused",
        library=Library(id="unused", name="operator"),
    )
    assert not executor.execute_node(node, None)
    assert executor.get_value(node) == operator
    assert isinstance(executor.get_execution_time(node.id), tuple)


def test_execute_import_nonexistant(executor: Executor):
    """
    Verify exception frame matches normal exception frame of importing nonexistanting import.
    """
    node = ImportNode(
        id="a_",
        session_id="unused",
        library=Library(id="unused", name="nonexistant_module"),
    )
    with raises(UserException) as excinfo:
        executor.execute_node(node, None)

    user_exception: UserException = excinfo.value

    with raises(ImportError) as excinfo:
        import nonexistant_module  # noqa
    # Verify string is same as builtin exception
    assert str(excinfo.value) == str(user_exception.__cause__)


def test_execute_import_exception(executor: Executor):
    """
    Verify exception frame matches of that of importing a module with an error.
    """
    node = ImportNode(
        id="a_",
        session_id="unused",
        library=Library(id="unused", name="lineapy.utils.__error_on_load"),
    )
    with raises(UserException) as excinfo:
        executor.execute_node(node, None)

    user_exception: UserException = excinfo.value

    with raises(ZeroDivisionError) as excinfo:
        import lineapy.utils.__error_on_load  # noqa
    # Verify string is same as builtin exception
    assert str(excinfo.value) == str(user_exception.__cause__)


# TODO
def test_execute_call(executor: Executor):
    """
    Verify that executing a call will return the side effects returned by the call, the timing, and the value.
    """
    pass


# TODO
def test_execute_bound_method(executor: Executor):
    """
    Test that getting a bound method and then executing it will properly add self as an implicit positional
    arg.
    """
    pass


# TODO
def test_execute_call_exception(executor: Executor):
    """
    Test that an exception raised by a function call will remove the top frame which includes the execute module.
    """
    pass


# TODO
def test_execute_call_artifact_save_exception(executor: Executor):
    """
    Verify that an exception raised during an artifact save will include the executor frame.
    """
    pass


# TODO
def test_execute_call_mutable_input_vars(executor: Executor):
    """
    Verify that if a global was accessed during a call, and the global was mutable, it is added as a mutate
    side effect.
    """
    pass


# TODO
def test_execute_call_immutable_input_vars(executor: Executor):
    """
    Verify that if a global was accessed during a call, and the global was immutable, it was not added as a mutate
    side effect.
    """
    pass


# TODO
def test_execute_literal(executor: Executor):
    """
    Verify executing a literal returns the value, timing, and no side effects
    """
    pass


# Make a global which is used in the executor globals, since it uses the globals from this module
some_global = object()


# TODO
@mark.parametrize(
    "name,value",
    [
        param("int", int, id="globals"),
        param("mul", operator.mul, id="operator"),
        param("l_list", l_list, id="linea_builtins"),
        param("some_global", some_global, id="custom globals"),
    ],
)
def test_execute_lookup(executor: Executor, name: str, value: object):
    """
    Verify that looking up a variable will return no side effects, a timing, and the value.
    """
    pass


# TODO
def test_execute_lookup_undefined(executor: Executor):
    """
    Verify that if looking up an undefined value, the exception will match the default python exception for an undefined var
    """
    pass


# TODO
def test_execute_mutate(executor: Executor):
    """
    Verify executing a mutate node adds a view between the nodes, the timing of the previous node, and the value of the previous node.
    """
    pass


# TODO
def test_execute_global(executor: Executor):
    """
    Verify that executing a global lookup will lookup the global value set by a call node, and return the timing of
    the call node, and a view between the call node and this node.
    """
    pass


# TODO
def test_execute_node_includes_source_location(executor: Executor):
    """
    Verify that if execting a node which includes a source location, which then raises an exception,
    that the source location will be added to the frames.
    """
    pass


# TOOD: Add tests for returning external state! many if statements here...
