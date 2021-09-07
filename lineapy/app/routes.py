from uuid import UUID
from lineapy.db.relational.schema.relational import ExecutionORM, NodeValueORM
from lineapy.data.types import Artifact, Execution
from flask import Blueprint, jsonify
from sqlalchemy import func

from lineapy.app.app_db import lineadb
from lineapy.db.relational.db import RelationalLineaDB

# from lineapy.db.relational.schema.relational import *
from lineapy.execution.executor import Executor

# from decouple import config


# IS_DEV = config("FLASK_ENV") == "development"
HTTP_REQUEST_HOST = "http://localhost:4000"

routes_blueprint = Blueprint("routes", __name__)


def latest_version():
    return lineadb.session.query(func.max(NodeValueORM.version)).scalar()


def parse_artifact_orm(artifact_orm):
    artifact = Artifact.from_orm(artifact_orm)
    artifact_json = lineadb.jsonify_artifact(artifact)

    artifact_value = lineadb.get_node_value(artifact.id, latest_version())
    if artifact.value_type in [VALUE_TYPE, ARRAY_TYPE]:
        result = RelationalLineaDB.cast_serialized(
            artifact_value, RelationalLineaDB.get_type(artifact_value)
        )
        artifact_json["text"] = result
    elif artifact.value_type is CHART_TYPE:
        ...
    elif artifact.value_type is DATASET_TYPE:
        result = LineaDB.cast_dataset(artifact_value)
        artifact_json["text"] = result
    return artifact_json


@routes_blueprint.route("/")
def home():
    return "ok"


@routes_blueprint.route("/api/v1/executor/execute/<artifact_id>", methods=["GET"])
def execute(artifact_id):
    artifact_id = UUID(artifact_id)
    artifact = lineadb.get_artifact(artifact_id)

    # find version
    version = latest_version()

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
    context = lineadb.get_context(artifact.context)
    executor.execute_program(program, context)

    # run through Graph nodes and write values to NodeValueORM with new version
    lineadb.write_node_values(program.nodes, version)

    # NOTE: we can hold off on the following comment because
    # the version property of both classes implicitly creates the relationship for us.
    # create relationships between Execution row and NodeValue objects

    # return new Artifact JSON with new NodeValue
    artifact_value = lineadb.get_node_value(artifact_id, version)

    # TODO: add handling for different data asset types
    asset = lineadb.jsonify_artifact(artifact)

    if artifact.value_type in [VALUE_TYPE, ARRAY_TYPE]:
        result = RelationalLineaDB.cast_serialized(
            artifact_value, RelationalLineaDB.get_type(artifact_value)
        )
        asset["text"] = result
    elif artifact.value_type is CHART:
        ...
    elif artifact.value_type is DATASET:
        result = RelationalLineaDB.cast_dataset(artifact_value)
        asset["text"] = result

    response = jsonify({"data_asset": asset})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@routes_blueprint.route("/api/v1/executor/executions/<artifact_id>", methods=["GET"])
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

    results = [parse_artifact_orm(artifact_orm) for artifact_orm in artifact_orms]

    response = jsonify({"data_assets": results})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@routes_blueprint.route("/api/v1/artifacts/<artifact_id>", methods=["GET"])
def get_artifact(artifact_id):
    artifact_id = UUID(artifact_id)
    artifact_orm = (
        lineadb.session.query(ArtifactORM).filter(ArtifactORM.id == artifact_id).first()
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
    node_value = lineadb.get_node_value(node_id, latest_version())

    node_value = RelationalLineaDB.cast_dataset(node_value)

    response = jsonify({"node_value": node_value})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
