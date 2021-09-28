from lineapy.data.types import SessionType
import pytest


class TestNodeTransformer:
    @pytest.mark.parametrize("code", ("import pandas", "import pandas as pd"))
    def test_visit_import(self, execute, code):
        execute(code)

    def test_visit_importfrom(self, execute):
        execute("from math import pow as power")

    @pytest.mark.parametrize("code", ("foo()", "foo(1, 2)"))
    def test_visit_call(self, execute, code):
        execute(code, session_type=SessionType.STATIC)

    def test_visit_call_kwargs(self, execute):
        call_with_keyword_args = "foo(b=1)"
        execute(call_with_keyword_args, session_type=SessionType.STATIC)

    @pytest.mark.parametrize("code", ("a = 1", "b=2\na = b"))
    def test_visit_assign(self, execute, code):
        execute(code)

    @pytest.mark.parametrize("code", ("[1, 2]", "a=3\n[1, a]"))
    @pytest.mark.xfail
    def test_visit_list(self, execute, code):
        execute(code)

    @pytest.mark.parametrize(
        "op",
        (
            "+",
            "-",
            "*",
            "/",
            "//",
            "%",
            "**",
            "<<",
            ">>",
            "|",
            "^",
            "&",
            pytest.param("@", marks=pytest.mark.xfail()),
        ),
    )
    def test_visit_binop(self, execute, op):
        execute(
            f"a=1\na {op} 1",
        )

    @pytest.mark.xfail
    @pytest.mark.parametrize(
        "op",
        (
            "==",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
            "is",
            "is not",
            "in",
            "not in",
            "<= c <",
        ),
    )
    def test_visit_compare(self, execute, op):
        execute(
            f"a=1\nb=2\na {op} b",
        )

    @pytest.mark.parametrize(
        "code",
        (
            "ls[0]",
            "ls[a]",
            "ls[1:2]",
            "ls[1:a]",
            pytest.param("ls[[1,2]]", marks=pytest.mark.xfail()),
        ),
    )
    def test_visit_subscript(self, execute, code):
        execute(
            "ls=[1,2,3]\na=1\n" + code,
        )

    @pytest.mark.parametrize(
        "code",
        (
            "ls[0] = 1",
            "ls[a] = b",
            "ls[1:2] = [1]",
            "ls[1:a] = [b]",
            pytest.param("ls[[1,2]] = [1,2]", marks=pytest.mark.xfail()),
        ),
    )
    def test_visit_assign_subscript(self, execute, code):
        execute(
            "ls=[1,2,3]\na=1\nb=4\n" + code,
        )

    @pytest.mark.parametrize(
        "code",
        (
            "lineapy.linea_publish(a)",
            "lineapy.linea_publish(a, 'test artifact')",
        ),
    )
    def test_linea_publish_visit_call(self, execute, code):
        execute(
            "a=1\n" + code,
        )

    def test_headless_literal(self, execute):
        execute("1")

    def test_headless_variable(self, execute):
        execute("b=1\nb")

    def test_literal_assignment(self, execute):
        execute("b = 2")
