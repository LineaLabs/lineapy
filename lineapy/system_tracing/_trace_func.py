from __future__ import annotations

import functools
import operator
from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from dis import Instruction, get_instructions
from sys import version_info
from types import CodeType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

from lineapy.system_tracing._op_stack import OpStack
from lineapy.system_tracing.function_call import FunctionCall

# This callback is saved when we have an operator that had some function call. We need to defer some of the processing until the next bytecode instruction loads,
# So that at the point, the return value will be in the stack and we can look at it.
# Called with the opstack and the next instruction offset
ReturnValueCallback = Callable[
    [OpStack, int], Union[FunctionCall, None, Iterable[FunctionCall]]
]


@dataclass
class TraceFunc:
    code: InitVar[CodeType]
    function_calls: List[FunctionCall] = field(default_factory=list)
    # Set of operations we encounter that we don't know how to handle
    not_implemented_ops: Set[str] = field(default_factory=set)

    # Mapping of each code object that was passed in to its instructions,
    # by offset, so we can quickly look up what instruction we are looking at
    code_to_offset_to_instruction: Dict[
        CodeType, Dict[int, Instruction]
    ] = field(init=False)

    # If set for the code object, then the previous bytecode instruction in the
    # frame for that code object had a function call, and during the next call,
    # we should call
    # this function with the current stack to get the FunctionCall result.
    code_to_return_value_callback: Dict[CodeType, ReturnValueCallback] = field(
        default_factory=dict
    )

    def __post_init__(self, code):
        self.code_to_offset_to_instruction = {
            code: {i.offset: i for i in get_instructions(code)}
            for code in all_code_objects(code)
        }

    def __call__(self, frame, event, arg):
        # Exit early if the code object for this frame is not one of the code
        # objects that is contained in the source code passed in (i.e., specifically
        # in the current usecase, anything outside of the blackbox).
        try:
            offset_to_instruction = self.code_to_offset_to_instruction[
                frame.f_code
            ]
        except KeyError:
            return self

        # If it is one we want to trace, enable opcode tracing on it
        frame.f_trace_opcodes = True
        # If this is not an opcode event, ignore it
        if event != "opcode":
            return self

        # Lookup the instruction we currently have based on the code object as
        # well as the offset in that object
        # Pop the instruction off the mapping, so that we only trace each bytecode once (for performance reasons)
        try:
            instruction = offset_to_instruction.pop(frame.f_lasti)
        except KeyError:
            return self

        code = frame.f_code
        offset = frame.f_lasti

        # We want to see the name and the arg for the actual instruction, not
        # the arg, so increment until we get to that
        extended_arg_counter = 1
        while instruction.opname == "EXTENDED_ARG":
            offset += 2
            extended_arg_counter += 1
            instruction = self.code_to_offset_to_instruction[code][offset]

        # Create an op stack around the frame so we can access the stack
        op_stack = OpStack(frame)

        # If during last instruction we had some function call that needs a
        # return value, trigger the callback with the current
        # stack, so it can get the return value.
        if code in self.code_to_return_value_callback:
            return_value_callback = self.code_to_return_value_callback[code]
            function_call = return_value_callback(op_stack, frame.f_lasti)
            if isinstance(function_call, FunctionCall):
                self.function_calls.append(function_call)
            elif function_call:
                self.function_calls.extend(function_call)
            del self.code_to_return_value_callback[code]

        # Check if the current operation is a function call
        try:
            possible_function_call = resolve_bytecode_execution(
                instruction.opname,
                instruction.argval,
                instruction.arg,
                op_stack,
                frame.f_lasti,
                extended_arg_counter,
            )
        except NotImplementedError:
            self.not_implemented_ops.add(instruction.opname)
            possible_function_call = None
        # If resolving the function call needs to be deferred until after we
        # have the return value, save the callback
        if callable(possible_function_call):
            self.code_to_return_value_callback[code] = possible_function_call
        # Otherwise, if we could resolve it fully now, add that to our function call
        elif isinstance(possible_function_call, FunctionCall):
            self.function_calls.append(possible_function_call)
        elif possible_function_call:
            self.function_calls.extend(possible_function_call)

        return self


