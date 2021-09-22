from flask import Blueprint, jsonify, send_file, make_response, request
from sqlalchemy import func
import io
from typing import Union, Optional

from lineapy.app.app_db import lineadb
from lineapy.data.types import (
    Artifact,
    Execution,
    LineaID,
    NodeType,
    ValueType,
)
from lineapy.db.relational.schema.relational import (
    NodeValueORM,
    ArtifactORM,
    ExecutionORM,
)
from lineapy.graph_reader.graph_util import get_segment_from_code
from lineapy.execution.executor import Executor
from lineapy.app.app_util import jsonify_artifact
from lineapy.utils import InternalLogicError, UserError, jsonify_value

from lineapy.constants import LATEST_NODE_VERSION


routes_blueprint = Blueprint("routes", __name__)


def latest_version_of_node(node_id: LineaID) -> Optional[int]:
    subqry = lineadb.session.query(func.max(NodeValueORM.version)).filter(
        NodeValueORM.node_id == node_id
    )
    qry = (
        lineadb.session.query(NodeValueORM)
        .filter(
            NodeValueORM.node_id == node_id,
            NodeValueORM.version == subqry,
        )
        .first()
    )
    if qry is not None:
        return qry.version
    return None


def parse_version(version: Optional[Union[str, int]], node_id: LineaID) -> int:
    """
    Helper function to either retrieve the latest version, or cast the version
      specified into string
    """
    if version is None:
        # FIXME: we should not crash the server
        raise UserError(f"Did not provide version info for node {node_id}")
    if version == LATEST_NODE_VERSION:
        latest = latest_version_of_node(node_id)
        if latest is None:
            raise InternalLogicError(
                f"Was not able to find latest version for {node_id}"
            )
        return latest
    return int(version)


def access_db_and_jsonify_artifact(artifact: Artifact, version: int):
    """
    This is a helper function that return new Artifact JSON with new NodeValue
    """
    artifact_value = lineadb.get_node_value_from_db(artifact.id, version)
    if artifact_value is None:
        raise InternalLogicError("Cannot find artifact")
    code = lineadb.get_code_from_artifact_id(artifact.id)
    graph_nodes = lineadb.get_session_graph_from_artifact_id(artifact.id).nodes

    graph_node_values = [
        lineadb.get_node_value_from_db(node.id, version) for node in graph_nodes
    ]

    graph_node_values = [node for node in graph_node_values if node is not None]

    return jsonify_artifact(
        artifact, version, code, artifact_value, graph_nodes, graph_node_values
    )


@routes_blueprint.route("/")
def home():
    """
    This is the API server so we don't have a home API, useful for testing.
    """
    return "ok"


@routes_blueprint.route(
    "/api/v1/executor/execute/<artifact_id>", methods=["GET"]
)
def execute(artifact_id):
    """
    Executes the graph associated with the artifact and returns the result of
      the execution.
    """
    artifact = lineadb.get_artifact(artifact_id)
    if artifact is not None:
        # find version
        version = latest_version_of_node(artifact.id)

        # increment version
        if version is None:
            version = 0
        version += 1

        # get graph and re-execute
        executor = Executor()
        program = lineadb.get_session_graph_from_artifact_id(artifact_id)
        artifact_node = lineadb.get_node_by_id(artifact_id)
        context = lineadb.get_context(artifact_node.session_id)
        execution_time = executor.execute_program(program, context)

        # create row in exec table
        exec_orm = ExecutionORM(
            artifact_id=artifact_id,
            version=version,
            execution_time=execution_time,
        )
        lineadb.session.add(exec_orm)
        lineadb.session.commit()

        # run through Graph nodes and write values to NodeValueORM with
        #   new version
        lineadb.write_node_values(program.nodes, version)

        # NOTE: we can hold off on the following comment because
        # the version property of both classes implicitly creates the
        #   relationship for us.
        # create relationships between Execution row and NodeValue objects

        asset = access_db_and_jsonify_artifact(artifact, version)

        response = jsonify({"data_asset": asset})
        # FIXME: this following is fishy
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    else:
        return {}


@routes_blueprint.route(
    "/api/v1/executor/executions/<artifact_id>", methods=["GET"]
)
def get_executions(artifact_id):

    execution_orms = (
        lineadb.session.query(ExecutionORM)
        .filter(ExecutionORM.artifact_id == artifact_id)
        .all()
    )
    executions = [Execution.from_orm(e) for e in execution_orms]

    jsons = [e.dict() for e in executions]
    response = jsonify({"executions": jsons})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@routes_blueprint.route("/api/v1/artifacts/all", methods=["GET"])
def get_artifacts():
    """
    `get_artifacts` (note the plural) gets the set of all artifacts at their
      latest versions
    It includes
    - LineaID
    - data type (for rendering & filtering purposes)
    - date created
    - (future) user

    TODO
    - We probably need pagination when the set of artifacts grows large
    """
    artifact_orms = lineadb.session.query(ArtifactORM).all()
    results = [
        access_db_and_jsonify_artifact(
            Artifact.from_orm(artifact_orm),
            latest_version_of_node(artifact_orm.id),
        )
        for artifact_orm in artifact_orms
    ]

    response = jsonify({"data_assets": results})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# query param "?version=some_int"
@routes_blueprint.route("/api/v1/artifacts/<artifact_id>", methods=["GET"])
def get_artifact(artifact_id):
    """
    `get_artifact` is accessed by the ArtifactPage and returns a lot more
      information than the summary data provided by `get_artifacts`.
    """
    artifact_orm = (
        lineadb.session.query(ArtifactORM)
        .filter(ArtifactORM.id == artifact_id)
        .first()
    )

    if artifact_orm is not None:
        version = parse_version(request.args.get("version"), artifact_id)
        artifact = access_db_and_jsonify_artifact(
            Artifact.from_orm(artifact_orm), version
        )
        response = jsonify({"data_asset": artifact})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    response = jsonify({"error": "asset not found"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# assuming binaries are in PNG format
@routes_blueprint.route("/api/v1/images/<value_id>/<version>", methods=["GET"])
def get_image(value_id, version):
    img = lineadb.get_node_value_from_db(value_id, version).value

    # create file-object in memory
    file_object = io.BytesIO()

    # write PNG in file-object
    img.save(file_object, "PNG")

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)

    response = make_response(
        send_file(
            file_object,
            mimetype="image/PNG",
        )
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# query param "?version=some_int"
@routes_blueprint.route("/api/v1/node/value/<node_id>", methods=["GET"])
def get_node_value(node_id):
    """
    This is currently used by the code view functionality to inspect
      intermediate results
    FIXME:
    - support more data types
    - also we should probably merge this with `get_image` because it's not up
      to the UI to know what the type of the node data is
    """
    raw_version = request.args.get("version")
    version = parse_version(raw_version, node_id)

    node = lineadb.get_node_by_id(node_id)
    node_value = lineadb.get_node_value_from_db(node_id, version)

    node_value_type = node_value.value_type

    if node_value_type in [ValueType.dataset, ValueType.value]:
        node_value = jsonify_value(node_value.value, node_value.value_type)

    node_name = None
    if (
        node.node_type is NodeType.CallNode
        and node.assigned_variable_name is not None
    ):
        node_name = node.assigned_variable_name
    else:
        node_name = get_segment_from_code(
            lineadb.get_context(node.session_id).code, node
        )

    response = jsonify(
        {
            "node_value": node_value,
            "node_value_type": node_value_type.name,
            "node_name": node_name,
        }
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
