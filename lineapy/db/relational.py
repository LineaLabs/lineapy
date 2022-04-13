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
from typing import Union

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    creation_time = Column(DateTime)
    working_directory = Column(String)
    session_name = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    hardware_spec = Column(String, nullable=True)
    execution_id = Column(String, ForeignKey("execution.id"))


class ArtifactORM(Base):
    """
    An artifact is a named pointer to a node.
    """

    __tablename__ = "artifact"
    node_id: LineaID = Column(String, ForeignKey("node.id"), primary_key=True)
    execution_id: LineaID = Column(
        String, ForeignKey("execution.id"), primary_key=True
    )
    name = Column(
        String,
        nullable=False,
        default=ARTIFACT_NAME_PLACEHOLDER,
        primary_key=True,
    )
    date_created = Column(DateTime, nullable=False)
    version = Column(String, nullable=False, primary_key=True)

    node: BaseNodeORM = relationship(
        "BaseNodeORM", uselist=False, lazy="joined", innerjoin=True
    )
    execution: ExecutionORM = relationship(
        "ExecutionORM", uselist=False, lazy="joined", innerjoin=True
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
    # The value of the literal serilaized as a string
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


# Explicitly define all subclasses of NodeORM, so that if we use this as a type
# we can accurately know if we cover all cases
NodeORM = Union[
    LookupNodeORM,
    ImportNodeORM,
    CallNodeORM,
    LiteralNodeORM,
    MutateNodeORM,
    GlobalNodeORM,
]