# Bytecode operations that are not function calls
NOT_FUNCTION_CALLS = {
    "NOP",
    "POP_TOP",
    "ROT_TWO",
    "ROT_THREE",
    "ROT_FOUR",
    "DUP_TOP",
    "DUP_TOP_TWO",
    "COPY",
    "SWAP",
    "RETURN_VALUE",
    "YIELD_VALUE",
    "YIELD_FROM",
    "SETUP_ANNOTATIONS",
    "POP_BLOCK",
    "POP_EXCEPT",
    "RERAISE",
    "LOAD_ASSERTION_ERROR",
    "LOAD_BUILD_CLASS",
    "STORE_NAME",
    "DELETE_NAME",
    "STORE_GLOBAL",
    "DELETE_GLOBAL",
    "LOAD_CONST",
    "LOAD_NAME",
    "BUILD_STRING",
    "WITH_CLEANUP_FINISH",
    "JUMP_FORWARD",
    "POP_JUMP_IF_TRUE",
    "POP_JUMP_IF_FALSE",
    "JUMP_IF_NOT_EXC_MATCH",
    "JUMP_IF_TRUE_OR_POP",
    "JUMP_IF_FALSE_OR_POP",
    "JUMP_ABSOLUTE",
    "LOAD_GLOBAL",
    "SETUP_FINALLY",
    "LOAD_FAST",
    "BEGIN_FINALLY",
    "STORE_FAST",
    "DELETE_FAST",
    "LOAD_CLOSURE",
    "LOAD_DEREF",
    "LOAD_CLASSDEREF",
    "STORE_DEREF",
    "DELETE_DEREF",
    "RAISE_VARARGS",
    "LOAD_METHOD",
    "MAKE_FUNCTION",
    "ROT_N",
    "SETUP_LOOP",
    "END_FINALLY",
    "POP_FINALLY",
}

UNARY_OPERATORS = {
    "UNARY_POSITIVE": operator.pos,
    "UNARY_NEGATIVE": operator.neg,
    "UNARY_NOT": operator.not_,
    "UNARY_INVERT": operator.inv,
    "GET_ITER": iter,
}

BINARY_OPERATIONS = {
    "BINARY_POWER": operator.pow,
    "BINARY_MULTIPLY": operator.mul,
    "BINARY_MATRIX_MULTIPLY": operator.matmul,
    "BINARY_FLOOR_DIVIDE": operator.floordiv,
    "BINARY_TRUE_DIVIDE": operator.truediv,
    "BINARY_MODULO": operator.mod,
    "BINARY_ADD": operator.add,
    "BINARY_SUBTRACT": operator.sub,
    "BINARY_SUBSCR": operator.getitem,
    "BINARY_LSHIFT": operator.lshift,
    "BINARY_RSHIFT": operator.rshift,
    "BINARY_AND": operator.and_,
    "BINARY_XOR": operator.xor,
    "BINARY_OR": operator.or_,
    # Inplace
    "INPLACE_POWER": operator.ipow,
    "INPLACE_MULTIPLY": operator.imul,
    "INPLACE_MATRIX_MULTIPLY": operator.imatmul,
    "INPLACE_FLOOR_DIVIDE": operator.ifloordiv,
    "INPLACE_TRUE_DIVIDE": operator.itruediv,
    "INPLACE_MODULO": operator.imod,
    "INPLACE_ADD": operator.iadd,
    "INPLACE_SUBTRACT": operator.isub,
    "INPLACE_LSHIFT": operator.ilshift,
    "INPLACE_RSHIFT": operator.irshift,
    "INPLACE_AND": operator.iand,
    "INPLACE_XOR": operator.ixor,
    "INPLACE_OR": operator.ior,
}


def compose(f, g):
    return lambda *a, **kw: f(g(*a, **kw))


def composer(*fs):
    return functools.reduce(compose, fs)


# Maybe of string compare ops, from dis.cmp_op, to operator
COMPARE_OPS: Dict[str, Callable] = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.neg,
    ">": operator.gt,
    ">=": operator.ge,
    # Python 3.7
    "in": operator.contains,
    "is": operator.is_,
    "not in": composer(operator.not_, operator.contains),
}


