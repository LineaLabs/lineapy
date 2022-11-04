import ast
import logging
import sys
from pathlib import Path
from typing import List, Optional

from lineapy.data.types import Node, SourceCode, SourceCodeLocation
from lineapy.editors.ipython_cell_storage import get_location_path
from lineapy.exceptions.user_exception import RemoveFrames, UserException
from lineapy.instrumentation.tracer import Tracer
from lineapy.transformer.base_transformer import BaseTransformer
from lineapy.transformer.node_transformer import NodeTransformer
from lineapy.transformer.py37_transformer import Py37Transformer
from lineapy.transformer.py38_transformer import Py38Transformer
from lineapy.utils.utils import get_new_id

logger = logging.getLogger(__name__)


def transform(
    code: str, location: SourceCodeLocation, tracer: Tracer
) -> Optional[Node]:
    """
    Traces the given code, executing it and writing the results to the DB.

    It returns the node corresponding to the last statement in the code,
    if it exists.
    """

    # create sourcecode object and register source code to db
    src = SourceCode(id=get_new_id(), code=code, location=location)
    tracer.db.write_source_code(src)

    # defaults for executor that were set inside node transformer
    # Set __file__ to the pathname of the file
    if isinstance(location, Path):
        tracer.executor.module_file = str(location)

    # initialize the transformer IN ORDER of preference
    transformers: List[BaseTransformer] = []

    # python 3.7 handler
    if sys.version_info < (3, 8):
        transformers.append(Py37Transformer(src, tracer))

    # python 3.8 handler
    if sys.version_info < (3, 9):
        transformers.append(Py38Transformer(src, tracer))

    # newer conditional transformers
    # FIXME these done work so they have been removed for now
    # transformers.append(ConditionalTransformer(src, tracer))

    # main transformation handler
    transformers.append(NodeTransformer(src, tracer))

    # parse the usercode in preparation for visits
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

    # walk the parsed tree through every transformer in the list
    if len(tree.body) > 0:
        for stmt in tree.body:
            res = None
            for trans in transformers:

                res = trans.visit(stmt)
                # swap the node with the output of previous transformer and use that for further calls
                # or some other statement to figure out whether the node is properly processed or not
                if res is not None:
                    stmt = res
            # if no transformers can process it - we'll change node transformer to not throw not implemented exception
            # so that it can be extended and move it here.
            if isinstance(res, ast.AST):
                raise NotImplementedError(
                    f"Don't know how to transform {type(stmt).__name__}"
                )
            last_statement_result = res

        tracer.db.commit()
        return last_statement_result

    return None
