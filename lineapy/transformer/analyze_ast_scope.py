from __future__ import annotations
from typing import List

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
    """
    stored follows the ast convention of newly defined variables; similarly,
      loaded is for the ones accessed.
    """

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

    def record_sibling(self, sibling: Scope) -> None:
        """
        Combine with the next sibling in this block. For example, if you have
        two statements in a block, `a; b`, then get the scope of `a` and `b` and
        then call `a_scope.record_sibling(b_scope)`.

        It is similar to record_child, except the stores scopes are also added
        whereas in record_child, they are not recorded.
        """
        # Mark anything as loaded, that the current scope does not
        # have stored
        self.loaded |= sibling.loaded - self.stored
        self.stored |= sibling.stored


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

    The general strategy is to make sure that we resolve the variables that
      are created within the block.
    """

    def generic_visit(self, node: ast.AST) -> Scope:  # type: ignore
        raise NotImplementedError(
            "Don't know how to analyze scope for node type"
            f" {type(node).__name__}:\n\n{astpretty.pformat(node)}"
        )

    def visit_Expr(self, node: ast.Expr) -> Scope:
        return self.visit(node.value)

    def visit_Assign(self, node: ast.Assign) -> Scope:
        scopes = [self.visit(t) for t in node.targets]
        return unify(*scopes)

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

    def visit_If(self, node: ast.If) -> Scope:
        # this basically reduces to the generic case
        # nothing is defined in test, so the scope should just be reading
        current_scope = self.visit(node.test)

        for expressions in [node.body, node.orelse]:
            # For each block of expressions, iterate over each expression
            # and update the inner scope. Then, once its finished,
            # Add any variables its looking for to our parent scope
            inner_scope = Scope()
            for e in expressions:
                inner_scope.record_sibling(self.visit(e))
            current_scope.record_child(inner_scope)
        return Scope(loaded=current_scope.loaded)

    def visit_Compare(self, node: ast.Compare) -> Scope:
        scopes = [self.visit(node.left)]
        for i in range(len(node.ops)):
            scopes.append(self.visit(node.comparators[i]))
        return unify(*scopes)

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

    def visit_Attribute(self, node: ast.Attribute) -> Scope:
        return self.visit(node.value)