"""
Defer supporting imports until after imports are turned into call nodes
Usually we don't need to worry about it, at least in the context of slicing,
but consider the following example:
# ```
# import x
# if ...:
#   import x.y
# a = x.y.z + 1
# ```
lineapy.save(a, "weird value") actually would have a dependency on the blackbox, as discussed in
https://github.com/LineaLabs/lineapy/blob/main/docs/source/rfcs/0001-imports.md.
Can read more: https://docs.python.org/3/reference/import.html#submodules

Here are the ones we don't support:
- IMPORT_STARIMPORT_STAR
- IMPORT_NAME
- IMPORT_FROM
"""


##
# We haven't thought much about generator functions, so we don't trace
# them for now.
##

# GET_YIELD_FROM_ITER
# GET_AWAITABLE
# GET_AITER
# GET_ANEXT
# END_ASYNC_FOR
# BEFORE_ASYNC_WITH

##
# Python 3.10 ops not supported
##
# COPY_DICT_WITHOUT_KEYS
# GET_LEN
# MATCH_MAPPING
# MATCH_SEQUENCE
# MATCH_KEYS
# MATCH_CLASS
# GEN_START


##
# Not sure when these appear
##

# BUILD_CONST_KEY_MAP
# LIST_TO_TUPLE
# DICT_MERGE


