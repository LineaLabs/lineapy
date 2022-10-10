from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import List, Optional

from lineapy.api.api_utils import extract_taskgraph
from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.db.relational import (
    ArtifactDependencyORM,
    PipelineORM,
    SessionContextORM,
)
from lineapy.execution.context import get_context
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writers import PipelineWriterFactory
from lineapy.plugins.task import AirflowDagConfig, TaskGraphEdge
from lineapy.utils.analytics.event_schemas import (
    ErrorType,
    ExceptionEvent,
    ToPipelineEvent,
)
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.utils import get_new_id

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(
        self,
        artifacts: List[str],
        name: Optional[str] = None,
        dependencies: TaskGraphEdge = {},
    ):
        if len(artifacts) == 0:
            raise ValueError(
                "Pipelines must contain at least one artifact\nEmpty Pipelines are invalid"
            )
        self.dependencies = dependencies
        self.artifact_safe_names, self.task_graph = extract_taskgraph(
            artifacts, dependencies
        )
        self.name = name or "_".join(self.artifact_safe_names)
        self.artifact_names: List[str] = artifacts
        self.id = get_new_id()

    def export(
        self,
        framework: str = "SCRIPT",
        output_dir: str = ".",
        input_parameters: List[str] = [],
        reuse_pre_computed_artifacts: List[str] = [],
        generate_test: bool = False,
        pipeline_dag_config: Optional[AirflowDagConfig] = {},
        include_non_slice_as_comment=True,
    ) -> Path:
        # Create artifact collection
        execution_context = get_context()
        artifact_defs = [
            get_lineaartifactdef(art_entry=art_entry)
            for art_entry in self.artifact_names
        ]
        reuse_pre_computed_artifact_defs = [
            get_lineaartifactdef(art_entry=art_entry)
            for art_entry in reuse_pre_computed_artifacts
        ]
        artifact_collection = ArtifactCollection(
            db=execution_context.executor.db,
            target_artifacts=artifact_defs,
            input_parameters=input_parameters,
            reuse_pre_computed_artifacts=reuse_pre_computed_artifact_defs,
            include_non_slice_as_comment=include_non_slice_as_comment,
        )

        # Check if the specified framework is a supported/valid one
        if framework not in PipelineType.__members__:
            raise Exception(f"No PipelineType for {framework}")

        # Construct pipeline writer
        pipeline_writer = PipelineWriterFactory.get(
            pipeline_type=PipelineType[framework],
            artifact_collection=artifact_collection,
            dependencies=self.dependencies,
            pipeline_name=self.name,
            output_dir=output_dir,
            generate_test=generate_test,
            dag_config=pipeline_dag_config,
        )

        # Write out pipeline files
        pipeline_writer.write_pipeline_files()

        # Provide user warning about currently unsupported functionality
        if len(reuse_pre_computed_artifacts) > 0 and framework == "AIRFLOW":
            warnings.warn(
                "Reuse of pre-computed artifacts is currently NOT supported "
                "for Airflow DAGs. Hence, the generated Airflow DAG file would "
                "recompute all artifacts in the pipeline."
            )

        # Track the event
        track(
            ToPipelineEvent(
                framework,
                len(self.artifact_names),
                self.task_graph.get_airflow_dependency() != "",
                pipeline_dag_config is not None,
            )
        )

        return pipeline_writer.output_dir

    def save(self):
        """
        Save this pipeline to the db using PipelineORM.
        """
        execution_context = get_context()
        db = execution_context.executor.db
        session_orm = (
            db.session.query(SessionContextORM)
            .order_by(SessionContextORM.creation_time.desc())
            .all()
        )
        if len(session_orm) == 0:
            track(ExceptionEvent(ErrorType.PIPELINE, "No session found in DB"))
            raise Exception("No sessions found in the database.")

        artifacts_to_save = {
            artifact_name: db.get_artifactorm_by_name(artifact_name)
            for artifact_name in self.artifact_names
        }

        art_deps_to_save = []
        for post_artifact, pre_artifacts in self.dependencies.items():
            post_to_save = artifacts_to_save[post_artifact]
            pre_to_save = [artifacts_to_save[a] for a in pre_artifacts]
            art_dep_to_save = ArtifactDependencyORM(
                post_artifact=post_to_save,
                pre_artifacts=set(pre_to_save),
            )
            art_deps_to_save.append(art_dep_to_save)

        pipeline_to_write = PipelineORM(
            name=self.name,
            artifacts=set(artifacts_to_save.values()),
            dependencies=art_deps_to_save,
        )
        db.write_pipeline(art_deps_to_save, pipeline_to_write)
