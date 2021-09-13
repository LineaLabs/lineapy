from typing import Any, Optional, List
from lineapy.data.types import (
    LiteralType,
    ValueType,
    Artifact,
    Node,
    NodeType,
    NodeValue,
    NodeValueType,
)
from lineapy.constants import BACKEND_REQUEST_HOST
from lineapy.db.relational.schema.relational import NodeValueORM
from lineapy.utils import jsonify_value


def jsonify_intermediate(
    intermediate_node: Node, intermediate_node_value: NodeValueORM
) -> Optional[dict]:

    start_col = intermediate_node.col_offset + 1
    end_col = intermediate_node.end_col_offset + 1
    if intermediate_node.assigned_variable_name is not None:
        end_col = len(intermediate_node.assigned_variable_name) + start_col

    token_json = {
        "id": intermediate_node.id,
        "line": intermediate_node.lineno,
        "start": start_col,
        "end": end_col,
    }

    if intermediate_node_value is None or intermediate_node_value.value is None:
        # FIXME
        return None

    # currently unsupported intermediate value types
    if intermediate_node_value.value_type in [ValueType.chart, ValueType.array]:
        # FIXME
        return None

    intermediate_value = jsonify_value(
        intermediate_node_value.value, intermediate_node_value.value_type
    )

    intermediate_json = {
        "file": "",
        "id": intermediate_node.id,
        "name": "",
        "type": intermediate_node_value.value_type.name,
        "date": intermediate_node_value.timestamp,
        "text": intermediate_value,
    }

    print(intermediate_json)
    print("ppppp")

    token_json["intermediate"] = intermediate_json
    return token_json


def jsonify_all_intermediates(
    graph_nodes: List[Node], graph_node_values: List[NodeValueORM]
):
    intermediates_json = []
    for intermediate_node in graph_nodes:
        if intermediate_node.node_type is not NodeType.CallNode:
            continue

        intermediate_node_value = None
        for node_value in graph_node_values:
            if node_value.node_id == intermediate_node.id:
                intermediate_node_value = node_value

        intermediate_json = jsonify_intermediate(
            intermediate_node, intermediate_node_value
        )

        if intermediate_json is not None:
            intermediates_json.append(intermediate_json)
    return intermediates_json


def jsonify_artifact(
    artifact: Artifact,
    version: int,
    code: str,
    artifact_value: NodeValueORM,
    graph_nodes: List[Node],
    graph_node_values: List[NodeValueORM],
) -> dict:
    """
    This function is called to create intermediates

    NOTE/TODO:
    - we skip some values whose type we don't currently handle
    """
    json_artifact = artifact.dict()

    json_artifact["type"] = artifact_value.value_type.name

    json_artifact["date"] = json_artifact["date_created"]
    del json_artifact["date_created"]

    json_artifact["file"] = ""

    json_artifact["code"] = {}
    json_artifact["code"]["text"] = code

    # generate intermediate jsons
    tokens_json = jsonify_all_intermediates(graph_nodes, graph_node_values)

    json_artifact["code"]["tokens"] = tokens_json

    if artifact_value.value_type in [
        ValueType.value,
        ValueType.array,
        ValueType.dataset,
    ]:
        result = jsonify_value(artifact_value.value, artifact_value.value_type)
        json_artifact["text"] = result
    elif artifact_value.value_type == ValueType.chart:
        json_artifact["image"] = (
            BACKEND_REQUEST_HOST
            + "/api/v1/images/"
            + str(artifact.id)
            + "/"
            + str(version)
        )

    return json_artifact