def resolve_bytecode_execution(
    name: str,
    value: Any,
    arg: Optional[int],
    stack: OpStack,
    offset: int,
    extended_arg_count: int,
) -> Union[Iterable[FunctionCall], ReturnValueCallback, FunctionCall, None]:
    """
    Returns a function call corresponding to the bytecode executing on the current stack.
    """
    if name in NOT_FUNCTION_CALLS:
        return None
    if name in UNARY_OPERATORS:
        # Unary operations take the top of the stack, apply the operation, and push the
        # result back on the stack.
        args = [stack[-1]]
        return lambda post_stack, _: FunctionCall(
            # updating mypy to 0.942 causes issues here. mypy 0.931 works fine.
            # something is up with the iter because the same thing works for binary ops below
            UNARY_OPERATORS[name],  # type: ignore
            args,
            {},
            post_stack[-1],
        )
    if name in BINARY_OPERATIONS:
        # Binary operations remove the top of the stack (TOS) and the second top-most
        # stack item (TOS1) from the stack.  They perform the operation, and put the
        # result back on the stack.
        args = [stack[-2], stack[-1]]
        return lambda post_stack, _: FunctionCall(
            BINARY_OPERATIONS[name], args, {}, post_stack[-1]
        )
    if name == "FOR_ITER":
        """
        From the original Python source code documentation:
        # TOS is an `iterator`.  Call its `__next__` method.  If
        # this yields a new value, push it on the stack (leaving the iterator below
        # it).  If the iterator indicates it is exhausted, TOS is popped, and the byte
        # code counter is incremented by *delta*.

        We need to handle the case when the code body is large and needs
        `EXTENDED_ARG`, this breaks the assumption that the offset will increase
        by 2, so we have the count of extended_arg passed in as traced by the caller
        and count with that instead.
        ```
        >>> large_for_loop_code = "for _ in x:\n  i = 1\n" + "  j = i\n" * 100
        >>> dis.dis(large_for_loop_code)
        1           0 LOAD_NAME                0 (x)
                    2 GET_ITER
                    4 EXTENDED_ARG             1
                    6 FOR_ITER               408 (to 416)
                    8 STORE_NAME               1 (_)

        2          10 LOAD_CONST               0 (1)
        ```

        So we translated to:
        If the current instruction is the next one (i.e. the offset has increased by 2), then we didn't jump,
        meaning the iterator was not exhausted. Otherwise, we did jump, and it was, so don't add a function call for this.

        Note tha if we start handling exception, we should edit how we are
        handling the loops, since Python uses the try/catch mechanism to catch
        loop end.
        """
        args = [stack[-1]]

        return (
            lambda post_stack, post_offset: FunctionCall(
                next, args, {}, post_stack[-1]
            )
            if post_offset == offset + 2 * extended_arg_count
            else None
        )
    if name == "STORE_SUBSCR":
        # Implements ``TOS1[TOS] = TOS2``.
        return FunctionCall(
            operator.setitem, [stack[-2], stack[-1], stack[-3]]
        )
    if name == "DELETE_SUBSCR":
        # Implements ``del TOS1[TOS]``.
        return FunctionCall(operator.delitem, [stack[-2], stack[-1]])
    if name == "SET_ADD":
        # Calls ``set.add(TOS1[-i], TOS)``.  Used to implement set comprehensions.
        return FunctionCall(getattr(stack[-value - 1], "add"), [stack[-1]])
    if name == "LIST_APPEND":
        # Calls `list.append(TOS1[-i], TOS)`.  Used to implement list comprehensions.
        return FunctionCall(getattr(stack[-value - 1], "append"), [stack[-1]])

    if name == "MAP_ADD":
        #  Calls `dict.__setitem__(TOS1[-i], TOS1, TOS)`.  Used to implement dict comprehensions.
        dict_ = stack[-value - 2]
        # Version 3.8:  Map value is TOS and map key is TOS1. Before, those were reversed.
        if version_info >= (3, 8):
            key = stack[-2]
            value = stack[-1]
        else:
            key = stack[-1]
            value = stack[-2]
        return FunctionCall(operator.setitem, [dict_, key, value])
    if name == "WITH_EXCEPT_START":
        # Calls the function in position 7 on the stack with the top three
        # items on the stack as arguments.
        # Used to implement the call ``context_manager.__exit__(*exc_info())`` when an exception
        # has occurred in a :keyword:`with` statement.
        fn = stack[-7]
        args = [stack[-1], stack[-2], stack[-3]]
        return lambda post_stack, _: FunctionCall(fn, args, res=post_stack[-1])

    if name == "SETUP_WITH":
        # This opcode performs several operations before a with block starts.  First,
        # it loads `__exit__` from the context manager and pushes it onto
        # the stack for later use by `WITH_EXCEPT_START`.  Then,
        # `__enter__` is called, and a finally block pointing to *delta*
        # is pushed.  Finally, the result of calling the ``__enter__()`` method is pushed onto
        # the stack.  The next opcode will either ignore it (`POP_TOP`), or
        # store it in (a) variable(s) (`STORE_FAST`, `STORE_NAME`, or
        # `UNPACK_SEQUENCE`).
        x = stack[-1]
        # The __enter__ bound method is never saved to the stack, so we recompute it to save in the function call
        return lambda post_stack, _: FunctionCall(
            getattr(x, "__enter__"), [], res=post_stack[-1]
        )

    if name == "WITH_CLEANUP_START":
        # At the top of the stack are 1-6 values indicating
        # how/why we entered the finally clause:
        # - TOP = None
        # - (TOP, SECOND) = (WHY_{RETURN,CONTINUE}), retval
        # - TOP = WHY_*; no retval below it
        # - (TOP, SECOND, THIRD) = exc_info()
        #     (FOURTH, FIFTH, SIXTH) = previous exception for EXCEPT_HANDLER
        # Below them is EXIT, the context.__exit__ bound method.
        # In the last case, we must call
        #     EXIT(TOP, SECOND, THIRD)
        # otherwise we must call
        #     EXIT(None, None, None)

        # In the first three cases, we remove EXIT from the
        # stack, leaving the rest in the same order.  In the
        # fourth case, we shift the bottom 3 values of the
        # stack down, and replace the empty spot with NULL.

        # In addition, if the stack represents an exception,
        # *and* the function call returns a 'true' value, we
        # push WHY_SILENCED onto the stack.  END_FINALLY will
        # then not re-raise the exception.  (But non-local
        # gotos should still be resumed.)
        args = [None, None, None]
        try:
            exc = stack[-1]
        except ValueError:
            exc = None
            fn = stack[-2]
        if exc is None:
            fn = stack[-2]
        elif isinstance(exc, int):
            # WHY_RETURN and WHY_CONTINUE
            if exc in {0x0008, 0x0020}:
                fn = stack[-3]
            else:
                fn = stack[-2]
        else:
            args = [exc, stack[-2], stack[-3]]
            fn = stack[-7]
        return lambda post_stack, _: FunctionCall(fn, args, res=post_stack[-1])
    if name == "UNPACK_SEQUENCE":
        # Unpacks TOS into *count* individual values, which are put onto the stack
        # right-to-left.
        from lineapy.utils.lineabuiltins import l_unpack_sequence

        seq = stack[-1]

        def callback(post_stack: OpStack, _):
            # Replicate the behavior of using our internal functions for unpacking
            unpacked = [post_stack[-i - 1] for i in range(value)]
            yield FunctionCall(l_unpack_sequence, [seq, value], res=unpacked)
            for i, v in enumerate(unpacked):
                yield FunctionCall(operator.getitem, [unpacked, i], res=v)

        return callback
    if name == "UNPACK_EX":
        # Implements assignment with a starred target: Unpacks an iterable in TOS into
        # individual values, where the total number of values can be smaller than the
        # number of items in the iterable: one of the new values will be a list of all
        # leftover items.
        #
        # The low byte of *counts* is the number of values before the list value, the
        # high byte of *counts* the number of values after it.  The resulting values
        # are put onto the stack right-to-left.

        from lineapy.utils.lineabuiltins import l_unpack_ex

        seq = stack[-1]

        count_left = cast(int, arg) % 256
        count_right = cast(int, arg) >> 8

        def callback(post_stack: OpStack, _):
            unpacked = [
                post_stack[-i - 1] for i in range(count_left + count_right + 1)
            ]
            yield FunctionCall(
                l_unpack_ex, [seq, count_left, count_right], res=unpacked
            )
            for i, v in enumerate(unpacked):
                yield FunctionCall(operator.getitem, [unpacked, i], res=v)

        return callback

    if name == "STORE_ATTR":
        # Implements ``TOS.name = TOS1``, where *namei* is the index of name in
        # `co_names`.
        return FunctionCall(setattr, [stack[-1], value, stack[-2]])
    if name == "DELETE_ATTR":
        # Implements ``del TOS.name``, using *namei* as index into :attr:`co_names`.
        return FunctionCall(delattr, [stack[-1], value])

    if name in {"BUILD_TUPLE", "BUILD_LIST", "BUILD_SET"}:
        # Creates a tuple consuming *count* items from the stack, and pushes the
        # resulting tuple onto the stack.
        from lineapy.utils.lineabuiltins import l_list, l_set, l_tuple

        INSTRUCTION_TO_FN = {
            "BUILD_TUPLE": l_tuple,
            "BUILD_LIST": l_list,
            "BUILD_SET": l_set,
        }
        fn = INSTRUCTION_TO_FN[name]

        args = [stack[-i - 1] for i in range(value)]
        args.reverse()
        return lambda post_stack, stack_offset: FunctionCall(
            fn, args, res=post_stack[-1]
        )

    if name == "LIST_TO_TUPLE":
        args = [stack[-1]]
        return lambda post_stack, stack_offset: FunctionCall(
            tuple, args, res=post_stack[-1]
        )
    # Python < 3.9
    if name == "BUILD_TUPLE_UNPACK":
        from lineapy.utils.lineabuiltins import l_list

        # Compiles down to one empty list creation, followed by a number of extends, and then convert to tuple
        args = [stack[-i - 1] for i in range(value)]
        args.reverse()

        def callback(post_stack: OpStack, _):
            intermediate_list = list(post_stack[-1])
            extend = intermediate_list.extend
            return [
                FunctionCall(l_list, res=intermediate_list),
                *(FunctionCall(extend, [a]) for a in args),
                FunctionCall(tuple, [intermediate_list], res=post_stack[-1]),
            ]

        return callback

    if name == "BUILD_LIST_UNPACK":

        # Compiles down to one empty list creation, followed by a number of extends
        args = [stack[-i - 1] for i in range(value)]
        args.reverse()
        return lambda post_stack, stack_offset: [
            FunctionCall(list, res=post_stack[-1])
        ] + [
            FunctionCall(getattr(post_stack[-1], "extend"), [a]) for a in args
        ]
    if name == "BUILD_TUPLE_UNPACK":

        # Compiles down to one empty list creation, followed by a number of extends, and then convert to tuple
        args = [stack[-i - 1] for i in range(value)]
        args.reverse()

        def callback(post_stack: OpStack, _):
            intermediate_list = list(post_stack[-1])
            extend = intermediate_list.extend
            return [
                FunctionCall(l_list, res=intermediate_list),
                *(FunctionCall(extend, [a]) for a in args),
                FunctionCall(tuple, [intermediate_list], res=post_stack[-1]),
            ]

        return callback
    if name == "BUILD_SET_UNPACK":
        from lineapy.utils.lineabuiltins import l_set

        # Compiles down to one empty set creation, followed by a number of update
        args = [stack[-i - 1] for i in range(value)]
        args.reverse()
        return lambda post_stack, stack_offset: [
            FunctionCall(l_set, res=post_stack[-1])
        ] + [
            FunctionCall(getattr(post_stack[-1], "update"), [a]) for a in args
        ]
    if name == "BUILD_MAP_UNPACK":
        from lineapy.utils.lineabuiltins import l_dict

        # Compiles down to one empty dic creation, followed by a number of extends
        args = [stack[-i - 1] for i in range(value)]
        args.reverse()
        return lambda post_stack, stack_offset: [
            FunctionCall(l_dict, res=post_stack[-1])
        ] + [
            FunctionCall(getattr(post_stack[-1], "update"), [a]) for a in args
        ]
    if name == "BUILD_MAP":
        # Pushes a new dictionary object onto the stack.  Pops ``2 * count`` items
        # so that the dictionary holds *count* entries:
        # ``{..., TOS3: TOS2, TOS1: TOS}``.
        from lineapy.utils.lineabuiltins import l_dict, l_tuple  # noqa: F811

        args = [(stack[-i * 2 - 2], stack[-i * 2 - 1]) for i in range(value)]
        args.reverse()

        return lambda post_stack, stack_offset: [
            FunctionCall(l_tuple, [k, v], res=(k, v)) for k, v in args
        ] + [FunctionCall(l_dict, args, res=post_stack[-1])]

    if name == "LIST_EXTEND":
        return FunctionCall(getattr(stack[-value - 1], "extend"), [stack[-1]])

    if name == "SET_UPDATE":
        return FunctionCall(getattr(stack[-value - 1], "update"), [stack[-1]])

    if name == "DICT_UPDATE" or name == "DICT_MERGE":
        return FunctionCall(getattr(stack[-value - 1], "update"), [stack[-1]])

    if name == "LOAD_ATTR":
        o = stack[-1]
        return lambda post_stack, _: FunctionCall(
            getattr, [o, value], res=post_stack[-1]
        )

    if name == "COMPARE_OP":
        args = [stack[-2], stack[-1]]
        if value == "in":
            args.reverse()
        return lambda post_stack, _: FunctionCall(
            COMPARE_OPS[value], args, res=post_stack[-1]
        )

    if name == "IS_OP":
        args = [stack[-2], stack[-1]]
        return lambda post_stack, _: FunctionCall(
            operator.is_, args, res=post_stack[-1]
        )
    if name == "CONTAINS_OP":
        args = [stack[-1], stack[-2]]
        return lambda post_stack, _: FunctionCall(
            operator.contains, args, res=post_stack[-1]
        )
    if name == "CALL_FUNCTION":
        # Calls a callable object with positional arguments.
        # *argc* indicates the number of positional arguments.
        # The top of the stack contains positional arguments, with the right-most
        # argument on top.  Below the arguments is a callable object to call.
        # `CALL_FUNCTION` pops all arguments and the callable object off the stack,
        # calls the callable object with those arguments, and pushes the return value
        # returned by the callable object.
        args = list(reversed([stack[-i - 1] for i in range(value)]))
        fn = stack[-value - 1]
        return lambda post_stack, _: FunctionCall(fn, args, res=post_stack[-1])

    if name == "CALL_FUNCTION_KW":
        # Calls a callable object with positional (if any) and keyword arguments.
        # *argc* indicates the total number of positional and keyword arguments.
        # The top element on the stack contains a tuple with the names of the
        # keyword arguments, which must be strings.
        # Below that are the values for the keyword arguments,
        # in the order corresponding to the tuple.
        # Below that are positional arguments, with the right-most parameter on
        # top.  Below the arguments is a callable object to call.
        # ``CALL_FUNCTION_KW`` pops all arguments and the callable object off the stack,
        # calls the callable object with those arguments, and pushes the return value
        # returned by the callable object.
        kwarg_names: Tuple[str, ...] = stack[-1]
        n_kwargs = len(kwarg_names)
        kwargs = {
            k: stack[-i - 2] for i, k in enumerate(reversed(kwarg_names))
        }
        args = [stack[-i - 2] for i in reversed(range(n_kwargs, value))]
        fn = stack[-value - 2]
        return lambda post_stack, _: FunctionCall(
            fn, args, kwargs, post_stack[-1]
        )

    if name == "CALL_FUNCTION_EX":
        # the only case that we cannot handle is an generator that exhausts
        #   then `raise NotImplementedError()`
        # The way we figure out if something is an iterator without accidentally calling .next, is to check whether it's a Sequence, since a generator doesn't have __getitem__ (the streaming/lazy semantic) https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes
        if cast(int, arg) & 0x01:
            # then it's kwargs
            kwargs = stack[-1]
            args = stack[-2]
            fn = stack[-3]
        else:
            # then it's positional
            args = stack[-1]
            fn = stack[-2]
        # check if the function is a generator
        if not isinstance(args, Sequence):
            raise NotImplementedError()
        return lambda post_stack, _: FunctionCall(
            fn, list(args), kwargs, post_stack[-1]
        )

    if name == "CALL_METHOD":
        # Calls a method.  *argc* is the number of positional arguments.
        # Keyword arguments are not supported.  This opcode is designed to be used
        # with `LOAD_METHOD`.  Positional arguments are on top of the stack.
        # Below them, the two items described in `LOAD_METHOD` are on the
        # stack (either ``self`` and an unbound method object or ``NULL`` and an
        # arbitrary callable). All of them are popped and the return value is pushed.

        args = list(reversed([stack[-i - 1] for i in range(value)]))
        self_ = stack[-value - 1]
        try:
            method = stack[-value - 2]
        # This is raised when it is NULL
        except ValueError:
            fn = self_
        else:
            fn = getattr(self_, method.__name__)
        return lambda post_stack, _: FunctionCall(fn, args, res=post_stack[-1])

    if name == "BUILD_SLICE":
        # Pushes a slice object on the stack.  *argc* must be 2 or 3.  If it is 2,
        # ``slice(TOS1, TOS)`` is pushed; if it is 3, ``slice(TOS2, TOS1, TOS)`` is
        # pushed. See the :func:`slice` built-in function for more information.
        if value == 2:
            args = [stack[-2], stack[-1]]
        elif value == 3:
            args = [stack[-3], stack[-2], stack[-1]]
        else:
            raise NotImplementedError()

        return lambda post_stack, _: FunctionCall(
            slice, args, res=post_stack[-1]
        )
    if name == "FORMAT_VALUE":
        # Used for implementing formatted literal strings (f-strings).  Pops
        # an optional *fmt_spec* from the stack, then a required *value*.
        # *flags* is interpreted as follows:
        #
        # * ``(flags & 0x03) == 0x00``: *value* is formatted as-is.
        # * ``(flags & 0x03) == 0x01``: call :func:`str` on *value* before
        #     formatting it.
        # * ``(flags & 0x03) == 0x02``: call :func:`repr` on *value* before
        #     formatting it.
        # * ``(flags & 0x03) == 0x03``: call :func:`ascii` on *value* before
        #     formatting it.
        # * ``(flags & 0x04) == 0x04``: pop *fmt_spec* from the stack and use
        #     it, else use an empty *fmt_spec*.
        #
        # Formatting is performed using :c:func:`PyObject_Format`.  The
        # result is pushed on the stack.
        have_format_spec = (cast(int, arg) & 0x04) == 0x04

        if have_format_spec:
            format_spec = stack[-1]
            str_ = stack[-2]
        else:
            format_spec = None
            str_ = stack[-1]

        which_conversion = cast(int, arg) & 0x03
        if which_conversion == 0x00:
            transformed_str = str_
            transform_calls = []
        elif which_conversion == 0x01:
            transformed_str = str(str_)
            transform_calls = [FunctionCall(str, [str_], res=transformed_str)]
        elif which_conversion == 0x02:
            transformed_str = repr(str_)
            transform_calls = [FunctionCall(repr, [str_], res=transformed_str)]
        elif which_conversion == 0x03:
            transformed_str = ascii(str_)
            transform_calls = [
                FunctionCall(ascii, [str_], res=transformed_str)
            ]
        else:
            raise NotImplementedError()
        return lambda post_stack, _: transform_calls + (
            [
                FunctionCall(
                    format,
                    [transformed_str, format_spec],
                    res=post_stack[-1],
                )
            ]
        )
    raise NotImplementedError()


def all_code_objects(code: CodeType) -> Iterable[CodeType]:
    """
    Return all code objects from a source code object. This will include those used within it, such as nested functions.
    """
    yield code
    for const in code.co_consts:
        if isinstance(const, CodeType):
            yield from all_code_objects(const)
