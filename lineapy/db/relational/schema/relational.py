""" Relationships
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

LiteralAssignNode
- ValueNode (One to One)

VariableAliasNode
- VariableAliasNode/CallNode (Many to One)

ConditionNode
- Node (Many to Many)

StateChangeNode
- SideEffectsNode (One to One)
- Node (Many to One)

"""

import json
from datetime import datetime
from uuid import UUID

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
    types,
)
from sqlalchemy.dialects.mysql.base import MSBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    declared_attr,
)
from sqlalchemy.sql.sqltypes import Boolean, Text

from lineapy.data.types import (
    SessionType,
    NodeType,
    StorageType,
    LiteralType,
)

Base = declarative_base()

###############
# base tables #
###############

# from https://stackoverflow.com/questions/183042/how-can-i-use-uuids-in-sqlalchemy
class LineaID(types.TypeDecorator):
    impl = MSBinary
    cache_ok = True  # this surppress an error from SQLAlchemy

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, UUID):
            return value.bytes
        elif value and not isinstance(value, UUID):
            raise ValueError("value %s is not a valid UUID" % value)
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            return UUID(bytes=value)
        else:
            return None

    def is_mutable(self):
        return False


class AttributesDict(types.TypeDecorator):

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


class SessionContextORM(Base):
    __tablename__ = "session_context"
    id = Column(LineaID, primary_key=True)
    environment_type = Column(Enum(SessionType))
    creation_time = Column(DateTime)
    file_name = Column(String)
    session_name = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    hardware_spec = Column(String, nullable=True)
    libraries = relationship("LibraryORM", backref="session")


class LibraryORM(Base):
    __tablename__ = "library"
    __table_args__ = (UniqueConstraint("session_id", "name", "version", "path"),)
    id = Column(LineaID, primary_key=True)
    session_id = Column(LineaID, ForeignKey("session_context.id"))
    name = Column(String)
    version = Column(String)
    path = Column(String)


class ArtifactORM(Base):
    __tablename__ = "artifact"
    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)
    context = Column(LineaID, ForeignKey("session_context.id"))
    value_type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    project = Column(String, nullable=True)
    description = Column(String, nullable=True)
    date_created = Column(String)
    code = Column(LineaID, nullable=True)


# one to many
code_token_association_table = Table(
    "code_token_association",
    Base.metadata,
    Column("code", ForeignKey("code.id"), primary_key=True),
    Column("token", ForeignKey("token.id"), primary_key=True),
)

# CodeORM and TokenORM are temporary, to be used for integration testing of intermediates

# CodeORM is derived from an Artifact, and used for the frontend Code objects that hold
# intermediate values (Tokens)
class CodeORM(Base):
    __tablename__ = "code"
    id = Column(LineaID, primary_key=True)
    text = Column(String)


# TokenORMs should be derived from existing NodeValueORMs, representing intermediates
# for the CodeView to handle
class TokenORM(Base):
    __tablename__ = "token"
    id = Column(LineaID, primary_key=True)
    line = Column(Integer)
    start = Column(Integer)
    end = Column(Integer)
    intermediate = Column(LineaID)  # points to a NodeValueORM


class ExecutionORM(Base):
    __tablename__ = "execution"
    artifact_id = Column(LineaID, ForeignKey("artifact.id"), primary_key=True)
    version = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)


class NodeValueORM(Base):
    __tablename__ = "node_value"
    node_id = Column(LineaID, ForeignKey("node.id"), primary_key=True)
    version = Column(Integer, primary_key=True)
    value = Column(PickleType, nullable=True)
    virtual = Column(Boolean)  # if True, value is not materialized in cache


class NodeORM(Base):
    __tablename__ = "node"

    id = Column(LineaID, primary_key=True)
    code = Column(String, nullable=True)
    session_id = Column(LineaID)
    node_type = Column(Enum(NodeType))

    __mapper_args__ = {
        "polymorphic_on": node_type,
        "polymorphic_identity": NodeType.Node,
    }


side_effects_state_change_association_table = Table(
    "side_effects_state_change_association",
    Base.metadata,
    Column(
        "side_effects_node_id", ForeignKey("side_effects_node.id"), primary_key=True
    ),
    Column(
        "state_change_node_id", ForeignKey("state_change_node.id"), primary_key=True
    ),
)

