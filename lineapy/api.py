"""
User exposed APIs.

We should keep these external APIs as small as possible, and unless there is
  a very compelling use case, not support more than one way to access the
  same feature.
"""
from typing import Any, Optional

from lineapy.constants import ExecutionMode
from lineapy.db.relational.db import RelationalLineaDB
from lineapy.graph_reader.apis import LineaArtifact, LineaCatalog


def save(variable: Any, description: Optional[str] = None) -> None:
    """
    Publishes artifact to the linea repo
    """
    """
    DEV NOTEs:
    - This method is instrumented by transformer to be called by the tracer
    """

    raise RuntimeError(
        """This method should be intrusmented and not invoked."""
    )


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
    # FIXME: this ExecutionMode.DEV is a hack
    db = RelationalLineaDB.from_environment(ExecutionMode.DEV)
    return LineaArtifact(artifact_name, db)


def catalog() -> LineaCatalog:
    """catalog
    Returns
    -------
    linea catalog
        an object of the class `LineaCatalog`
    """
    db = RelationalLineaDB.from_environment(ExecutionMode.DEV)
    return LineaCatalog(db)
