from dataclasses import dataclass, field
from typing import List, Optional

from lineapy.data.types import ControlNode, LineaID


@dataclass
class ControlFlowTracker:

    # When dealing with control flow, we might encounter nested structures like:
    #
    # if <condition>:
    #   if <another condition>:
    #       <body>
    # else:
    #   <else body>
    #
    # To deal with such recursive structures, we maintain a stack like data
    # structure as is popular in compilers as
    # (a) it ensures we are able to keep track of the outer `if` while dealing
    #     with the inner `if`
    # (b) we do not need to rewrite all existing node_visitor functions to
    #     account for the additional bookkeeping, as would be the case in
    #     functional coding
    #
    # Whenever we encounter a new control flow node, like `if` in the example
    # above, we call push_node() below to add the node to the stack.
    # While the control flow node is in scope, it is kept on the stack, and for
    # all other nodes created in that duration, we simply call the method
    # current_control_dependency (which returns the innermost control flow node
    # currently in scope) for marking out control dependencies of each newly
    # generated node.
    # When the control flow node goes out of scope, we call pop_node() to pop
    # the control flow node from the stack, so that nodes generated in the
    # future do not depend on the popped control flow node.

    control_flow_node_stack: List[LineaID] = field(default_factory=list)

    def push_node(self, control_node_id: LineaID) -> None:
        self.control_flow_node_stack.append(control_node_id)

    def pop_node(self) -> LineaID:
        return self.control_flow_node_stack.pop()

    def current_control_dependency(self) -> Optional[LineaID]:
        return (
            self.control_flow_node_stack[-1]
            if len(self.control_flow_node_stack) > 0
            else None
        )


@dataclass
class ControlFlowContext:

    # Wrapper used for the ControlFlowTracker. This class is used as a context
    # manager to ensure the programmer does not need to remember to call
    # pop_node for every push_node in the ControlFlowTracker above.

    control_node: ControlNode
    control_flow_tracker: ControlFlowTracker

    def __enter__(self) -> ControlNode:
        self.control_flow_tracker.push_node(self.control_node.id)
        return self.control_node

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.control_flow_tracker.pop_node()
