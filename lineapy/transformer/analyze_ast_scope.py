from __future__ import annotations

"""
Utility for analyzing python AST scoping.
"""
import ast
from dataclasses import dataclass, field
import astpretty


__all__ = ["Scope", "analyze_ast_scope"]


def analyze_ast_scope(a: ast.AST) -> Scope:
    return ScopeNodeTransformer().visit(a)


@dataclass
class Scope:
    # Names that are stored/set in this scope
    stored: set[str] = field(default_factory=set)
    # Names that are loaded/accessed in this scope
    loaded: set[str] = field(default_factory=set)

    def record_child(self, child: Scope) -> None:
        """
        Combine with a child node.

        Anything the child node has loaded, that we don't have stored,
        add to our loaded
        """
        self.loaded |= child.loaded - self.stored


def unify(*scopes: Scope) -> Scope:
    """
    Unify multiple scopes into one, by taking the union of all the their variables
    and resolving any variables it tries to load from those that it has stored.
    """
    s = Scope(
        stored=set.union(*(s.stored for s in scopes)),
        loaded=set.union(*(s.loaded for s in scopes)),
    )
    s.loaded -= s.stored
    return s


class ScopeNodeTransformer(ast.NodeTransformer):
    """
    A node transformer which should return a Scope if it can figure it out
    for the given node.
    """

    def generic_visit(self, node: ast.AST) -> ast.AST:
        raise NotImplementedError(
            f"Don't know how to analyze scope for node type {type(node).__name__}:\n\n{astpretty.pformat(node)}"
        )

    def visit_Expr(self, node: ast.Expr) -> Scope:
        return self.visit(node.value)

    def visit_ListComp(self, node: ast.ListComp) -> Scope:
        inner_scope = self.visit(node.elt)
        # Start with most inner loop first
        for gen in reversed(node.generators):
            # Any values its setting,
            target = self.visit(gen.target)
            iter_ = self.visit(gen.iter)
            ifs = [self.visit(i) for i in gen.ifs]
            parent_scope = unify(target, iter_, *ifs)
            parent_scope.record_child(inner_scope)
            inner_scope = parent_scope

        # The list comprehension itself is a scope, so remove any variables
        # it sets when returning
        return Scope(loaded=inner_scope.loaded)

    def visit_Name(self, node: ast.Name) -> Scope:
        if isinstance(node.ctx, ast.Load):
            return Scope(loaded={node.id})
        elif isinstance(node.ctx, ast.Store):
            return Scope(stored={node.id})
        raise NotImplementedError("deleting not supported yet")

    def visit_BinOp(self, node: ast.BinOp) -> Scope:
        return unify(self.visit(node.left), self.visit(node.right))

    def visit_Constant(self, node: ast.Constant) -> Scope:
        return Scope()

    def visit_Call(self, node: ast.Call) -> Scope:
        return unify(
            self.visit(node.func),
            *(self.visit(arg) for arg in node.args),
        )
