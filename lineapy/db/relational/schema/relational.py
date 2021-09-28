import json
from datetime import datetime

from sqlalchemy import (
    Column,
    UniqueConstraint,
    Integer,
    String,
    Enum,
    ForeignKey,
    Table,
    DateTime,
    PickleType,
    Float,
    types,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    declared_attr,  # type: ignore
)
from sqlalchemy.sql.sqltypes import Boolean, Float, Text

from lineapy.data.types import (
    SessionType,
    ValueType,
    NodeType,
    StateDependencyType,
    StorageType,
    LiteralType,
)

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

SideEffectsNode
- StateChangeNode (One to Many)
- ImportNode (Many to Many)

ImportNode
- Library (Many to One)

ArgumentNode
- Node (One to One)

CallNode
- ArgumentNode (One to Many)
- ImportNode/CallNode (function_module) (One to One)
- FunctionDefinitionNode (One to One)

LiteralNode
- ValueNode (One to One)

VariableNode
- VariableNode/CallNode (Many to One)

StateChangeNode
- SideEffectsNode (One to One)
- Node (Many to One)
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
    file_name = Column(String)
    working_directory = Column(String)
    session_name = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    hardware_spec = Column(String, nullable=True)
    libraries = relationship("LibraryORM", backref="session")
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
    execution_time = Column(Float)


class NodeValueORM(Base):  # type: ignore
    __tablename__ = "node_value"
    node_id = Column(String, ForeignKey("node.id"), primary_key=True)
    version = Column(Integer, primary_key=True)
    value = Column(PickleType, nullable=True)
    value_type = Column(Enum(ValueType))
    virtual = Column(Boolean)  # if True, value is not materialized in cache
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)


class NodeORM(Base):  # type: ignore
    __tablename__ = "node"
    id = Column(String, primary_key=True)
    session_id = Column(String)
    node_type = Column(Enum(NodeType))
    lineno = Column(Integer, nullable=True)  # line numbers are 1-indexed
    col_offset = Column(Integer, nullable=True)  # col numbers are 0-indexed
    end_lineno = Column(Integer, nullable=True)
    end_col_offset = Column(Integer, nullable=True)

    line = Column(Integer, nullable=True)
    line_end = Column(Integer, nullable=True)
    col_start = Column(Integer, nullable=True)
    col_end = Column(Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_on": node_type,
        "polymorphic_identity": NodeType.Node,
    }


side_effects_output_state_change_association_table = Table(
    "side_effects_output_state_change_association",
    Base.metadata,
    Column(
        "side_effects_node_id",
        ForeignKey("side_effects_node.id"),
        primary_key=True,
    ),
    Column(
        "output_state_change_node_id",
        ForeignKey("state_change_node.id"),
        primary_key=True,
    ),
)

side_effects_input_state_change_association_table = Table(
    "side_effects_input_state_change_association",
    Base.metadata,
    Column(
        "side_effects_node_id",
        ForeignKey("side_effects_node.id"),
        primary_key=True,
    ),
    Column(
        "input_state_change_node_id",
        ForeignKey("state_change_node.id"),
        primary_key=True,
    ),
)

side_effects_import_association_table = Table(
    "side_effects_import_association",
    Base.metadata,
    Column(
        "side_effects_node_id",
        ForeignKey("side_effects_node.id"),
        primary_key=True,
    ),
    Column("import_node_id", ForeignKey("import_node.id"), primary_key=True),
)


class LookupNodeORM(NodeORM):
    __tablename__ = "lookup"
    __mapper_args__ = {"polymorphic_identity": NodeType.LookupNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    name = Column(String, nullable=False)


class SideEffectsNodeORM(NodeORM):
    __tablename__ = "side_effects_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.SideEffectsNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)


class ImportNodeORM(NodeORM):
    __tablename__ = "import_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.ImportNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    library_id = Column(String, ForeignKey("library.id"))
    attributes = Column(AttributesDict(), nullable=True)
    alias = Column(String, nullable=True)


class StateChangeNodeORM(NodeORM):
    __tablename__ = "state_change_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.StateChangeNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    variable_name = Column(String)
    associated_node_id = Column(String)
    initial_value_node_id = Column(String)
    state_dependency_type = Column(Enum(StateDependencyType))


call_node_association_table = Table(
    "call_node_association",
    Base.metadata,
    Column("call_node_id", ForeignKey("call_node.id"), primary_key=True),
    Column(
        "argument_node_id", ForeignKey("argument_node.id"), primary_key=True
    ),
)


class CallNodeORM(NodeORM):
    __tablename__ = "call_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.CallNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)
    # FIXME: add ForeignKey("node.id") back in!!!!
    function_id = Column(String, nullable=False)
    # function_module = Column(String, nullable=True)
    # locally_defined_function_id = Column(String, nullable=True)

    # this pattern is used when multiple sibling classes have the same column
    # @declared_attr
    # def assigned_variable_name(cls):
    #     return NodeORM.__table__.c.get(
    #         "assigned_variable_name", Column(String, nullable=True)
    #     )
    # @declared_attr
    # def function_name(cls):
    #     return NodeORM.__table__.c.get("function_name", Column(String))


class ArgumentNodeORM(NodeORM):
    __tablename__ = "argument_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.ArgumentNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    keyword = Column(String, nullable=True)
    positional_order = Column(Integer, nullable=True)
    value_literal = Column(String, nullable=True)
    value_literal_type = Column(Enum(LiteralType), nullable=True)

    @declared_attr
    def value_node_id(cls):
        return NodeORM.__table__.c.get("value_node_id", Column(String))


class LiteralNodeORM(NodeORM):
    __tablename__ = "literal_assign_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.LiteralNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    value_type = Column(Enum(LiteralType))

    @declared_attr
    def assigned_variable_name(cls):
        return NodeORM.__table__.c.get(
            "assigned_variable_name", Column(String, nullable=True)
        )

    @declared_attr
    def value(cls):
        return NodeORM.__table__.c.get("value", Column(String))

    # @declared_attr
    # def value_node_id(cls):
    #     return NodeORM.__table__.c.get("value_node_id", Column(String))


class FunctionDefinitionNodeORM(SideEffectsNodeORM):
    __tablename__ = "function_definition_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.FunctionDefinitionNode}

    id = Column(String, ForeignKey("side_effects_node.id"), primary_key=True)

    @declared_attr
    def value(cls):
        return NodeORM.__table__.c.get("value", Column(String))

    @declared_attr
    def function_name(cls):
        return NodeORM.__table__.c.get("function_name", Column(String))


class VariableNodeORM(NodeORM):
    __tablename__ = "variable_alias_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.VariableNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    source_node_id = Column(String)
    assigned_variable_name = Column(String, nullable=True)


class LoopNodeORM(SideEffectsNodeORM):
    __tablename__ = "loop_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.LoopNode}

    id = Column(String, ForeignKey("side_effects_node.id"), primary_key=True)


class ConditionNodeORM(SideEffectsNodeORM):
    __tablename__ = "condition_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.ConditionNode}

    id = Column(String, ForeignKey("side_effects_node.id"), primary_key=True)


class DataSourceNodeORM(NodeORM):
    __tablename__ = "data_source_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.DataSourceNode}

    id = Column(String, ForeignKey("node.id"), primary_key=True)

    storage_type = Column(Enum(StorageType))
    access_path = Column(String)
    name = Column(String, nullable=True)
