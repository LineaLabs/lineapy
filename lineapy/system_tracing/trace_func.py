from __future__ import annotations

import operator
from dataclasses import InitVar, dataclass, field
from dis import Instruction, get_instructions
from types import CodeType
from typing import Callable, Dict, Iterable, List, Optional, Set, Union

from lineapy.system_tracing._op_stack import OpStack
from lineapy.system_tracing.function_call import FunctionCall

# This callback is saved when we have an operator that had some function call. We need to defer some of the processing until the next bytecode instruction loads,
# So that at the point, the return value will be in the stack and we can look at it.
# Called with the opstack and the next instruction offset
ReturnValueCallback = Optional[
    Callable[[OpStack, int], Optional[FunctionCall]]
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

    # If set, then the previous bytecode instruction had a function call, and during the next call, we should call
    # this function with the current stack to get the FunctionCall result.
    return_value_callback: ReturnValueCallback = field(default=None)

    def __post_init__(self, code):
        self.code_to_offset_to_instruction = {
            code: {i.offset: i for i in get_instructions(code)}
            for code in all_code_objects(code)
        }

    def __call__(self, frame, event, arg):
        # Exit early if the code object for this frame is not one of the code objects we want to trace
        if frame.f_code not in self.code_to_offset_to_instruction:
            return self

        # If it is one we want to trace, enable opcode tracing on it
        frame.f_trace_opcodes = True
        # If this is not an opcode event, ignore it
        if event != "opcode":
            return self

        # Lookup the instruction we currently have based on the code object as well as the offset in that object
        instruction = self.code_to_offset_to_instruction[frame.f_code][
            frame.f_lasti
        ]

        # Create an op stack around the frame so we can access the stack
        op_stack = OpStack(frame)

        # If during last instruction we had some function call that needs a return value, trigger the callback with the current
        # stack, so it can get the return value.
        if self.return_value_callback:
            function_call = self.return_value_callback(op_stack, frame.f_lasti)
            if function_call:
                self.function_calls.append(function_call)
            self.return_value_callback = None

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
            self.return_value_callback = possible_function_call
        # Otherwise, if we could resolve it fully now, add that to our function call
        elif possible_function_call:
            self.function_calls.append(possible_function_call)

        return self


# Bytecode operations that are not function calls
NOT_FUNCTION_CALLS = {
    "NOP",
    "POP_TOP",
    "COPY",
    "SWAP",
    #
    "LOAD_CONST",
    "LOAD_NAME",
    "RETURN_VALUE",
    "STORE_NAME",
    "JUMP_ABSOLUTE",
    "POP_BLOCK",
    "SETUP_LOOP",
}

UNARY_OPERATORS = {
    "UNARY_POSITIVE": operator.pos,
    "UNARY_NEGATIVE": operator.neg,
    "UNARY_NOT": operator.not_,
    "UNARY_INVERT": operator.inv,
    "GET_ITER": iter,
    # Generators not supported
    # GET_YIELD_FROM_ITER
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


def resolve_bytecode_execution(
    name: str, value: object, stack: OpStack, offset: int
) -> Union[ReturnValueCallback, FunctionCall]:
    """
    Returns a function call corresponding to the bytecode executing on the current stack.
    """
    if name in NOT_FUNCTION_CALLS:
        return None
    if name in UNARY_OPERATORS:
        args = [stack[-1]]
        return lambda post_stack, _: FunctionCall(
            UNARY_OPERATORS[name], args, {}, post_stack[-1]
        )
    if name in BINARY_OPERATIONS:
        args = [stack[-2], stack[-1]]
        return lambda post_stack, _: FunctionCall(
            BINARY_OPERATIONS[name], args, {}, post_stack[-1]
        )
    if name == "FOR_ITER":
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
    # TODO: Add support for more bytecode operations!
    raise NotImplementedError()


def all_code_objects(code: CodeType) -> Iterable[CodeType]:
    """
    Return all code objects from a source code object. This will include those used within it, such as nested functions.
    """
    yield code
    for const in code.co_consts:
        if isinstance(const, CodeType):
            yield from all_code_objects(const)
