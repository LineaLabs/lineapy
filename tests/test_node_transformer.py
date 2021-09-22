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

    @pytest.mark.parametrize("code", ("a = 1", "a = foo"))
    def test_visit_assign(self, execute, code):
        execute(
            code,
            exec_transformed_xfail="evaling transformed with undefined var in list fails",
        )

    @pytest.mark.parametrize("code", ("[1, 2]", "[1, a]"))
    def test_visit_list(self, execute, code):
        execute(
            code,
            exec_transformed_xfail="evaling transformed with undefined var in list fails",
        )

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
            "@",
        ),
    )
    def test_visit_binop(self, execute, op):
        execute(
            f"a {op} 1",
            exec_transformed_xfail="cant eval undefined var in transform",
        )

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
            f"a {op} b",
            exec_transformed_xfail="cant eval undefined var in transform",
        )

    @pytest.mark.parametrize(
        "code",
        (
            "ls[0]",
            "ls[a]",
            "ls[1:2]",
            "ls[1:a]",
            "ls[[1,2]]",
        ),
    )
    def test_visit_subscript(self, execute, code):
        execute(
            code,
            exec_transformed_xfail="cant eval undefined var in transform",
        )

    @pytest.mark.parametrize(
        "code",
        (
            "ls[0] = 1",
            "ls[a] = b",
            "ls[1:2] = [1]",
            "ls[1:a] = [b]",
            "ls[[1,2]] = [1,2]",
        ),
    )
    def test_visit_assign_subscript(self, execute, code):
        execute(
            code,
            exec_transformed_xfail="cant eval undefined var in transform",
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
            code,
            exec_transformed_xfail="cant eval undefined var in transform",
        )

    def test_headless_literal(self, execute):
        execute("1")

    def test_headless_variable(self, execute):
        execute(
            "b",
            exec_transformed_xfail="evaling transformed with undefined var fails",
        )

    def test_literal_assignment(self, execute):
        execute("b = 2")
