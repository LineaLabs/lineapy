"""
Unit tests for the executor.

Unfortunately, the executor requires passing in the database, since
that is used when executing certain nodes which use the database, like call node's
which call `linea.publish`.

This should cover `execution/executor.py`
"""

import operator

from pytest import fixture, mark, param, raises

from lineapy.data.types import (
    CallNode,
    GlobalNode,
    ImportNode,
    Library,
    LineaID,
    LiteralNode,
    LookupNode,
    MutateNode,
)
from lineapy.exceptions.user_exception import UserException
from lineapy.execution.executor import (
    ID,
    AccessedGlobals,
    Executor,
    MutatedNode,
    Variable,
    ViewOfNodes,
)
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
    id_ = LineaID("operator_id")
    assert not executor.execute_node(
        ImportNode(
            id=id_,
            session_id="unused",
            library=Library(id="unused", name="operator"),
        ),
    )
    assert executor.get_value(id_) == operator
    assert isinstance(executor.get_execution_time(id_), tuple)


def test_execute_import_nonexistant(executor: Executor):
    """
    Verify exception frame matches normal exception frame of importing nonexistanting import.
    """
    node = ImportNode(
        id="a",
        session_id="unused",
        library=Library(id="unused", name="nonexistant_module"),
    )
    with raises(UserException) as excinfo:
        executor.execute_node(node)

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
        id="a",
        session_id="unused",
        library=Library(id="unused", name="lineapy.utils.__error_on_load"),
    )
    with raises(UserException) as excinfo:
        executor.execute_node(node)

    user_exception: UserException = excinfo.value

    with raises(ZeroDivisionError) as excinfo:
        import lineapy.utils.__error_on_load  # noqa
    # Verify string is same as builtin exception
    assert str(excinfo.value) == str(user_exception.__cause__)


def test_execute_call(executor: Executor):
    """
    Verify that executing a call will return the side effects returned by the call, the timing, and the value.
    """
    # First lookup the `neg` operator
    executor.execute_node(
        LookupNode(id="neg", name="neg", session_id="unused")
    )
    # Then add the 1 literal
    executor.execute_node(LiteralNode(id="one", value=1, session_id="unused"))

    # Now call neg with one
    id_ = LineaID("neg-one")
    side_effects = executor.execute_node(
        CallNode(
            id=id_,
            session_id="unused",
            function_id="neg",
            positional_args=["one"],
        )
    )
    # There should be no side effects
    assert not side_effects

    # we should be able to get the value
    assert executor.get_value(id_) == -1

    # and the timing
    assert isinstance(executor.get_execution_time(id_), tuple)


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


def test_execute_call_mutable_input_vars(executor: Executor):
    """
    Verify that if a global was accessed during a call, and the global was mutable, it is added as a mutate
    side effect.
    """
    # Create a list
    assert not executor.execute_node(
        LookupNode(id="l_list", name="l_list", session_id="")
    )
    assert not executor.execute_node(
        CallNode(id="list", function_id="l_list", session_id="")
    )

    # Use exec statement to re-assign the list to another variable
    assert not executor.execute_node(
        LookupNode(
            id="l_exec_statement", name="l_exec_statement", session_id=""
        )
    )
    assert not executor.execute_node(
        LiteralNode(
            id="assign_str", value="x.append(10); y = x", session_id=""
        )
    )

    # Assert that it assigned to a global
    call_side_effects = executor.execute_node(
        CallNode(
            id="assign_call",
            function_id="l_exec_statement",
            positional_args=["assign_str"],
            session_id="",
        ),
        {"x": LineaID("list")},
    )
    assert call_side_effects == [
        AccessedGlobals(retrieved=["x"], added_or_updated=["y"]),
        MutatedNode(ID(LineaID("list"))),
        # The list and the variable should be views
        ViewOfNodes([ID(LineaID("list")), Variable("y")]),
    ]


# TODO
def test_execute_call_immutable_input_vars(executor: Executor):
    """
    Verify that if a global was accessed during a call, and the global was immutable, it was not added as a mutate
    side effect.
    """
    pass


