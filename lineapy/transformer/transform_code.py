import ast
import logging
import sys
from typing import Optional

from lineapy.data.types import Node, SourceCodeLocation
from lineapy.editors.ipython_cell_storage import get_location_path
from lineapy.exceptions.user_exception import RemoveFrames, UserException
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.node_transformer import NodeTransformer

logger = logging.getLogger(__name__)


def transform(
    code: str, location: SourceCodeLocation, tracer: Tracer
) -> Optional[Node]:
    """
    Traces the given code, executing it and writing the results to the DB.

    It returns the node corresponding to the last statement in the code,
    if it exists.
    """

    transformers = [
        NodeTransformer(code, location, tracer),
    ]
    try:
        tree = ast.parse(
            code,
            str(get_location_path(location).absolute()),
        )
    except SyntaxError as e:
        raise UserException(e, RemoveFrames(2))
    if sys.version_info < (3, 8):
        from asttokens import ASTTokens

        from lineapy.transformer.source_giver import SourceGiver

        # if python version is 3.7 or below, we need to run the source_giver
        # to add the end_lineno's to the nodes. We do this in two steps - first
        # the asttoken lib does its thing and adds tokens to the nodes
        # and then we swoop in and copy the end_lineno from the tokens
        # and claim credit for their hard work
        ASTTokens(code, parse=False, tree=tree)
        SourceGiver().transform(tree)

    if len(tree.body) > 0:
        for stmt in tree.body:
            res = None
            for trans in transformers:
                # print(ast.dump(stmt))
                res = trans.visit(stmt)
                # or some other statement to figure out whether the node is properly processed or not
                if res is not None:
                    stmt = res  # swap the node with the output of previous transformer and use that for further calls
            # if no transformers can process it - we'll change node transformer to not throw not implemented exception
            # so that it can be extended and move it here.
            if isinstance(res, ast.AST):
                raise NotImplementedError(
                    f"Don't know how to transform {type(stmt).__name__}"
                )
            # FIXME - this is needed for jupyter, will revisit this after prototype phase.
            last_statement_result = res  # type: ignore
        # replaced by the for loop above
        # node_transformer.visit(tree)

        tracer.db.commit()
        return last_statement_result  # type: ignore

    return None
