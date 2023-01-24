from __future__ import annotations

import logging
from typing import List, cast

from lineapy.api.models.linea_artifact import LineaArtifact
from lineapy.db.relational import ArtifactORM

logger = logging.getLogger(__name__)


class LineaArtifactStore:
    """
    A simple way to access meta data about artifacts in Linea.
    """

    def __init__(self, db):
        db_artifacts: List[ArtifactORM] = db.get_all_artifacts()
        self.artifacts: List[LineaArtifact] = [
            LineaArtifact(
                db=db,
                _execution_id=db_artifact.execution_id,
                _node_id=db_artifact.node_id,
                _session_id=db_artifact.node.session_id,
                _version=db_artifact.version,  # type: ignore
                name=cast(str, db_artifact.name),
                date_created=db_artifact.date_created,  # type: ignore
            )
            for db_artifact in db_artifacts
        ]

    @property
    def len(self) -> int:
        return len(self.artifacts)

    @property
    def print(self) -> str:
        # Can't really cache this since the values might change
        return "\n".join(
            [
                f"{a.name}:{a.version} created on {a.date_created}"
                for a in self.artifacts
            ]
        )

    def __str__(self) -> str:
        return self.print

    def __repr__(self) -> str:
        return self.print

    @property
    def export(self):
        """
        Returns
        -------
        Dict
            Dictionary of artifact information, which the user can then
            manipulate with their favorite dataframe tools, such as pandas,
            e.g., `cat_df = pd.DataFrame(artifact_store.export())`.
        """
        return [
            {
                "artifact_name": a.name,
                "artifact_version": a.version,
                "date_created": a.date_created,
            }
            for a in self.artifacts
        ]
