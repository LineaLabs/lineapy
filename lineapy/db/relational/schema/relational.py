# TODO Create ORM for the objects defined in `linea.dataflow.data_types`
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Table,
    PickleType,
    DateTime,
    types,
)
from sqlalchemy.dialects.mysql.base import MSBinary
from sqlalchemy.dialects.postgresql import ARRAY, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    backref,
    relationship,
    declarative_mixin,
    declared_attr,
)
from sqlalchemy.sql.sqltypes import Boolean

from lineapy.data.types import SessionType, NodeType, StorageType, LiteralType


Base = declarative_base()

###############
# base tables #
###############

# from https://stackoverflow.com/questions/183042/how-can-i-use-uuids-in-sqlalchemy
class LineaID(types.TypeDecorator):
    impl = MSBinary

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, UUID):
            return value.bytes
        elif value and not isinstance(value, UUID):
            raise (ValueError, "value %s is not a valid UUID" % value)
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            return UUID(bytes=value)
        else:
            return None

    def is_mutable(self):
        return False


class SessionContextORM(Base):
    __tablename__ = "session_context"
    id = Column(LineaID, primary_key=True)
    environment_type = Column(Enum(SessionType))
    creation_time = Column(DateTime)
    file_name = Column(String)
    session_name = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    hardware_spec = Column(String, nullable=True)
    libraries = Column(PickleType, nullable=True)


# TODO: spec out artifact table
class ArtifactORM(Base):
    __tablename__ = "artifact"
    id = Column(LineaID, primary_key=True)


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


class DirectedEdgeORM(Base):
    __tablename__ = "directed_edge"
    source_node_id = Column(LineaID, primary_key=True)
    sink_node_id = Column(LineaID, primary_key=True)


class SideEffectsNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.SideEffectsNode}

    state_change_nodes = Column(PickleType, nullable=True)
    import_nodes = Column(PickleType, nullable=True)


# TODO: dictionary typing in SQLAlchemy
class ImportNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.ImportNode}

    library = Column(PickleType)
    attributes = Column(PickleType, nullable=True)
    alias = Column(String, nullable=True)


class ArgumentNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.ArgumentNode}

    keyword = Column(String, nullable=True)
    positional_order = Column(Integer, nullable=True)
    value_literal = Column(String, nullable=True)
    value_literal_type = Column(Enum(LiteralType), nullable=True)
    value_pickled = Column(PickleType, nullable=True)

    @declared_attr
    def value_node_id(cls):
        return NodeORM.__table__.c.get("value_node_id", Column(LineaID))


class CallNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.CallNode}

    arguments = Column(PickleType)
    function_module = Column(LineaID, nullable=True)
    locally_defined_function_id = Column(LineaID, nullable=True)

    @declared_attr
    def assigned_variable_name(cls):
        return NodeORM.__table__.c.get(
            "assigned_variable_name", Column(String, nullable=True)
        )

    @declared_attr
    def function_name(cls):
        return NodeORM.__table__.c.get("function_name", Column(String))


class LiteralAssignNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.LiteralAssignNode}

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


class StateChangeNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.StateChangeNode}

    variable_name = Column(String)
    associated_node_id = Column(LineaID)
    initial_value_node_id = Column(LineaID)


class FunctionDefinitionNodeORM(SideEffectsNodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.FunctionDefinitionNode}

    @declared_attr
    def value(cls):
        return NodeORM.__table__.c.get("value", Column(String))

    @declared_attr
    def function_name(cls):
        return NodeORM.__table__.c.get("function_name", Column(String))


class VariableAliasNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.VariableAliasNode}

    source_variable_id = Column(LineaID)


class LoopNodeORM(SideEffectsNodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.LoopNode}


class ConditionNodeORM(SideEffectsNodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.ConditionNode}

    dependent_variables_in_predicate = Column(PickleType, nullable=True)


class DataSourceNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": NodeType.DataSourceNode}

    storage_type = Column(Enum(StorageType))
    access_path = Column(String)
    name = Column(String, nullable=True)
