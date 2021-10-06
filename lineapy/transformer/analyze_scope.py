"""
Utility for analyzing python AST scoping.
"""

from __future__ import annotations
from typing import List, Union
import types
import dis
from dataclasses import dataclass, field


__all__ = ["Scope", "analyze_code_scope"]


def analyze_code_scope(code: str):
    """
    TODO: it's probably more robust to use ast rather than string, but not
          sure how to connect. Currently there is some weirdness
          ast: ast.AST
    """
    return ByteCodeTransformer().get_scope(code)


def unify(*scopes: Scope) -> Scope:
    """
    merges the scopes
    """
    s = Scope(
        stored=set.union(*(s.stored for s in scopes)),
        loaded=set.union(*(s.loaded for s in scopes)),
    )
    return s


@dataclass
class Scope:
    """
    stored follows the ast convention of newly defined variables; similarly,
      loaded is for the ones accessed.
    """

    # Names that are stored/set in this scope
    stored: set[str] = field(default_factory=set)
    # Names that are loaded/accessed in this scope
    loaded: set[str] = field(default_factory=set)


# for the ones in override, they can bypass the function scope
GLOBAL_STORE = {"STORE_GLOBAL"}
STORE = {"STORE_NAME"}.union(GLOBAL_STORE)
# Note that for internally defined variables are accessed as "LOAD_FAST"
LOAD = ["LOAD_GLOBAL", "LOAD_NAME"]
REST_SCOPE = ["POP_JUMP_IF_FALSE", "JUMP_FORWARD"]


def iterate_through(bytecode, global_scope: Scope):
    current_scope = Scope()
    for instr in bytecode:
        if isinstance(instr.argval, types.CodeType):
            current_scope = iterate_through(
                dis.Bytecode(instr.argval), global_scope
            )
            global_scope = unify(current_scope, global_scope)
        elif instr.opname in STORE:
            current_scope.stored.add(instr.argrepr)
        elif (
            instr.opname in LOAD and instr.argrepr not in current_scope.stored
        ):
            current_scope.loaded.add(instr.argrepr)
        elif instr.opname in GLOBAL_STORE:
            global_scope.stored.add(instr.argrepr)
        elif instr.opname in REST_SCOPE:
            # FIXME: this is a hack that only works for limited scope right now
            global_scope = unify(current_scope, global_scope)
            current_scope = Scope()

    return unify(current_scope, global_scope)


class ByteCodeTransformer:
    def get_scope(self, code: str) -> Scope:
        global_scope = Scope()
        bytecode = dis.Bytecode(code)
        return iterate_through(bytecode, global_scope)
