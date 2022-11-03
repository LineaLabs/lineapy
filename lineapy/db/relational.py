"""
This file contains the ORM versions of the graph node in types.py.
  Pydantic allows us to extract out a Dataclass like object from the ORM,
  but not let us directly write to the ORM.


Relationships
-------------

Warning
-------

non exhaustive list


SessionContext
- ImportNode (One to Many)
- HardwareSpec (Many to One)

Node
- SessionContext (Many to One)

CallNode
- Node (Many to Many)
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Union

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table

from lineapy.data.types import (
    LineaID,
    LiteralType,
    NodeType,
    SessionType,
    ValueType,
)
from lineapy.utils.constants import ARTIFACT_NAME_PLACEHOLDER

Base = declarative_base()


class SessionContextORM(Base):
    __tablename__ = "session_context"
    id = Column(String, primary_key=True)
    environment_type = Column(Enum(SessionType))
    python_version = Column(String)
    creation_time = Column(DateTime)
    working_directory = Column(String)
    session_name = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    hardware_spec = Column(String, nullable=True)
    execution_id = Column(String, ForeignKey("execution.id"))


artifact_to_pipeline_table = Table(
    "artifact_to_pipeline",
    Base.metadata,
    Column("pipeline_id", ForeignKey("pipeline.id")),
    Column("artifact_id", ForeignKey("artifact.id")),
)

dependency_to_artifact_table = Table(
    "dependency_to_artifact_table",
    Base.metadata,
    Column("dependency_id", ForeignKey("dependency.id")),
    Column("artifact_id", ForeignKey("artifact.id")),
)


class ArtifactORM(Base):
    """
    An artifact is a named pointer to a node.
    """

    __tablename__ = "artifact"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id: LineaID = Column(String, ForeignKey("node.id"), nullable=False)
    execution_id: LineaID = Column(
        String, ForeignKey("execution.id"), nullable=False
    )

    name = Column(
        String,
        nullable=False,
        default=ARTIFACT_NAME_PLACEHOLDER,
    )
    date_created = Column(DateTime, nullable=False)
    version = Column(Integer, nullable=False)

    node: BaseNodeORM = relationship(
        "BaseNodeORM", uselist=False, lazy="joined", innerjoin=True
    )
    execution: ExecutionORM = relationship(
        "ExecutionORM", uselist=False, lazy="joined", innerjoin=True
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "version", name="_unique_artifact_name_and_version"
        ),
        UniqueConstraint(
            "name",
            "node_id",
            "execution_id",
            "version",
            name="_unique_artifact_name_for_a_node_id_and_exec_id",
        ),
    )


class MLflowArtifactMetadataORM(Base):
    __tablename__ = "mlflow_artifact_storage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(Integer, ForeignKey("artifact.id"), nullable=False)
    backend = Column(String, nullable=False)
    tracking_uri = Column(String, nullable=False)
    registry_uri = Column(String, nullable=True)
    model_uri = Column(String, nullable=False)
    model_flavor = Column(String, nullable=False)
    delete_time = Column(DateTime, nullable=True)


class PipelineORM(Base):
    __tablename__ = "pipeline"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    artifacts = relationship(
        ArtifactORM, secondary=artifact_to_pipeline_table, collection_class=set
    )
    dependencies: List[ArtifactDependencyORM] = relationship(
        "ArtifactDependencyORM",
        back_populates="pipeline",
    )


class ArtifactDependencyORM(Base):
    __tablename__ = "dependency"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(Integer, ForeignKey("pipeline.id"), nullable=False)
    pipeline = relationship(
        PipelineORM, back_populates="dependencies", uselist=False
    )
    post_artifact_id = Column(
        Integer, ForeignKey("artifact.id"), nullable=False
    )
    post_artifact = relationship(
        ArtifactORM,
        uselist=False,
        foreign_keys=[post_artifact_id],
    )
    pre_artifacts = relationship(
        ArtifactORM,
        secondary=dependency_to_artifact_table,
        collection_class=set,
    )


class ExecutionORM(Base):
    """
    An execution represents one Python interpreter invocation of some number of nodes
    """

    __tablename__ = "execution"
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)


class NodeValueORM(Base):
    """
    A node value represents the value of a node during some execution.

    It is uniquely identified by the `node_id` and `execution_id`.

    The following invariant holds:
    `value.node.session == value.execution.session`
    """

    __tablename__ = "node_value"
    node_id = Column(String, ForeignKey("node.id"), primary_key=True)
    execution_id = Column(String, ForeignKey("execution.id"), primary_key=True)
    value = Column(String, nullable=True)
    value_type = Column(Enum(ValueType))

    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)


class BaseNodeORM(Base):
    """
    node.source_code has a path value if node.session.environment_type == "script"
    otherwise the environment type is "jupyter" and it has a jupyter execution
    count and session id, which is equal to the node.session

    NOTE
    ----

    - Because other nodes are inheriting from BaseNodeORM, finding a node
      based on its id is easy (something like the following)::

       session.query(BaseNodeORM).filter(BaseNodeORM.id == linea_id)

    - Each node inheriting from BaseNodeORM must have non null values for
      all of lineno, col_offset, end_lineno, end_col_offset and source_code_id
      or nulls for all of them.

    """

    __tablename__ = "node"
    id = Column(String, primary_key=True)
    session_id: LineaID = Column(String)
    node_type = Column(Enum(NodeType))
    lineno = Column(Integer, nullable=True)  # line numbers are 1-indexed
    col_offset = Column(Integer, nullable=True)  # col numbers are 0-indexed
    end_lineno = Column(Integer, nullable=True)
    end_col_offset = Column(Integer, nullable=True)
    control_dependency = Column(String, ForeignKey("node.id"), nullable=True)
    source_code_id = Column(
        String, ForeignKey("source_code.id"), nullable=True
    )
    source_code: SourceCodeORM = relationship("SourceCodeORM", lazy="joined")

    __table_args__ = (
        # Either all source keys or none should be specified
        CheckConstraint(
            "(lineno IS NULL) = (col_offset is NULL) and "
            "(col_offset is NULL) = (end_lineno is NULL) and "
            "(end_lineno is NULL) = (end_col_offset is NULL) and "
            "(end_col_offset is NULL) = (source_code_id is NULL)"
        ),
    )
    # https://docs.sqlalchemy.org/en/14/orm/inheritance.html#joined-table-inheritance
    __mapper_args__ = {
        "polymorphic_on": node_type,
        "polymorphic_identity": NodeType.Node,
    }


class SourceCodeORM(Base):
    __tablename__ = "source_code"

    id = Column(String, primary_key=True)
    code = Column(String)

    path = Column(String, nullable=True)
    jupyter_execution_count = Column(Integer, nullable=True)
    jupyter_session_id = Column(String, nullable=True)

    __table_args__ = (
        # Either path is set or jupyter_execution_count and jupyter_session_id are set
        CheckConstraint(
            "(path IS NOT NULL) != ((jupyter_execution_count IS NOT NULL) AND "
            "(jupyter_execution_count IS NOT NULL))"
        ),
        # If one jupyter arg is provided, both must be
        CheckConstraint(
            "(jupyter_execution_count IS NULL) = (jupyter_session_id is NULL)"
        ),
    )


class LookupNodeORM(BaseNodeORM):
    __tablename__ = "lookup"
    __mapper_args__ = {"polymorphic_identity": NodeType.LookupNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    name = Column(String, nullable=False)


class ImportNodeORM(BaseNodeORM):
    __tablename__ = "import_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.ImportNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)
    name = Column(String)
    package_name = Column(String, nullable=True)
    version = Column(String, nullable=True)
    path = Column(String, nullable=True)


# Use associations for many to many relationship between calls and args
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object


class PositionalArgORM(Base):
    __tablename__ = "positional_arg"
    call_node_id: str = Column(
        ForeignKey("call_node.id"), primary_key=True, nullable=False
    )
    arg_node_id: LineaID = Column(
        ForeignKey("node.id"), primary_key=True, nullable=False
    )
    starred: bool = Column(Boolean, nullable=False, default=False)
    index = Column(Integer, primary_key=True, nullable=False)
    argument = relationship(BaseNodeORM, uselist=False)


class KeywordArgORM(Base):
    __tablename__ = "keyword_arg"
    call_node_id: str = Column(
        ForeignKey("call_node.id"), primary_key=True, nullable=False
    )
    arg_node_id: LineaID = Column(
        ForeignKey("node.id"), primary_key=True, nullable=False
    )
    starred: bool = Column(Boolean, nullable=False, default=False)
    name: str = Column(String, primary_key=True, nullable=False)
    argument = relationship(BaseNodeORM, uselist=False)


class GlobalReferenceORM(Base):
    __tablename__ = "global_reference"
    call_node_id: str = Column(
        ForeignKey("call_node.id"), primary_key=True, nullable=False
    )
    variable_node_id: str = Column(
        ForeignKey("node.id"), primary_key=True, nullable=False
    )
    variable_name = Column(String, primary_key=True, nullable=False)
    variable_node = relationship(BaseNodeORM, uselist=False)


class ImplicitDependencyORM(Base):
    __tablename__ = "implicit_dependency"
    call_node_id: str = Column(
        ForeignKey("call_node.id"), primary_key=True, nullable=False
    )
    arg_node_id: str = Column(
        ForeignKey("node.id"), primary_key=True, nullable=False
    )
    index = Column(Integer, primary_key=True, nullable=False)
    argument = relationship(BaseNodeORM, uselist=False)


class CallNodeORM(BaseNodeORM):
    __tablename__ = "call_node"

    id = Column(String, ForeignKey("node.id"), primary_key=True)
    function_id = Column(String, ForeignKey("node.id"))

    positional_args = relationship(
        PositionalArgORM, collection_class=set, lazy="joined"
    )
    keyword_args = relationship(
        KeywordArgORM, collection_class=set, lazy="joined"
    )
    global_reads = relationship(
        GlobalReferenceORM, collection_class=set, lazy="joined"
    )

    implicit_dependencies = relationship(
        ImplicitDependencyORM,
        collection_class=set,
        lazy="joined",
    )

    __mapper_args__ = {
        "polymorphic_identity": NodeType.CallNode,
        # Need this so that sqlalchemy doesn't get confused about additional
        # foreign key from function_id
        # https://stackoverflow.com/a/39518177/907060
        "inherit_condition": id == BaseNodeORM.id,
    }


class LiteralNodeORM(BaseNodeORM):
    __tablename__ = "literal_assign_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.LiteralNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    value_type: LiteralType = Column(Enum(LiteralType))
    # The value of the literal serialized as a string
    value: str = Column(String, nullable=False)


class MutateNodeORM(BaseNodeORM):
    __tablename__ = "mutate_node"

    id = Column(String, ForeignKey("node.id"), primary_key=True)
    source_id = Column(String, ForeignKey("node.id"))
    call_id = Column(String, ForeignKey("node.id"))

    __mapper_args__ = {
        "polymorphic_identity": NodeType.MutateNode,
        "inherit_condition": id == BaseNodeORM.id,
    }


class GlobalNodeORM(BaseNodeORM):
    __tablename__ = "global_node"

    id = Column(String, ForeignKey("node.id"), primary_key=True)
    name = Column(String)
    call_id = Column(String, ForeignKey("node.id"))

    __mapper_args__ = {
        "polymorphic_identity": NodeType.GlobalNode,
        "inherit_condition": id == BaseNodeORM.id,
    }


class IfNodeORM(BaseNodeORM):
    __tablename__ = "if_node"

    id = Column(String, ForeignKey("node.id"), primary_key=True)
    test_id = Column(String, ForeignKey("node.id"))
    companion_id = Column(String, ForeignKey("node.id"))
    unexec_id = Column(String, ForeignKey("literal_assign_node.id"))

    __mapper_args__ = {
        "polymorphic_identity": NodeType.IfNode,
        "inherit_condition": id == BaseNodeORM.id,
    }


class ElseNodeORM(BaseNodeORM):
    __tablename__ = "else_node"

    id = Column(String, ForeignKey("node.id"), primary_key=True)
    companion_id = Column(String, ForeignKey("node.id"))
    unexec_id = Column(String, ForeignKey("literal_assign_node.id"))

    __mapper_args__ = {
        "polymorphic_identity": NodeType.ElseNode,
        "inherit_condition": id == BaseNodeORM.id,
    }


# Explicitly define all subclasses of NodeORM, so that if we use this as a type
# we can accurately know if we cover all cases
NodeORM = Union[
    LookupNodeORM,
    ImportNodeORM,
    CallNodeORM,
    LiteralNodeORM,
    MutateNodeORM,
    GlobalNodeORM,
    IfNodeORM,
    ElseNodeORM,
]


class VariableNodeORM(Base):

    __tablename__ = "assigned_variable_node"
    id = Column(String, primary_key=True)
    # Warlus operator can assign to multiple variables at the same node,  so need two primary keys
    variable_name: str = Column(String, nullable=False, primary_key=True)
