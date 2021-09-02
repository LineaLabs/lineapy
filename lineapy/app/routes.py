from flask import Blueprint, request, jsonify, send_file, make_response
from sqlalchemy import func
from requests import get
import os

from lineapy.app.app_db import lineadb
from lineapy.db.relational.schema.relational import *
from lineapy.data.types import *
from lineapy.execution.executor import Executor
from lineapy.db.db import LineaDB
from tests.stub_data.stub import stub_data_assets


# from decouple import config


# IS_DEV = config("FLASK_ENV") == "development"
HTTP_REQUEST_HOST = "http://localhost:4000"

routes_blueprint = Blueprint("routes", __name__)


@routes_blueprint.route("/")
def home():
    return "ok"


@routes_blueprint.route("/api/v1/executor/execute/<artifact_id>", methods=["GET"])
def execute(artifact_id):
    artifact_id = UUID(artifact_id)
    artifact = lineadb.get_artifact(artifact_id)

    # find version
    version = lineadb.session.query(func.max(NodeValueORM.version)).scalar()

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
    lineadb.write_node_values(program._nodes, version)

    # NOTE: we can hold off on the following comment because
    # the version property of both classes implicitly creates the relationship for us.
    # create relationships between Execution row and NodeValue objects

    # return new Artifact JSON with new NodeValue
    artifact_value = lineadb.get_node_value(artifact_id, version)

    # TODO: add handling for different DataAssetTypes
    # asset = lineadb.jsonify_artifact(artifact)
    # # get artifact from stub
    asset = None
    for a in stub_data_assets:
        if a["id"] == artifact_id:
            # prepare_asset(asset, preview=False)
            asset = a
    if artifact.value_type == DataAssetType.Value:
        result = LineaDB.cast_serialized(
            artifact_value, LineaDB.get_type(artifact_value)
        )
        asset["text"] = result

    response = jsonify({"data_asset": asset})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
