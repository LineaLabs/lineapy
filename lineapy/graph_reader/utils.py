from itertools import groupby
from typing import Iterable, List, Tuple

from lineapy.api.models.linea_artifact import LineaArtifact, LineaArtifactDef
from lineapy.data.graph import Graph
from lineapy.data.types import CallNode, LineaID, LookupNode
from lineapy.db.db import RelationalLineaDB


def is_import_node(graph: Graph, node_id: LineaID) -> bool:
    """
    Given node_id, check whether it is a CallNode doing module import
    """
    node = graph.get_node(node_id)
    if isinstance(node, CallNode) and hasattr(node, "function_id"):
        lookup_node_id = node.__dict__.get("function_id", None)
        if lookup_node_id is not None:
            lookup_node = graph.get_node(lookup_node_id)
            if isinstance(lookup_node, LookupNode):
                lookup_node_name = lookup_node.__dict__.get("name", "")
                return lookup_node_name in ["l_import", "getattr"]
    return False


def get_db_artifacts_from_artifactdef(
    db: RelationalLineaDB, artifact_entries: List[LineaArtifactDef]
) -> List[LineaArtifact]:
    # converts artifactdef list to a linea artfact list by fetching it from the db
    return [
        LineaArtifact.get_artifact_from_def(db, art_def)
        for art_def in artifact_entries
    ]


def get_artifacts_grouped_by_session(
    all_linea_artifacts: List[LineaArtifact],
) -> Iterable[Tuple[LineaID, List[LineaArtifact]]]:
    """
    Get LineaArtifact from each artifact entry and group by the Session they belong to.

    Artifact entries are specified as name and optionally version as the end user would specify.

    This helper function is used to group target and reuse_precomputed artifacts so that we can
    create SessionArtifacts for each Session.

    """
    # This function groups artifacts into a dict with session ids as key
    #
    for session_id, artifacts_by_session in groupby(
        all_linea_artifacts, lambda d: d._session_id
    ):
        yield session_id, list(artifacts_by_session)


def check_duplicates(artifact_entries: List[LineaArtifactDef]):
    all_names = [art_def["artifact_name"] for art_def in artifact_entries]
    if len(all_names) != len(set(all_names)):
        raise KeyError(
            # TODO - make this error more specific. Should tell you which calling list has the duplicates
            "Duplicate artifacts added"
        )
