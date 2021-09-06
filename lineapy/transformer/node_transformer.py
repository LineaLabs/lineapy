import ast
from typing import Optional

from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.transformer import LINEAPY_TRACER_NAME


def turn_none_to_empty_str(a: Optional[str]):
    if not a:
        return ""
    return a


class NodeTransformer(ast.NodeTransformer):
    """
    Notes:
    - Need to be careful about the order by which these calls are invoked so that the transformation do not get called more than once.
    """

    def __init__(self, source: str):
        self.source = source

    def _get_code_from_node(self, node):
        code = """{}""".format(ast.get_source_segment(self.source, node))
        return code

    def visit_Import(self, node):
        """
        similar to import from, slightly different class syntax
        """
        # FIXME: the code will have to de-duplicate or we'd have to create our own code....
        result = []
        code = self._get_code_from_node(node)
        for lib in node.names:
            result.append(
                ast.Expr(
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                            attr="trace_import",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(arg="name", value=ast.Constant(value=lib.name)),
                            ast.keyword(arg="code", value=ast.Constant(value=code)),
                            ast.keyword(
                                arg="alias", value=ast.Constant(value=lib.asname)
                            ),
                        ],
                    )
                )
            )
        return result

    def visit_ImportFrom(self, node):
        """
        pretty simple, no recursion
        """
        keys = []
        values = []
        for alias in node.names:
            keys.append(ast.Constant(value=alias.name))
            # needed to do this empty string business because of some issue with pydantic
            values.append(ast.Constant(value=turn_none_to_empty_str(alias.asname)))

        code = self._get_code_from_node(node)
        result = ast.Expr(
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                    attr=Tracer.TRACE_IMPORT,
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(value=node.module)),
                    ast.keyword(arg="code", value=ast.Constant(value=code)),
                    ast.keyword(
                        arg="attributes", value=ast.Dict(keys=keys, values=values)
                    ),
                ],
            )
        )
        return result

    def visit_Call(self, node) -> ast.Call:
        """
        TODO: figure out what to do with the other type of expressions
        TODO: find function_module
        """
        code = self._get_code_from_node(node)
        argument_nodes = [self.visit(arg) for arg in node.args]
        result = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.TRACE_CALL,
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(
                    arg="function_name",
                    value=ast.Constant(value=node.func.id),
                ),
                ast.keyword(
                    arg="code",
                    value=ast.Constant(value=code),
                ),
                ast.keyword(
                    arg="arguments",
                    value=ast.List(elts=argument_nodes),
                ),
            ],
        )
        return result

    def visit_Assign(self, node: ast.Assign) -> ast.Expr:
        """
        Note
        - some code segments subsume the others
        - need to pad with expr to make astor happy
        https://stackoverflow.com/questions/49646402/function-isnt-added-to-new-line-when-adding-node-to-ast-in-python
        """
        code = self._get_code_from_node(node)
        if type(node.targets[0]) is not ast.Name:
            raise NotImplementedError("other assignment types are not supported")
        variable_name = node.targets[0].id  # type: ignore
        call_ast = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=LINEAPY_TRACER_NAME, ctx=ast.Load()),
                attr=Tracer.TRACE_ASSIGN,
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(
                    arg="variable_name",
                    value=ast.Constant(value=variable_name),
                ),
                ast.keyword(
                    arg="value_node",
                    value=self.visit(node.value),
                ),
                ast.keyword(
                    arg="code",
                    value=ast.Constant(value=code),
                ),
            ],
        )
        result = ast.Expr(value=call_ast)
        return result
