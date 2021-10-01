from lineapy.transformer.analyze_ast_scope import (
    analyze_ast_scope,
    Scope,
)
import pytest
import ast
import astpretty


IF_EXAMPLES: list[tuple[str, Scope]] = [
    # including print for now, and we can decide if we don't want it to be kept
    ("if a:\n  b=1\n  print(b)", Scope(loaded={"a", "print"})),
    ("if a:\n  print(b)", Scope(loaded={"a", "b", "print"})),
    (
        "if a:\n  c=1\nelif b==1:\n  d=2\nelse:\n  print(c)",
        Scope(loaded={"a", "b", "c", "print"}),
    ),
]

EXAMPLES: list[tuple[str, Scope]] = [
    ("[x for x in xx]", Scope(loaded={"xx"})),
    ("[x for x in xx if y]", Scope(loaded={"xx", "y"})),
    ("[x for xx in xxx for x in xx]", Scope(loaded={"xxx"})),
    # Verify that conditionals only end up having unbound variables
    # if they are not defined in one of their parent scopes.
    ("[x for xx in xxx if x for x in xx]", Scope(loaded={"xxx", "x"})),
    ("[x for xx in xxx for x in xx if x]", Scope(loaded={"xxx"})),
    ("x.y", Scope(loaded={"x"})),
]


@pytest.mark.parametrize("code,scope", IF_EXAMPLES)
def test_if(code: str, scope: Scope):
    a = ast.parse(code).body[0]
    assert analyze_ast_scope(a) == scope, astpretty.pformat(a)


@pytest.mark.parametrize("code,scope", EXAMPLES)
def test_list_comprehension(code: str, scope: Scope):
    a = ast.parse(code).body[0]
    assert analyze_ast_scope(a) == scope, astpretty.pformat(a)
