import ast


class SourceGiver:
    def transform(self, nodes: ast.Module) -> None:
        """
        This call should only happen once asttoken has run its magic
        and embellished the ast with tokens and line numbers.
        At that point, all this function will do is use those tokens to
        figure out end_lineno and end_col_offset for every node in the tree
        """
        node: ast.AST
        # TODO check if the ast type is a Module instead of simply relying on mypy
        for node in ast.walk(nodes):
            if not hasattr(node, "lineno"):
                continue

            if hasattr(node, "last_token"):
                node.end_lineno = node.last_token.end[0]  # type: ignore
                node.end_col_offset = node.last_token.end[1]  # type: ignore
                # if isinstance(node, ast.ListComp):
                node.col_offset = node.first_token.start[1]  # type: ignore