side_effects_import_association_table = Table(
    "side_effects_import_association",
    Base.metadata,
    Column(
        "side_effects_node_id", ForeignKey("side_effects_node.id"), primary_key=True
    ),
    Column("import_node_id", ForeignKey("import_node.id"), primary_key=True),
)


class SideEffectsNodeORM(NodeORM):

    __tablename__ = "side_effects_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.SideEffectsNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)


class ImportNodeORM(NodeORM):

    __tablename__ = "import_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.ImportNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)

    library_id = Column(LineaID, ForeignKey("library.id"))
    attributes = Column(AttributesDict(), nullable=True)
    alias = Column(String, nullable=True)


class StateChangeNodeORM(NodeORM):
    __tablename__ = "state_change_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.StateChangeNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)

    variable_name = Column(String)
    associated_node_id = Column(LineaID)
    initial_value_node_id = Column(LineaID)


call_node_association_table = Table(
    "call_node_association",
    Base.metadata,
    Column("call_node_id", ForeignKey("call_node.id"), primary_key=True),
    Column("argument_node_id", ForeignKey("argument_node.id"), primary_key=True),
)


class CallNodeORM(NodeORM):
    __tablename__ = "call_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.CallNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)

    function_module = Column(LineaID, nullable=True)
    locally_defined_function_id = Column(LineaID, nullable=True)

    # this pattern is used when multiple sibling classes have the same column
    @declared_attr
    def assigned_variable_name(cls):
        return NodeORM.__table__.c.get(
            "assigned_variable_name", Column(String, nullable=True)
        )

    @declared_attr
    def function_name(cls):
        return NodeORM.__table__.c.get("function_name", Column(String))


class ArgumentNodeORM(NodeORM):
    __tablename__ = "argument_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.ArgumentNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)

    keyword = Column(String, nullable=True)
    positional_order = Column(Integer, nullable=True)
    value_literal = Column(String, nullable=True)
    value_literal_type = Column(Enum(LiteralType), nullable=True)

    @declared_attr
    def value_node_id(cls):
        return NodeORM.__table__.c.get("value_node_id", Column(LineaID))


class LiteralAssignNodeORM(NodeORM):
    __tablename__ = "literal_assign_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.LiteralAssignNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)

    value_type = Column(Enum(LiteralType))

    @declared_attr
    def assigned_variable_name(cls):
        return NodeORM.__table__.c.get(
            "assigned_variable_name", Column(String, nullable=True)
        )

    @declared_attr
    def value(cls):
        return NodeORM.__table__.c.get("value", Column(String))

    @declared_attr
    def value_node_id(cls):
        return NodeORM.__table__.c.get("value_node_id", Column(LineaID))


class FunctionDefinitionNodeORM(SideEffectsNodeORM):
    __tablename__ = "function_definition_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.FunctionDefinitionNode}

    id = Column(LineaID, ForeignKey("side_effects_node.id"), primary_key=True)

    @declared_attr
    def value(cls):
        return NodeORM.__table__.c.get("value", Column(String))

    @declared_attr
    def function_name(cls):
        return NodeORM.__table__.c.get("function_name", Column(String))


class VariableAliasNodeORM(NodeORM):
    __tablename__ = "variable_alias_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.VariableAliasNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)

    source_variable_id = Column(LineaID)


class LoopNodeORM(SideEffectsNodeORM):
    __tablename__ = "loop_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.LoopNode}

    id = Column(LineaID, ForeignKey("side_effects_node.id"), primary_key=True)


condition_association_table = Table(
    "condition_association",
    Base.metadata,
    Column("condition_node_id", ForeignKey("condition_node.id"), primary_key=True),
    Column("dependent_node_id", ForeignKey("node.id"), primary_key=True),
)


class ConditionNodeORM(SideEffectsNodeORM):
    __tablename__ = "condition_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.ConditionNode}

    id = Column(LineaID, ForeignKey("side_effects_node.id"), primary_key=True)


class DataSourceNodeORM(NodeORM):
    __tablename__ = "data_source_node"
    __mapper_args__ = {"polymorphic_identity": NodeType.DataSourceNode}

    id = Column(LineaID, ForeignKey("node.id"), primary_key=True)

    storage_type = Column(Enum(StorageType))
    access_path = Column(String)
    name = Column(String, nullable=True)
