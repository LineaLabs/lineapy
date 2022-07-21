from lineapy.data.graph import Graph
from lineapy.data.types import CallNode, LineaID, LookupNode


def _is_import_node(graph: Graph, node_id: LineaID) -> bool:
    """
    Given node_id, check whether it is a CallNode doing module import
    """
    node = graph.get_node(node_id)
    if isinstance(node, CallNode) and hasattr(node, "function_id"):
        lookup_node_id = node.__dict__.get("function_id", None)
        if lookup_node_id is not None:
            lookup_node = graph.get_node(lookup_node_id)
            if isinstance(lookup_node, LookupNode):
                lookup_node_name = lookup_node.__dict__.get("name", "")
                return lookup_node_name in ["l_import", "getattr"]
    return False
