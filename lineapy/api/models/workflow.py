from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Dict, List, Optional

from lineapy.api.models.linea_artifact import get_lineaartifactdef
from lineapy.data.types import WorkflowType
from lineapy.db.relational import (
    ArtifactDependencyORM,
    SessionContextORM,
    WorkflowORM,
)
from lineapy.execution.context import get_context
from lineapy.graph_reader.artifact_collection import ArtifactCollection
from lineapy.plugins.task import TaskGraphEdge
from lineapy.plugins.utils import slugify

# TODO: workflow_writer_factory -> workflow_writer_factory
# TODO: WorkflowWriterFactory -> WorkflowWriterFactory
from lineapy.plugins.workflow_writer_factory import WorkflowWriterFactory

# TODO: CreateWorkflowEvent -> CreateWorkflowEvent
from lineapy.utils.analytics.event_schemas import (
    CreateWorkflowEvent,
    ErrorType,
    ExceptionEvent,
)
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.utils import get_new_id

logger = logging.getLogger(__name__)


class Workflow:
    def __init__(
        self,
        artifacts: List[str],
        name: Optional[str] = None,
        dependencies: TaskGraphEdge = {},
    ):
        if len(artifacts) == 0:
            raise ValueError(
                "Workflows must contain at least one artifact\nEmpty Workflows are invalid"
            )
        self.dependencies = dependencies
        self.artifact_names: List[str] = artifacts

        artifact_safe_names = []
        for artifact_name in artifacts:
            artifact_var = slugify(artifact_name)
            if len(artifact_var) == 0:
                raise ValueError(f"Invalid slice name {artifact_name}.")
            artifact_safe_names.append(artifact_var)

        self.name = name or "_".join(artifact_safe_names)
        self.id = get_new_id()
        self.output_dir = None

    def export(
        self,
        framework: str = "SCRIPT",
        output_dir: str = ".",
        input_parameters: List[str] = [],
        reuse_pre_computed_artifacts: List[str] = [],
        generate_test: bool = False,
        workflow_dag_config: Optional[Dict] = {},
        include_non_slice_as_comment=False,
    ) -> Path:
        # Check if the specified framework is a supported/valid one
        if framework not in WorkflowType.__members__:
            raise Exception(f"No WorkflowType for {framework}")

        # get artifact_collection for use in workflow writers
        artifact_collection = self._get_artifact_collection(
            input_parameters=input_parameters,
            reuse_pre_computed_artifacts=reuse_pre_computed_artifacts,
            include_non_slice_as_comment=include_non_slice_as_comment,
            dependencies=self.dependencies,
        )

        # Construct workflow writer. Check out class:WorkflowType for supported frameworks
        # If you want to add a new framework, please read the "adding a new workflow writer" tutorial
        workflow_writer = WorkflowWriterFactory.get(
            workflow_type=WorkflowType[framework],
            artifact_collection=artifact_collection,
            workflow_name=self.name,
            output_dir=output_dir,
            generate_test=generate_test,
            dag_config=workflow_dag_config,
            include_non_slice_as_comment=include_non_slice_as_comment,
        )

        # Write out workflow files
        workflow_writer.write_workflow_files()

        # Provide user warning about currently unsupported functionality
        if len(reuse_pre_computed_artifacts) > 0 and framework == "AIRFLOW":
            warnings.warn(
                "Reuse of pre-computed artifacts is currently NOT supported "
                "for Airflow DAGs. Hence, the generated Airflow DAG file would "
                "recompute all artifacts in the workflow."
            )

        # Track the event
        track(
            CreateWorkflowEvent(
                framework,
                len(self.artifact_names),
                len(self.dependencies) > 0,
                workflow_dag_config is not None,
            )
        )

        self.output_dir = workflow_writer.output_dir
        return workflow_writer.output_dir

    def _get_artifact_collection(
        self,
        input_parameters,
        reuse_pre_computed_artifacts,
        dependencies,
        include_non_slice_as_comment,
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
            dependencies=dependencies,
        )

        return artifact_collection

    def save(self):
        """
        Save this workflow to the db using WorkflowORM.
        """
        execution_context = get_context()
        db = execution_context.executor.db
        session_orm = (
            db.session.query(SessionContextORM)
            .order_by(SessionContextORM.creation_time.desc())
            .all()
        )
        if len(session_orm) == 0:
            track(ExceptionEvent(ErrorType.WORKFLOW, "No session found in DB"))
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

        workflow_to_write = WorkflowORM(
            name=self.name,
            artifacts=set(artifacts_to_save.values()),
            dependencies=art_deps_to_save,
        )
        db.write_workflow(art_deps_to_save, workflow_to_write)
