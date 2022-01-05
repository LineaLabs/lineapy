import ast


class SourceGiver:
    def __init__(self):
        pass

    def transform(self, nodes: ast.Module) -> None:
        """
        This call should only happen once asttoken has run its magic
        and embellished the ast with tokens and line numbers.
        At that point, all this function will do is use those tokens to
        figure out end_lineno and end_col_offset for every node in the tree

        If we do not want to depend on asttokens lib, use transform_inhouse which sucks
        btw because we didnt put enough effort into figuring out the end col offsets
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

    def transform_inhouse(self, nodes: ast.Module) -> None:
        curr_line_start: int = -1
        curr_line_offset: int = -1
        prev_line_start: int = -1
        prev_line_offset: int = -1
        prev_node = None
        node: ast.AST
        # TODO check if the ast type is a Module instead of simply relying on mypy
        for node in ast.walk(nodes):
            if not hasattr(node, "lineno"):
                continue

            curr_line_start = node.lineno
            curr_line_offset = node.col_offset
            if prev_node is not None:
                prev_node.end_lineno = max(  # type: ignore
                    prev_line_start, curr_line_start - 1
                )
                if prev_line_start == curr_line_start:
                    prev_node.end_col_offset = max(
                        prev_line_offset, curr_line_offset - 1
                    )
                else:
                    prev_node.end_col_offset = -1
            prev_node = node
            prev_line_start = curr_line_start
            prev_line_offset = curr_line_offset
