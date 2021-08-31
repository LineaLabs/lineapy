from flask import request, Blueprint, jsonify, send_file, make_response
from requests import get
import os
from app_db import lineadb
from tests.stub_data.stub import stub_data_assets
from tests.stub_data.graph_with_csv_import import (
    graph_with_csv_import as stub_graph,
    session,
    sum_call,
)
from lineapy.db.relational.schema.relational import *
from lineapy.data.types import *
from lineapy.execution.executor import Executor
from lineapy.db.db import LineaDB
from sqlalchemy import func

# from decouple import config


# IS_DEV = config("FLASK_ENV") == "development"
WEBPACK_DEV_SERVER_HOST = "http://localhost:3000"
HTTP_REQUEST_HOST = "http://localhost:6000"

routes_blueprint = Blueprint("routes", __name__)


def proxy(host, path):
    """
    This proxy setup is to allow webpack hot-reload to work
    """
    response = get(f"{host}{path}")
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = {
        name: value
        for name, value in response.raw.headers.items()
        if name.lower() not in excluded_headers
    }
    return (response.content, response.status_code, headers)


# @app.route("/app/", defaults={"path": "index.html"}, methods=["POST", "OPTIONS"])
# @app.route("/app/<path:path>")
# def getApp(path):
#     if IS_DEV:
#         print("in dev environemtn")
#         return proxy(WEBPACK_DEV_SERVER_HOST, request.path)
#     return app.send_static_file(path)


@routes_blueprint.route("/")
def home():
    return "ok"


@routes_blueprint.route("/api/v1/executor/execute/<artifact_id>", methods=["GET"])
def execute(artifact_id):
    artifact_id = sum_call.id

    # find version
    version = lineadb.session.query(func.max(NodeValueORM.version)).scalar()

    # increment version
    if version is None:
        version = 0
    version += 1

    executor = Executor()

    # NOTE: in the future the graph nodes will already exist in the database before
    # the execution API is called. So this is just a filler for testing for MVP
    # this is all stuff that should have happened before execute API is called
    # version will never be 1 during re-exec
    if version == 1:
        # execute stub graph and write to database
        executor.execute_program(stub_graph)
        lineadb.write_context(session)
        lineadb.write_nodes(stub_graph._nodes)

        # TODO: determine type of artifact value
        lineadb.add_node_id_to_artifact_table(
            artifact_id, value_type=DataAssetType.Array
        )

    # create row in exec table
    exec_orm = ExecutionORM(artifact_id=artifact_id, version=version)
    lineadb.session.add(exec_orm)
    lineadb.session.commit()

    # call get_graph_from_artifact_id
    program = lineadb.get_graph_from_artifact_id(artifact_id)

    # call execute_program on Graph
    executor.execute_program(program, session)

    # run through Graph nodes and write values to NodeValueORM with new version
    lineadb.write_node_values(program._nodes, version)

    # NOTE: we can hold off on the following comment because
    # the version property of both classes implicitly creates the relationship for us.
    # create relationships between Execution row and NodeValue objects

    # return new Artifact JSON with new NodeValue
    artifact_value = lineadb.get_node_value(artifact_id, version)

    # TODO: add handling for different DataAssetTypes
    result = None
    artifact = lineadb.get_artifact(artifact_id)
    if artifact.value_type == DataAssetType.Array:
        result = LineaDB.cast_serialized(
            artifact_value, LineaDB.get_type(artifact_value)
        )

    response = jsonify({"result": result})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
