"""
User exposed APIs.

We should keep these external APIs as small as possible, and unless there is
  a very compelling use case, not support more than one way to access the
  same feature.
"""
import pickle
import types
from datetime import datetime

from lineapy.data.types import Artifact, NodeValue
from lineapy.exceptions.db_exceptions import ArtifactSaveException
from lineapy.execution.context import get_context
from lineapy.graph_reader.apis import LineaArtifact, LineaCatalog
from lineapy.utils import get_value_type


def save(value: object, description: str, /) -> LineaArtifact:
    """
    Publishes artifact to the linea repo
    """
    execution_context = get_context()
    executor = execution_context.executor
    db = executor.db
    call_node = execution_context.node

    # If this value is stored as a global in the executor (meaning its an external side effect)
    # then look it up from there, instead of using this node.
    try:
        in_value_to_node = value in executor._value_to_node
    # happens on non hashable objects
    except Exception:
        in_value_to_node = False
    if in_value_to_node:
        value_node_id = executor._value_to_node[value]
    else:
        # Lookup the first arguments id, which is the id for the value, and
        # save that as the artifact
        value_node_id = call_node.positional_args[0]

    execution_id = executor.execution.id
    timing = executor.get_execution_time(value_node_id)

    # serialize value to db if we haven't before
    # (happens with multiple artifacts pointing to the same value)
    if not db.node_value_in_db(
        node_id=value_node_id, execution_id=execution_id
    ):
        if not _can_save_to_db(value):
            raise ArtifactSaveException()
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
    db.write_artifact(
        Artifact(
            node_id=value_node_id,
            execution_id=execution_id,
            date_created=datetime.now(),
            name=description,
        )
    )
    # we have to commit eagerly because if we just add it
    #   to the queue, the `res` value may have mutated
    #   and that's incorrect.
    db.commit()

    return LineaArtifact(
        db=db,
        execution_id=executor.execution.id,
        node_id=value_node_id,
        session_id=call_node.session_id,
        name=description,
    )


def _can_save_to_db(value: object) -> bool:
    """
    Tests if the value is of a type that can be serialized to the DB.
    """
    if isinstance(value, types.ModuleType):
        return False
    try:
        pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError:
        return False
    return True


def get(artifact_name: str) -> LineaArtifact:
    """
    Gets an artifact from the DB.

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
    db = execution_context.executor.db
    artifact = db.get_artifact_by_name(artifact_name)
    return LineaArtifact(
        db=db,
        execution_id=artifact.execution_id,
        node_id=artifact.node_id,
        session_id=artifact.node.session_id,
        name=artifact_name,
    )


def catalog() -> LineaCatalog:
    """catalog
    Returns
    -------
    linea catalog
        an object of the class `LineaCatalog`
    """
    execution_context = get_context()
    return LineaCatalog(execution_context.executor.db)