def test_execute_literal(executor: Executor):
    """
    Verify executing a literal returns the value, timing, and no side effects
    """
    id_ = LineaID("one")

    executor.execute_node(LiteralNode(id=id_, value=1, session_id="unused"))
    assert executor.get_value(id_) == 1
    assert executor.get_execution_time(id_)


# Make a global which is used in the executor globals, since it uses the globals from this module
some_global = object()


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
    id_ = LineaID("lookup_oid")
    executor.execute_node(LookupNode(id=id_, name=name, session_id="unused"))
    assert executor.get_value(id_) == value
    assert executor.get_execution_time(id_)


# TODO
def test_execute_lookup_undefined(executor: Executor):
    """
    Verify that if looking up an undefined value, the exception will match the default python exception for an undefined var
    """
    pass


def test_execute_mutate(executor: Executor):
    """
    Verify executing a mutate node adds a view between the nodes, the timing of the previous node, and the value of the previous node.
    """
    # Create a list and append to it.

    # Create the list
    assert not executor.execute_node(
        LookupNode(id="l_list", name="l_list", session_id="")
    )
    assert not executor.execute_node(
        CallNode(id="list", function_id="l_list", session_id="")
    )

    # Get the append method
    assert not executor.execute_node(
        LookupNode(id="getattr", name="getattr", session_id="")
    )
    assert not executor.execute_node(
        LiteralNode(id="append_str", value="append", session_id="")
    )
    assert not executor.execute_node(
        CallNode(
            id="append_method",
            function_id="getattr",
            positional_args=["list", "append_str"],
            session_id="",
        )
    )
    # append one to it
    assert not executor.execute_node(
        LiteralNode(id="one", value=1, session_id="")
    )
    side_effects = executor.execute_node(
        CallNode(
            id="call_append",
            function_id="append_method",
            positional_args=["one"],
            session_id="",
        )
    )
    # Assert that list is mutated
    assert side_effects == [MutatedNode(ID(LineaID("list")))]

    # Now create a mutate node for the new list
    mutate_side_effects = executor.execute_node(
        MutateNode(
            id="mutated_list",
            session_id="",
            source_id="list",
            call_id="call_append",
        )
    )
    # Verify there is a view now between them
    assert mutate_side_effects == [
        ViewOfNodes(
            [
                ID(LineaID("mutated_list")),
                ID(LineaID("list")),
            ]
        )
    ]

    # Verify value and timing is copied
    assert executor.get_execution_time(
        LineaID("mutated_list")
    ) == executor.get_execution_time(LineaID("call_append"))
    assert executor.get_value(LineaID("mutated_list")) == executor.get_value(
        LineaID("list")
    )


# TODO
def test_execute_global(executor: Executor):
    """
    Verify that executing a global lookup will lookup the global value set by a call node, and return the timing of
    the call node, and a view between the call node and this node.
    """
    # Use exec statement to execute assigning a variable, then grabbing it
    assert not executor.execute_node(
        LookupNode(
            id="l_exec_statement", name="l_exec_statement", session_id=""
        )
    )
    assert not executor.execute_node(
        LiteralNode(id="assign_str", value="x = 1", session_id="")
    )
    # Assert that it assigned to a global
    call_side_effects = executor.execute_node(
        CallNode(
            id="assign_call",
            function_id="l_exec_statement",
            positional_args=["assign_str"],
            session_id="",
        )
    )
    assert call_side_effects == [
        AccessedGlobals(retrieved=[], added_or_updated=["x"])
    ]
    # Now create a global node to get the value
    assert not executor.execute_node(
        GlobalNode(id="x", session_id="", name="x", call_id="assign_call")
    )
    # Verify it has same timing as parent and has value
    assert executor.get_execution_time(
        LineaID("x")
    ) == executor.get_execution_time(LineaID("assign_call"))
    assert executor.get_value(LineaID("x")) == 1


# TODO
def test_execute_node_includes_source_location(executor: Executor):
    """
    Verify that if execting a node which includes a source location, which then raises an exception,
    that the source location will be added to the frames.
    """
    pass


# TOOD: Add tests for returning external state! many if statements here...
