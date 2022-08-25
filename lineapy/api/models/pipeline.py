from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from lineapy.api.api_utils import extract_taskgraph
from lineapy.data.types import PipelineType
from lineapy.db.relational import (
    ArtifactDependencyORM,
    PipelineORM,
    SessionContextORM,
)
from lineapy.execution.context import get_context
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.airflow import AirflowDagConfig, AirflowPlugin
from lineapy.plugins.pipeline_writers import PipelineWriterFactory
from lineapy.plugins.script import ScriptPlugin
from lineapy.plugins.task import AirflowDagConfig as AirflowDagConfig2
from lineapy.plugins.task import TaskGraphEdge
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
        output_dir: Optional[str] = None,
        pipeline_dag_config: Optional[AirflowDagConfig] = {},
    ) -> Path:
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
        last_session = session_orm[0]

        if framework in PipelineType.__members__:
            if PipelineType[framework] == PipelineType.AIRFLOW:

                ret = AirflowPlugin(db, last_session.id).sliced_airflow_dag(
                    self.name,
                    self.task_graph,
                    output_dir=output_dir,
                    airflow_dag_config=pipeline_dag_config,
                )

            else:

                ret = ScriptPlugin(db, last_session.id).sliced_pipeline_dag(
                    self.name,
                    self.task_graph,
                    output_dir=output_dir,
                )

            # send the info
            track(
                ToPipelineEvent(
                    framework,
                    len(self.artifact_names),
                    self.task_graph.get_airflow_dependency() != "",
                    pipeline_dag_config is not None,
                )
            )
            return ret

        else:
            raise Exception(f"No PipelineType for {framework}")

    def _export(
        self,
        framework: str = "SCRIPT",
        output_dir: str = ".",
        pipeline_dag_config: Optional[AirflowDagConfig2] = {},
    ) -> None:
        """
        This method uses objects implementing new style of graph refactor.
        It is meant to eventually replace existing `export()` method above.
        TODO [LIN-469]: Replace existing `export()` method with this one.
        """
        # Create artifact collection
        execution_context = get_context()
        artifact_collection = ArtifactCollection(
            execution_context.executor.db, self.artifact_names
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
            dag_config=pipeline_dag_config,
        )

        # Write out pipeline files
        pipeline_writer.write_pipeline_files()

        # Track the event
        track(
            ToPipelineEvent(
                framework,
                len(self.artifact_names),
                self.task_graph.get_airflow_dependency() != "",
                pipeline_dag_config is not None,
            )
        )

    def save(self):
        # TODO save this pipeline to the db using PipelineORM
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
