"""
The goal of this module is to go from bytecode -> CFG -> Bytecode,
to allow us to do dependency analysis and various other things at the CFG level.
"""

from dis import dis
import bytecode
from dataclasses import dataclass

__all__ = ["ControlFlowGraph"]


@dataclass
class ControlFlowGraph:
    @classmethod
    def from_bytecode(bytecode):
        """
        Convert a bytecode object into a CFG.
        """
        raise NotImplementedError


def p(code):
    dis.dis(code)
    print(
        bytecode.dump_bytecode(
            bytecode.ControlFlowGraph.from_bytecode(
                bytecode.Bytecode.from_code(compile(code, "None", "exec"))
            )
        )
    )
