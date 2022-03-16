from __future__ import annotations

from contextlib import contextmanager
from dataclasses import InitVar, dataclass, field
from dis import Instruction, get_instructions
from sys import settrace
from types import CodeType
from typing import Dict, Iterable, Iterator, List

from rich.console import Console
from rich.table import Table

from lineapy.system_tracing._op_stack import OpStack
from lineapy.system_tracing.function_call import FunctionCall


@contextmanager
def record_function_calls(code: CodeType) -> Iterator[List[FunctionCall]]:
    # TODO: use tracing
    function_calls: List[FunctionCall] = []

    try:
        trace_fn = TraceFunc(code)
        settrace(trace_fn)
        yield function_calls
    finally:
        settrace(None)
        # trace_fn.visualize()


@dataclass
class TraceFunc:

    code: InitVar[CodeType]
    # Mapping of each code object that was passed in to its instructions, by offset.
    code_to_offset_to_instruction: Dict[
        CodeType, Dict[int, Instruction]
    ] = field(init=False)

    table: Table = field(
        default_factory=lambda: Table(title="Bytecode Evaluations")
    )

    def __post_init__(self, code):
        self.code_to_offset_to_instruction = {
            code: {i.offset: i for i in get_instructions(code)}
            for code in all_code_objects(code)
        }

        self.table.add_column("Name", justify="right", no_wrap=True)
        self.table.add_column(
            "Arg",
            justify="right",
        )
        self.table.add_column(
            "Stack",
        )

    def visualize(self):
        console = Console()
        console.print(self.table)

    def __call__(self, frame, event, arg):
        if frame.f_code not in self.code_to_offset_to_instruction:
            return self
        frame.f_trace_opcodes = True
        if event != "opcode":
            return self

        offset_to_instructions = self.code_to_offset_to_instruction[
            frame.f_code
        ]

        instruction = offset_to_instructions[frame.f_lasti]

        op_stack = OpStack(frame)

        self.table.add_row(
            instruction.opname,
            instruction.argrepr,
        )
        return self


def all_code_objects(code: CodeType) -> Iterable[CodeType]:
    yield code
    for const in code.co_consts:
        if isinstance(const, CodeType):
            yield from all_code_objects(const)
