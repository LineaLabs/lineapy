from uuid import UUID
from flask import Blueprint, jsonify

from lineapy.db.relational.schema.relational import (
    ArtifactORM,
    ExecutionORM,
    NodeValueORM,
)
from lineapy.data.types import Artifact, DataAssetType, Execution
from lineapy.utils import (
    CaseNotHandledError,
    EntryNotFoundError,
    NullValueError,
)
from lineapy.app.app_db import lineadb
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.utils import EntryNotFoundError
from lineapy.execution.executor import Executor

# from decouple import config


# IS_DEV = config("FLASK_ENV") == "development"
HTTP_REQUEST_HOST = "http://localhost:4000"

routes_blueprint = Blueprint("routes", __name__)


def parse_artifact_orm(artifact_orm):
    artifact = Artifact.from_orm(artifact_orm)
    artifact_json = lineadb.jsonify_base_artifact(artifact)

    #     return artifact_json
    # raise EntryNotFoundError(f"Value for {artifact.id} is not found")


@routes_blueprint.route("/")
def home():
    return "ok"


@routes_blueprint.route(
    "/api/v1/executor/execute/<artifact_id>", methods=["GET"]
)
def execute(artifact_id):
    # FIXME: we shouldn't mutate the same variable name's type
    artifact_id = UUID(artifact_id)
    artifact = lineadb.get_artifact(artifact_id)
    if artifact is None:
        raise EntryNotFoundError(f"Artifact with {artifact_id} is not found")
    # find version
    version = lineadb.get_latest_node_version(artifact_id)

    # increment version
    if version is None:
        version = 0
    version += 1

    # create row in exec table
    exec_orm = ExecutionORM(artifact_id=artifact_id, version=version)
    lineadb.session.add(exec_orm)
    lineadb.session.commit()

    # get graph and re-execute
    executor = Executor()
    program = lineadb.get_graph_from_artifact_id(artifact_id)
    artifact_node = lineadb.get_node_by_id(artifact_id)
    context = lineadb.get_context(artifact_node.session_id)
    executor.execute_program(program, context)

    # run through Graph nodes and write values to NodeValueORM with new version
    lineadb.write_node_values(program.nodes, version)

    # NOTE: we can hold off on the following comment because
    # the version property of both classes implicitly creates the relationship for us.
    # create relationships between Execution row and NodeValue objects

    # return new Artifact JSON with new NodeValue
    artifact_value = lineadb.get_node_value(artifact_id, version)
    if artifact_value is None:
        raise EntryNotFoundError(
            f"Artifact value with {artifact_id} is not found"
        )

    asset = lineadb.jsonify_base_artifact(artifact)

    response = jsonify({"data_asset": asset})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@routes_blueprint.route(
    "/api/v1/executor/executions/<artifact_id>", methods=["GET"]
)
def get_executions(artifact_id):
    artifact_id = UUID(artifact_id)

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
    artifact_orms = lineadb.session.query(ArtifactORM).all()

    results = [
        parse_artifact_orm(artifact_orm) for artifact_orm in artifact_orms
    ]

    response = jsonify({"data_assets": results})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@routes_blueprint.route("/api/v1/artifacts/<artifact_id>", methods=["GET"])
def get_artifact(artifact_id):
    artifact_id = UUID(artifact_id)
    artifact_orm = (
        lineadb.session.query(ArtifactORM)
        .filter(ArtifactORM.id == artifact_id)
        .first()
    )

    if artifact_orm is not None:
        artifact = parse_artifact_orm(artifact_orm)
        response = jsonify({"data_asset": artifact})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    response = jsonify({"error": "asset not found"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# right now we only support Dataset intermediates, because we don't have a way of automatically demarking what type
# each intermediate is
@routes_blueprint.route("/api/v1/node/value/<node_id>", methods=["GET"])
def get_node_value(node_id):
    node_id = UUID(node_id)
    node_value = lineadb.get_node_value(node_id)

    if node_value is None:
        raise NullValueError(f"Could not get value for {node_id}")

    if node_value.value_type is DataAssetType.PandasDataFrame:
        value = RelationalLineaDB.cast_dataset(node_value)
        response = jsonify({"node_value": value})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    raise CaseNotHandledError("Need to handle other data types for the API")
