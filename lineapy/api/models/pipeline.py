from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import PipelineType
from lineapy.db.relational import (
    ArtifactDependencyORM,
    PipelineORM,
    SessionContextORM,
    VariableNodeORM,
)
from lineapy.execution.context import get_context
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.pipeline_writer_factory import PipelineWriterFactory
from lineapy.plugins.task import TaskGraphEdge, extract_taskgraph
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
        artifacts: List[Union[str, Tuple[str, int]]],
        name: Optional[str] = None,
        dependencies: TaskGraphEdge = {},
        input_parameters: List[str] = [],
        reuse_pre_computed_artifacts: List[Union[str, Tuple[str, int]]] = [],
        is_udf: bool = False,
    ):
        if len(artifacts) == 0:
            raise ValueError(
                "Pipelines must contain at least one artifact\nEmpty Pipelines are invalid"
            )
        self.dependencies = dependencies
        self.artifact_safe_names, self.task_graph = extract_taskgraph(
            artifacts, dependencies
        )
        self.name = name or "_".join(
            [str(artname) for artname in self.artifact_safe_names]
        )
        self.artifact_names: List[Union[str, Tuple[str, int]]] = artifacts
        self.reuse_pre_computed_artifacts: List[
            Union[str, Tuple[str, int]]
        ] = reuse_pre_computed_artifacts
        self.id = get_new_id()

        # get artifact_collection for use in pipeline writers
        self.artifact_collection = self._get_artifact_collection(
            input_parameters,
            reuse_pre_computed_artifacts,
        )
        self.is_udf: bool = is_udf

    def export(
        self,
        framework: str = "SCRIPT",
        output_dir: str = ".",
        generate_test: bool = False,
        pipeline_dag_config: Optional[Dict] = {},
        include_non_slice_as_comment=False,
    ) -> Path:
        # Check if the specified framework is a supported/valid one
        if framework not in PipelineType.__members__:
            raise Exception(f"No PipelineType for {framework}")

        # Construct pipeline writer. Check out class:PipelineType for supported frameworks
        # If you want to add a new framework, please read the "adding a new pipeline writer" tutorial
        pipeline_writer = PipelineWriterFactory.get(
            pipeline_type=PipelineType[framework],
            artifact_collection=self.artifact_collection,
            dependencies=self.dependencies,
            pipeline_name=self.name,
            output_dir=output_dir,
            generate_test=generate_test,
            dag_config=pipeline_dag_config,
            include_non_slice_as_comment=include_non_slice_as_comment,
        )

        # Write out pipeline files
        pipeline_writer.write_pipeline_files()

        # Provide user warning about currently unsupported functionality
        if (
            len(self.reuse_pre_computed_artifacts) > 0
            and framework == "AIRFLOW"
        ):
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
                len(list(self.task_graph.graph.edges)) > 0,
                pipeline_dag_config is not None,
            )
        )

        return pipeline_writer.output_dir

    def _get_artifact_collection(
        self,
        input_parameters,
        reuse_pre_computed_artifacts,
    ):
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
        )

        return artifact_collection

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
            artifact_name: (
                db.get_artifactorm_by_name(artifact_name)
                if isinstance(artifact_name, str)
                else db.get_artifactorm_by_name(
                    artifact_name[0], version=artifact_name[1]
                )
            )
            for artifact_name in self.artifact_names
        }

        reuse_artifacts_to_save = {
            artifact_name: (
                db.get_artifactorm_by_name(artifact_name)
                if isinstance(artifact_name, str)
                else db.get_artifactorm_by_name(
                    artifact_name[0], version=artifact_name[1]
                )
            )
            for artifact_name in self.reuse_pre_computed_artifacts
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

        input_parameter_nodes = set()
        for (
            session_artifact
        ) in self.artifact_collection.session_artifacts.values():
            for (
                input_parameter_name,
                input_parameter_node_id,
            ) in session_artifact.input_parameters_node.values():
                input_parameter_nodes.add(
                    VariableNodeORM(
                        id=input_parameter_node_id,
                        variable_name=input_parameter_name,
                    )
                )

        pipeline_to_write = PipelineORM(
            name=self.name,
            artifacts=set(artifacts_to_save.values()),
            reuseartifacts=set(reuse_artifacts_to_save.values()),
            inputvariables=input_parameter_nodes,
            dependencies=art_deps_to_save,
            isUDF=self.is_udf,
        )
        db.write_pipeline(art_deps_to_save, pipeline_to_write)
