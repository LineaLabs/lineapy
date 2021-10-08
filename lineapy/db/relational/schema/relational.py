from __future__ import annotations

import json
from datetime import datetime
from typing import Union

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    PickleType,
    String,
    Table,
    UniqueConstraint,
    types,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Boolean, Text

from lineapy.data.types import LiteralType, NodeType, SessionType, ValueType


""" 
This file contains the ORM versions of the graph node in types.py.
  Pydantic allows us to extract out a Dataclass like object from the ORM,
  but not let us directly write to the ORM.


Relationships
-------------

_Warning: non exhaustive_

SessionContext
- Library (One to Many)
- HardwareSpec (Many to One)

Node
- SessionContext (Many to One)

ImportNode
- Library (Many to One)

CallNode
- Node (Many to Many)
"""

Base = declarative_base()


class AttributesDict(types.TypeDecorator):
    # FIXME: missing two inherited abstract methods that
    #        need to be implemented:
    #  - `process_literal_param` from  `TypeDecorator`
    #  - `python_type` from `TypeEngine`.

    impl = Text()
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)

        return value


class SessionContextORM(Base):  # type: ignore
    __tablename__ = "session_context"
    id = Column(String, primary_key=True)
    environment_type = Column(Enum(SessionType))
    creation_time = Column(DateTime)
    working_directory = Column(String)
    session_name = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    hardware_spec = Column(String, nullable=True)
    code = Column(String)


class LibraryORM(Base):  # type: ignore
    __tablename__ = "library"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "name",
            "version",
            "path",
        ),
    )
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("session_context.id"))
    name = Column(String)
    version = Column(String)
    path = Column(String)


class ArtifactORM(Base):  # type: ignore
    __tablename__ = "artifact"
    id = Column(String, ForeignKey("node.id"), primary_key=True)
    name = Column(String, nullable=True)
    date_created = Column(Float, nullable=False)


artifact_project_association_table = Table(
    "artifact_project_association",
    Base.metadata,
    Column("artifact", ForeignKey("artifact.id"), primary_key=True),
    Column("project", ForeignKey("project.id"), primary_key=True),
)


class ProjectORM(Base):  # type: ignore
    __tablename__ = "project"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class ExecutionORM(Base):  # type: ignore
    __tablename__ = "execution"
    artifact_id = Column(String, ForeignKey("artifact.id"), primary_key=True)
    version = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)


class NodeValueORM(Base):  # type: ignore
    __tablename__ = "node_value"
    node_id = Column(String, ForeignKey("node.id"), primary_key=True)
    version = Column(Integer, primary_key=True)
    value = Column(PickleType, nullable=True)
    value_type = Column(Enum(ValueType))
    virtual = Column(Boolean)  # if True, value is not materialized in cache
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)


class BaseNodeORM(Base):  # type: ignore
    __tablename__ = "node"
    id = Column(String, primary_key=True)
    session_id = Column(String)
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

    library_id = Column(String, ForeignKey("library.id"))
    attributes = Column(AttributesDict(), nullable=True)
    alias = Column(String, nullable=True)


# Use associations for many to many relationship between calls and args
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object


class PositionalArgORM(Base):
    __tablename__ = "positional_arg"
    call_node_id: str = Column(
        ForeignKey("call_node.id"), primary_key=True, nullable=False
    )
    arg_node_id: str = Column(
        ForeignKey("node.id"), primary_key=True, nullable=False
    )
    index = Column(Integer, primary_key=True, nullable=False)
    argument = relationship(BaseNodeORM, uselist=False)


class KeywordArgORM(Base):
    __tablename__ = "keyword_arg"
    call_node_id: str = Column(
        ForeignKey("call_node.id"), primary_key=True, nullable=False
    )
    arg_node_id: str = Column(
        ForeignKey("node.id"), primary_key=True, nullable=False
    )
    name = Column(String, primary_key=True, nullable=False)
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

    value_type = Column(Enum(LiteralType))

    @declared_attr  # type: ignore
    def value(cls):
        return BaseNodeORM.__table__.c.get("value", Column(String))


# Explicitly define all subclasses of NodeORM, so that if we use this as a type
# we can accurately know if we cover all cases
NodeORM = Union[LookupNodeORM, ImportNodeORM, CallNodeORM, LiteralNodeORM]
