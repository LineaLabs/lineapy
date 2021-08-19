from lineapy.data.types import Node, NodeType

# right now it's just a simple function that returns true if the callnode has an assignment, but in the future we should definitely add more logic


def caching_decider(node: Node):
    if node.node_type == NodeType.CallNode:
        if hasattr(node, "assigned_variable_name"):
            return True
    return False
