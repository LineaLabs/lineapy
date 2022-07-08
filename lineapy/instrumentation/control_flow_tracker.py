from dataclasses import dataclass, field
from typing import List, Optional

from lineapy.data.types import LineaID


@dataclass
class ControlFlowTracker:

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
