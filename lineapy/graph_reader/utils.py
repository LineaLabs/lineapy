from collections import defaultdict
from typing import Dict, List, Set

from lineapy.api.models.linea_artifact import LineaArtifact, LineaArtifactDef
from lineapy.data.graph import Graph
from lineapy.data.types import CallNode, LineaID, LookupNode


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


def get_artifacts_grouped_by_session(
    db,
    artifact_entries: List[LineaArtifactDef],
) -> Dict[LineaID, List[LineaArtifact]]:
    """
    Get LineaArtifact from each artifact entry and group by the Session they belong to.

    Artifact entries are specified as name and optionally version as the end user would specify.

    This helper function is used to group target and reuse_precomputed artifacts so that we can
    create SessionArtifacts for each Session.

    """
    # TODO: This seems to do three things:
    # 1) Check if artifact name has been repeated in the input list
    # 2) converts artifactdef to a linea artfact by fetching it from the db
    # 3) groups these initialized artifacts into a dict with session ids as key
    #
    # I think the function is doing too much and needs to be fragmented into three with each handling these tasks

    artifacts_grouped_by_session: Dict[
        LineaID, List[LineaArtifact]
    ] = defaultdict(list)
    seen_artifact_names: Set[str] = set()
    for art_def in artifact_entries:
        # Check no two target artifacts have the same name
        if art_def["artifact_name"] in seen_artifact_names:
            raise KeyError(
                "Artifact %s is duplicated", art_def["artifact_name"]
            )
        # Retrieve artifact and put it in the right group
        art = LineaArtifact.get_artifact_from_def(db, art_def)
        artifacts_grouped_by_session[art._session_id].append(art)
        seen_artifact_names.add(art_def["artifact_name"])

    return artifacts_grouped_by_session
