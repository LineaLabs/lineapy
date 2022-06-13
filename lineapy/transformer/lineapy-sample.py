from lineapy.transformer.node_transformer import NodeTransformer


class LineaCallNode(CallNode):
    # might not be used directly yet.
    module_name: str #lineapy.api.api or lineapy.api.api_classes type of string
    function_name: str # save/get type of string
    artifact_name:str
    artifact_version: str
    execution_count:int = 0



class lapi():
    def __init__(self):
        #initialize tracer here
        db: RelationalLineaDB
        executor: executor = Executor(db)
        ExecutionContext: ExecutionContext
        tracer: Tracer = Tracer(executor, db)
        self.transformers = [ LineaCallTransformer(tracer), NodeTransformer(tracer) ]

    def transform():
    # get the contents of orig transform here.
    try:
        tree = ast.parse(
            code,
            str(get_location_path(location).absolute()),
        )
    except SyntaxError as e:
        raise UserException(e, RemoveFrames(2))
    if sys.version_info < (3, 8):
        from asttokens import ASTTokens

        from lineapy.transformer.source_giver import SourceGiverfor

        # if python version is 3.7 or below, we need to run the source_giver
        # to add the end_lineno's to the nodes. We do this in two steps - first
        # the asttoken lib does its thing and adds tokens to the nodes
        # and then we swoop in and copy the end_lineno from the tokens
        # and claim credit for their hard work
        ASTTokens(code, parse=False, tree=tree)
        SourceGiver().transform(tree)

    #tree is of module type - atleast for scripts - check for jupyter
    for node in tree.body:
        for trans in self.transformer:
            res = trans.visit(node)
            # or some other statement to figure out whether the node is properly processed or not
            if res is not None:
                node = res # swap the node with the output of previous transformer and use that for further calls
        # if no transformers can process it - we'll change node transformer to not throw not implemented exception
        # so that it can be extended and move it here.
        if isinstance(node, ast.Any):
            raise NotImplementedError(
                f"Don't know how to transform {type(node).__name__}"
            )
    
    db.commit()
    return self.transformers[-1].last_statement_result


class LineaCallTransformer(NodeTransformer):
    def visit_Call(self, node):
        # check if function is lineapy-ish
        # we have access to tracer here. so we can simply get the function from the
        # tracer.variable_name_to_node dict and can get the orig object from there.
        # if the object does not exist, simple pass along and let node_transformer handle it
        # if the object does exist, get it and check its module/function name and if 
        # it is a lineapy function, EXECUTE IT without involving the executor and make 
        # it into a LineaCallNode and pass it along to the next transformer.
        # this new node should still be made part of the tree, so we will pass it along 
        # for node transformer to process it and add to the graph.

class NodeTransformer(NodeTransformer):
    # add new function
    def visit_LineaCallNode(self, node):
        # should never be passed to executor since it already should be executed.
        # execute_call will not be called.

        # this instead can be used to do other stuff like count executions 
        # for the same graph. it will look up executions by artifact_name, artifact_version, 
        # (or alternately node_id bcause it was already executed in lineapytransformer) and 
        # up the execution count by 1
