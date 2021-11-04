"""
User exposed APIs.

We should keep these external APIs as small as possible, and unless there is
  a very compelling use case, not support more than one way to access the
  same feature.
"""
from datetime import datetime
from typing import Optional

from lineapy.data.types import Artifact, NodeValue
from lineapy.execution.context import get_context
from lineapy.graph_reader.apis import LineaArtifact, LineaCatalog
from lineapy.utils import get_value_type


def save(value: object, /, description: Optional[str] = None) -> LineaArtifact:
    """
    Publishes artifact to the linea repo
    """
    execution_context = get_context()
    executor = execution_context.executor
    db = executor.db
    call_node = execution_context.node
    value_node_id = call_node.positional_args[0]
    db.write_artifact(
        Artifact(
            id=value_node_id,
            date_created=datetime.now(),
            name=description,
        )
    )
    # serialize to db
    timing = executor.get_execution_time(value_node_id)
    db.write_node_value(
        NodeValue(
            node_id=value_node_id,
            value=value,
            execution_id=executor.execution.id,
            start_time=timing[0],
            end_time=timing[1],
            value_type=get_value_type(value),
        )
    )
    # we have to commit eagerly because if we just add it
    #   to the queue, the `res` value may have mutated
    #   and that's incorrect.
    db.commit()

    # TODO: Make work with unnamed artifacts
    return LineaArtifact(description, db)


def get(artifact_name: str) -> LineaArtifact:
    """get

    Parameters
    ----------
    artifact_name: str
        name of the artifact. Note that if you do not remember the artifact,
        you can use the catalog to browse the options

    Returns
    -------
    linea artifact
        an object of the class `LineaArtifact`, which offers methods to access
        information we have stored about the artifact
    """
    execution_context = get_context()
    return LineaArtifact(artifact_name, execution_context.executor.db)


def catalog() -> LineaCatalog:
    """catalog
    Returns
    -------
    linea catalog
        an object of the class `LineaCatalog`
    """
    execution_context = get_context()
    return LineaCatalog(execution_context.executor.db)
