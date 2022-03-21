from __future__ import annotations

import operator
from dataclasses import InitVar, dataclass, field
from dis import Instruction, get_instructions
from sys import version_info
from types import CodeType
from typing import Any, Callable, Dict, Iterable, List, Set, Union

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

    # Mapping of each code object that was passed in to its instructions, by offset, so we can quicjly look up what instruction we are looking at
    code_to_offset_to_instruction: Dict[
        CodeType, Dict[int, Instruction]
    ] = field(init=False)

    # If set for the code object, then the previous bytecode instruction in the frame for that code object had a function call, and during the next call, we should call
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
        code = frame.f_code
        # Exit early if the code object for this frame is not one of the code objects we want to trace
        if frame.f_code not in self.code_to_offset_to_instruction:
            return self

        # If it is one we want to trace, enable opcode tracing on it
        frame.f_trace_opcodes = True
        # If this is not an opcode event, ignore it
        if event != "opcode":
            return self

        offset = frame.f_lasti
        # Lookup the instruction we currently have based on the code object as well as the offset in that object
        instruction = self.code_to_offset_to_instruction[code][offset]
        # We want to see the name and the arg for the actual instruction, not the arg, so increment until we get to that
        while instruction.opname == "EXTENDED_ARG":
            offset += 2
            instruction = self.code_to_offset_to_instruction[code][offset]

        # Create an op stack around the frame so we can access the stack
        op_stack = OpStack(frame)

        # If during last instruction we had some function call that needs a return value, trigger the callback with the current
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
                instruction.opname, instruction.argval, op_stack, frame.f_lasti
            )
        except NotImplementedError:
            self.not_implemented_ops.add(instruction.opname)
            possible_function_call = None
        # If resolving the function call needs to be deferred until after we have the return value, save teh callback
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
    #
    "JUMP_ABSOLUTE",
    "POP_BLOCK",
    "SETUP_LOOP",
    "MAKE_FUNCTION",
    "LOAD_FAST",
    "STORE_FAST",
    "DUP_TOP",
    "JUMP_FORWARD",
    "POP_JUMP_IF_TRUE",
    "RAISE_VARARGS",
}
# TODO: When seeing most recent value, check stack we are in.

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

##
# Defer supprting imports until after imports are turned into call nodes
##
# IMPORT_STARIMPORT_STAR

##
# Generator functions not supported
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


def resolve_bytecode_execution(
    name: str, value: Any, stack: OpStack, offset: int
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
            UNARY_OPERATORS[name], args, {}, post_stack[-1]
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
        # TOS is an `iterator`.  Call its `__next__` method.  If
        # this yields a new value, push it on the stack (leaving the iterator below
        # it).  If the iterator indicates it is exhausted, TOS is popped, and the byte
        # code counter is incremented by *delta*.
        args = [stack[-1]]

        # If the current instruction is the next one (i.e. the offset has increased by 2), then we didn't jump,
        # meaning the iterator was not exhausted. Otherwise, we did jump, and it was, so don't add a function call for this.
        # TODO: We don't support function calls which end in exceptions currently, if/when we do, we need to update this
        return (
            lambda post_stack, post_offset: FunctionCall(
                next, args, {}, post_stack[-1]
            )
            if post_offset == offset + 2
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
        set_ = stack[-value - 1]
        arg = stack[-1]
        method = getattr(set_, "add")
        # Translate method call to getitem followed by function call, to match AST behavior
        return [
            FunctionCall(getattr, [set_, "add"], res=method),
            FunctionCall(method, [arg]),
        ]
    if name == "LIST_APPEND":
        # Calls `list.append(TOS1[-i], TOS)`.  Used to implement list comprehensions.
        list_ = stack[-value - 1]
        arg = stack[-1]
        method = getattr(list_, "append")
        return [
            FunctionCall(getattr, [list_, "append"], res=method),
            FunctionCall(method, [arg]),
        ]
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

        count_left = value % 256
        count_right = value >> 8

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

    if name == "BUILD_MAP":
        #    Pushes a new dictionary object onto the stack.  Pops ``2 * count`` items
        #    so that the dictionary holds *count* entries:
        #    ``{..., TOS3: TOS2, TOS1: TOS}``.
        from lineapy.utils.lineabuiltins import l_dict, l_tuple

        args = [(stack[-i * 2 - 2], stack[-i * 2 - 1]) for i in range(value)]
        args.reverse()

        return lambda post_stack, stack_offset: [
            FunctionCall(l_tuple, [k, v], res=(k, v)) for k, v in args
        ] + [FunctionCall(l_dict, args, res=post_stack[-1])]
    # TODO: Add support for more bytecode operations.
    # Adding in sequence from dis docs in Python.

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
        enter_fn = getattr(x, "__enter__")
        return lambda post_stack, _: [
            FunctionCall(getattr, [x, "__exit__"], res=post_stack[-2]),
            FunctionCall(getattr, [x, "__enter__"], res=enter_fn),
            FunctionCall(enter_fn, [], res=post_stack[-1]),
        ]

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
        return lambda post_stack, stack_offset: FunctionCall(
            fn, args, res=post_stack[-1]
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
