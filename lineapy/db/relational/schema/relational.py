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

from lineapy.data.types import SessionType, NodeType


Base = declarative_base()

###############
# base tables #
###############

LineaID = UUID

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
    # libraries = Column(ARRAY(Library), nullable=True)


class NodeORM(Base):
    __tablename__ = "node"
    __mapper_args__ = {"polymorphic_identity": "node"}
    id = Column(LineaID, primary_key=True)
    code = Column(String, nullable=True)
    session_id = Column(LineaID)
    node_type = Column(Enum(NodeType))


# class SideEffectsNodeORM(NodeORM):
#     __mapper_args__ = {"polymorphic_identity": "side_effects_node"}

#     state_change_nodes = Column(ARRAY(LineaID), nullable=True)
#     import_nodes = Column(ARRAY(LineaID), nullable=True)


# TODO: dictionary typing in SQLAlchemy
# class ImportNodeORM(NodeORM):
#     __mapper_args__ = {"polymorphic_identity": "import_node"}

#     node_type = Column(Enum(NodeType), default=NodeType.ImportNode)
#     code = Column(String)
#     library = Column(Library)
#     attributes = Column(nullable=True)
#     alias = Column(String, nullable=True)
#     module = Column(Any, nullable=True)


class ArgumentNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": "argument_node"}

    keyword = Column(String, nullable=True)
    positional_order = Column(Integer, nullable=True)
    value_node_id = Column(LineaID, nullable=True)
    value_literal = Column(Integer, nullable=True)
    value_pickled = Column(String, nullable=True)


class CallNodeORM(NodeORM):
    __mapper_args__ = {"polymorphic_identity": "call_node"}

    arguments = Column(PickleType)
    function_name = Column(String)
    function_module = Column(LineaID, nullable=True)
    locally_defined_function_id = Column(LineaID, nullable=True)
    assigned_variable_name = Column(String, nullable=True)
    value = Column(String, nullable=True)

    # @declared_attr
    # def assigned_variable_name(cls):
    #     return NodeORM.__table__.c.get(
    #         "assigned_variable_name", Column(String, nullable=True)
    #     )


# class LiteralAssignNodeORM(NodeORM):
#     __mapper_args__ = {"polymorphic_identity": "literal_assign_node"}

#     value = Column(String)
#     value_node_id = Column(LineaID, nullable=True)

#     @declared_attr
#     def assigned_variable_name(cls):
#         return NodeORM.__table__.c.get(
#             "assigned_variable_name", Column(String, nullable=True)
#         )


# class FunctionDefinitionNodeORM(SideEffectsNodeORM):
#     __mapper_args__ = {"polymorphic_identity": "function_definition_node"}

#     function_name = Column(String)
#     value = Column(Any, nullable=True)


# class ConditionNodeORM(SideEffectsNodeORM):
#     __mapper_args__ = {"polymorphic_identity": "condition_node"}

#     node_type = Column(Enum(NodeType), default=NodeType.ConditionNode)
#     dependent_variables_in_predicate = Column(ARRAY(LineaID), nullable=True)


class DirectedEdgeORM(Base):
    __tablename__ = "directed_edge"
    id = Column(LineaID, primary_key=True)
    source_node_id = Column(LineaID)
    sink_node_id = Column(LineaID)
