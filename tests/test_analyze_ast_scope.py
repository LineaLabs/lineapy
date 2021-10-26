import pytest

from lineapy.transformer.analyze_scope import Scope, analyze_code_scope

ParameterType = list[tuple[str, Scope]]

ASSIGN_EXAMPLES: ParameterType = [
    ("a=b", Scope(loaded={"b"}, stored={"a"})),
    ("a+=b", Scope(loaded={"a", "b"}, stored={"a"})),
]

IF_EXAMPLES: ParameterType = [
    # including print for now, and we can decide if we don't want it to be kept
    ("if a:\n  b=1\n  print(b)", Scope(loaded={"a", "print"}, stored={"b"})),
    (
        "if a:\n  print(b)\n  b=1",
        Scope(loaded={"a", "b", "print"}, stored={"b"}),
    ),
    ("if a:\n  print(b)", Scope(loaded={"a", "b", "print"})),
    (
        "if a:\n  c=1\nelif b==1:\n  d=2\nelse:\n  print(c)",
        Scope(loaded={"a", "b", "c", "print"}, stored={"d", "c"}),
    ),
]

LIST_COMP_EXAMPLES: ParameterType = [
    ("[x for x in xx]", Scope(loaded={"xx"})),
    ("[x for x in xx if y]", Scope(loaded={"xx", "y"})),
    ("[x for xx in xxx for x in xx]", Scope(loaded={"xxx"})),
    # Verify that conditionals only end up having unbound variables
    # if they are not defined in one of their parent scopes.
    ("[x for xx in xxx if y for x in xx]", Scope(loaded={"xxx", "y"})),
    ("[x for xx in xxx for x in xx if x]", Scope(loaded={"xxx"})),
    ("x.y", Scope(loaded={"x"})),
]

FOR_EXAMPLES: ParameterType = [
    (
        "for a in range(5):\n  print(a)",
        Scope(loaded={"print", "range"}, stored={"a"}),
    ),
    (
        "for a in range(5):\n  b+=a",
        Scope(loaded={"range", "b"}, stored={"b", "a"}),
    ),
    (
        "for a in range(c):\n  h = a",
        Scope(loaded={"range", "c"}, stored={"h", "a"}),
    ),
    (
        "for a in [1,2]:\n  print(a+b)",
        Scope(loaded={"print", "b"}, stored={"a"}),
    ),
]

FUNCTION_SCOPE_EXAMPLES: ParameterType = [
    (
        "def my_function():\n  global a\n  a = math.factorial(5)",
        Scope(loaded={"math"}, stored={"a", "my_function"}),
    ),
    ("def foo(a):\n  print(a)", Scope(loaded={"print"}, stored={"foo"})),
    ("def foo():\n  print(a)", Scope(loaded={"a", "print"}, stored={"foo"})),
    ("def foo():\n  global a\n  a=1\n  b=2", Scope(stored={"foo", "a"})),
    ("def foo():\n  global a\n  a=1\n  b=2", Scope(stored={"foo", "a"})),
]

LAMBDA_EXAMPLES: ParameterType = [
    (
        """lambda x: x + a""",
        Scope(loaded={"a"}),
    )
]


def _helper(code: str, scope: Scope):
    # a = ast.parse(code).body[0]
    assert analyze_code_scope(code) == scope, code


@pytest.mark.parametrize("code,scope", FUNCTION_SCOPE_EXAMPLES)
def test_function(code: str, scope: Scope):
    _helper(code, scope)


@pytest.mark.parametrize("code,scope", ASSIGN_EXAMPLES)
def test_assign(code: str, scope: Scope):
    _helper(code, scope)


@pytest.mark.parametrize("code,scope", FOR_EXAMPLES)
def test_for_loop(code: str, scope: Scope):
    _helper(code, scope)


@pytest.mark.parametrize("code,scope", IF_EXAMPLES)
def test_if(code: str, scope: Scope):
    _helper(code, scope)


@pytest.mark.parametrize("code,scope", LIST_COMP_EXAMPLES)
def test_list_comprehension(code: str, scope: Scope):
    _helper(code, scope)


@pytest.mark.parametrize("code,scope", LAMBDA_EXAMPLES)
def test_lambda(code: str, scope: Scope):
    _helper(code, scope)
