# copied from linea-server
# TODO match this up with the new in-memory objects

from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    backref,
    relationship,
    declarative_mixin,
    declared_attr,
)
from sqlalchemy.sql.sqltypes import Boolean


class Tables:
    CALL_TABLE_NAME = "calls"

    ASSET_PREVIEW_TABLE_NAME = "asset_preview"

    ARTIFACT_TABLE_NAME = "artifacts"

    DATA_ASSET_TABLE_NAME = "data_assets"

    ASSIGNMENT_TABLE_NAME = "assignments"

    LIBRARY_VERSION_TABLE_NAME = "library_versions"

    ARGUMENT_TABLE_NAME = "argument"

    FUNCTION_TABLE_NAME = "function"

    SESSION_TABLE_NAME = "session"

    # Web tables
    USER_TABLE_NAME = "users"
    PROJECT_TABLE_NAME = "projects"
    REPORT_TABLE_NAME = "reports"

    # relationship tables
    PROJECT_ARTIFACT_TABLE_NAME = "project_artifact_relation"

    REPORT_ARTIFACT_TABLE_NAME = "report_artifact_relation"
    REPORT_COMMENT_TABLE_NAME = "report_comments"
    ARTIFACT_COMMENT_TABLE_NAME = "artifact_comments"
    USER_VIEW_TABLE_NAME = "user_views"
    USER_EDIT_TABLE_NAME = "user_edits"

    ARTIFACT_ACTIVE_INTERMEDIATE_TABLE_NAME = "artifact_active_intermediates"

    SCHEDULE_SPECIFICATION_TABLE_NAME = "schedule_specifications"
    SCHEDULED_RUN_TABLE_NAME = "scheduled_runs"
    RUN_STATUS_TABLE_NAME = "run_statuses"


Base = declarative_base()


###############
# base tables #
###############


@declarative_mixin
class DateCreatedMixin:
    @declared_attr
    def date_created(cls):
        return Column(DateTime, default=datetime.utcnow)


@declarative_mixin
class FileMixin:
    """ """

    local_file_path = Column(String, nullable=True)
    remote_file_path = Column(String, nullable=True)


class AssetPreview(FileMixin, Base):
    """
    Currently supported data types:
      png (for charts from e.g., Matplotlib)
      csv (for table preview)
      html (for vega related)
    """

    __tablename__ = Tables.ASSET_PREVIEW_TABLE_NAME
    asset_preview_id = Column(Integer, primary_key=True, autoincrement=True)


class DataAsset(Base):
    """
    Assets are all cloudpickled, except for the ones that are JUST visuals with no backing Python (in which case both the local and remote files will be empty). Though Doris seems to suggest that there is a Python correspondence for all objects.
    """

    __tablename__ = Tables.DATA_ASSET_TABLE_NAME
    asset_id = Column(Integer, primary_key=True)
    # I don't think assets needs name now that they are linked with the assignments and other things
    # name = Column(String)
    data_type = Column(String)
    asset_preview_id = Column(Integer, ForeignKey(AssetPreview.asset_preview_id))
    file_link = Column(String)
    serialization_time_ms = Column(Integer)
    file_size_kb = Column(Integer)


class Function(Base):
    """
    Note that the functions should be unique if they are in the same session. At write time, we will search if it's already defined.
    Some example values:
    - "module": "sklearn.ensemble._forest",
    - "name": "RandomForestClassifier"
    """

    __tablename__ = Tables.FUNCTION_TABLE_NAME
    function_id = Column(Integer, primary_key=True, autoincrement=True)
    module = Column(String, nullable=True)
    name = Column(String, nullable=True)
    # call_id = Column(Integer, ForeignKey(Call.call_id))
    # call = relationship("Call")


class Session(Base):
    """
    Each call happens in a Python session, which is associated with library dependencies.
    """

    __tablename__ = Tables.SESSION_TABLE_NAME
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)


class Call(Base):
    """
    Each row in the `Call` corresponds to each invocation of the function.
    LineaPy will provide the ID (crytographically unique).
     we can look into performance optimization later (e.g. to remove tracking inside loops)
    """

    __tablename__ = Tables.CALL_TABLE_NAME
    call_id = Column(String, primary_key=True)
    session_id = Column(Integer, ForeignKey(Session.session_id))
    start_time = Column(DateTime)
    duration_in_ms = Column(Integer)
    # the hash value of a call
    call_hash = Column(String)
    # its either an assignment or a call result
    # using relationship here to avoid having to flush after every function insertion
    #   see https://dev.to/zchtodd/sqlalchemy-performance-anti-patterns-and-their-fixes-4bmm
    #   and https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html
    # function_id = Column(String, ForeignKey(Function.function_id))
    return_asset_id = Column(Integer, ForeignKey(DataAsset.asset_id), nullable=True)
    data_asset = Column(Integer, ForeignKey(DataAsset.asset_id), nullable=True)
    # artifact_id = Column(Integer, ForeignKey(Artifact.artifact_id))
    arguments = relationship(Tables.ARGUMENT_TABLE_NAME)
    artifact = relationship(
        Tables.ARTIFACT_TABLE_NAME,
        backref=backref(Tables.CALL_TABLE_NAME, uselist=False),
    )


@declarative_mixin
class LiteralValueMixin:
    """
    There are quite a few different ways to have a value in Python:
    - literal_value
    - asset_id_value
    TODO: at insertion time, check that literals and asset_ids do NOT have attribute set
    NOTE
    - We need declared_attr for those with Foreign keys.
    - Note that for attributes, we are just going to compress them into a string for now.
    """

    literal_value = Column(
        String, nullable=True
    )  # this is a json version of the values

    @declared_attr
    def asset_id_value(cls):
        return Column(Integer, ForeignKey(DataAsset.asset_id), nullable=True)


@declarative_mixin
class DerivedValueMixin:
    """
    DerivedValueMixin is different from  LiteralValueMixin in that the latter is raw values
    - assignment_id_value
      - attribute
    - call_result_value
      - attribute
    TODO: sync with Rolando about how he is thinking about attribute.
    `DerivedValueMixin` and `LiteralValueMixin` together compose of
       all the ways that we can have values
    """

    @declared_attr
    def call_result_value(cls):
        return Column(Integer, ForeignKey(Call.call_id), nullable=True)

    @declared_attr
    def assignment_id_value(cls):
        return Column(Integer, ForeignKey(Assignment.assignment_id), nullable=True)


class Assignment(DateCreatedMixin, LiteralValueMixin, Base):
    """
    TODO
    """

    __tablename__ = Tables.ASSIGNMENT_TABLE_NAME
    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    variable_name = Column(String)
    user_timestamp = Column(DateTime)
    call_result_value = Column(Integer, ForeignKey(Call.call_id), nullable=True)


class Argument(LiteralValueMixin, DerivedValueMixin, Base):
    """
    https://docs.sqlalchemy.org/en/14/orm/declarative_mixins.html#composing-mapped-hierarchies-with-mixins
    """

    __tablename__ = Tables.ARGUMENT_TABLE_NAME

    # this is the call associated with the argument
    call_id = Column(Integer, ForeignKey(Call.call_id), primary_key=True)

    # this is for keyword arguments
    keyword = Column(String, nullable=True, primary_key=True)
    # this if for positional arguments
    positional_order = Column(Integer, nullable=True, primary_key=True)


class LibraryVersion(Base):
    """
    This captures the library dependencies.
    Still depends on https://github.com/LineaLabs/tracer/issues/91 to be implemented before this information could be stored.
    """

    __tablename__ = Tables.LIBRARY_VERSION_TABLE_NAME
    session_id = Column(Integer, ForeignKey(Session.session_id), primary_key=True)
    # We need the libraries and their versions because its not recorded in the
    library = Column(String, primary_key=True)
    # TODO: discuss, maybe we want better types for versions.
    version = Column(String)


class Artifact(DateCreatedMixin, Base):
    """
    The creation of an artifact an annotation on top of either a variable or an unnamed call result (the latter should be less likely but we will support it anyways).
    """

    __tablename__ = Tables.ARTIFACT_TABLE_NAME
    artifact_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey(Session.session_id))
    name = Column(String)
    assignment_id = Column(Integer, ForeignKey(Assignment.assignment_id), nullable=True)
    call_id = Column(Integer, ForeignKey(Call.call_id), nullable=True)


"""
Helper tables
  TODO: We need to coordinate what needs to be synced to a remote server. Maybe all the artifacts needs an additional field that describes if its has been uploaded? Need to discuss.
"""

"""
DERIVED TABLES
- these tables hold eagerly computed information (could be re-computed from the log) that's useful for quick queries, such as metadata search and caching:
  - data source
  - 
TODO:
- we will add this later once the basic parts are done
- we also need to discuss who is going to own the graph IR piece, here or in the Python piece.
"""

"""
External data for other parts of the platform
"""


class User(DateCreatedMixin, Base):
    """
    TODO: we probably will need to add some login mechanism
    """

    __tablename__ = Tables.USER_TABLE_NAME

    user_id = Column(String, primary_key=True)
    # the above should be their email
    display_name = Column(String)


class Project(DateCreatedMixin, Base):
    """
    A project is a way to organize different artifacts
    TODO: we probably want better ways to keep track of versions. Maybe a general key-value structure for all the user edited strings?
    """

    __tablename__ = Tables.PROJECT_TABLE_NAME
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey(User.user_id))
    name = Column(String)
    description = Column(String)


"""
Note that we are not using relationship here, but directly the associations table to improve performance since we just want to insert the IDs directly.
"""
ProjectArtifact = Table(
    Tables.PROJECT_ARTIFACT_TABLE_NAME,
    Base.metadata,
    Column(
        "artifact_id",
        Integer,
        ForeignKey(f"{Tables.ARTIFACT_TABLE_NAME}.artifact_id"),
    ),
    Column(
        "project_id", Integer, ForeignKey(f"{Tables.PROJECT_TABLE_NAME}.project_id")
    ),
)


class Report(Base):
    """
    Reports are used for gathering together artifacts into a report
    """

    __tablename__ = Tables.REPORT_TABLE_NAME

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey(User.user_id))


"""
TODO: coordinate the layout encoding with Joyce
"""
ReportArtifact = Table(
    Tables.REPORT_ARTIFACT_TABLE_NAME,
    Base.metadata,
    Column(
        "artifact_id",
        Integer,
        ForeignKey(f"{Tables.ARTIFACT_TABLE_NAME}.artifact_id"),
    ),
    Column("report_id", Integer, ForeignKey(f"{Tables.REPORT_TABLE_NAME}.report_id")),
    Column("layout_x", Integer),
    Column("layout_y", Integer),
    Column("layout_width", Integer),
)


class ItemsIdMixin:
    @declared_attr
    def project_id(cls):
        return Column(Integer, ForeignKey(Project.project_id), nullable=True)

    @declared_attr
    def report_id(cls):
        return Column(Integer, ForeignKey(Report.report_id), nullable=True)

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey(User.user_id), nullable=False)


class UserViews(ItemsIdMixin, DateCreatedMixin, Base):
    __tablename__ = Tables.USER_VIEW_TABLE_NAME
    user_view_id = Column(Integer, primary_key=True, autoincrement=True)


class UserEdit(ItemsIdMixin, DateCreatedMixin, Base):
    __tablename__ = Tables.USER_EDIT_TABLE_NAME

    user_edit_id = Column(Integer, primary_key=True, autoincrement=True)


@declarative_mixin
class CommentMixin:
    """
    Comment values shared in different types of comments
    """

    # not sure if we need the following, but keeping it for now.
    is_resolved = Column(Boolean)

    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey(User.user_id))

    @declared_attr
    def commend_id(cls):
        return Column(Integer, primary_key=True, autoincrement=True)


class ReportComment(CommentMixin, Base):
    """
    TODO: in the future we need to add permissions, which involves user groups
    """

    __tablename__ = Tables.REPORT_COMMENT_TABLE_NAME
    report_id = Column(Integer, ForeignKey(Report.report_id))


class ArtifactComment(CommentMixin, Base):
    """
    Different people could comment on different part
    """

    __tablename__ = Tables.ARTIFACT_COMMENT_TABLE_NAME
    artifact_id = Column(Integer, ForeignKey(Artifact.artifact_id))


# the following is for scheduling


class ScheduleSpecification(Base):
    """
    This could be either artifact or report, and we would then have to calculate which one to use if the artifact one needs to be over-written.
    TODO: figure out how to add ENUM support for dbs
    """

    __tablename__ = Tables.SCHEDULE_SPECIFICATION_TABLE_NAME

    user_id = Column(Integer, ForeignKey(User.user_id), primary_key=True)
    report_id = Column(Integer, ForeignKey(Report.report_id), primary_key=True)
    artifact_id = Column(Integer, ForeignKey(Artifact.artifact_id), primary_key=True)
    # this would be either week, month, or year
    frequency = Column(String)
    skip = Column(Integer)
    day_of_the_week = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)


class ScheduledRun(Base):
    """
    This is the runs that are actually scheduled. Running window for the next seven days.
    TODO: have a scheduler run through this.
    """

    __tablename__ = Tables.SCHEDULED_RUN_TABLE_NAME
    run_id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(Integer, ForeignKey(Artifact.artifact_id))
    time = Column(DateTime)


class RunStatus(Base):
    """
    For every run, report if there was a problem
    """

    __tablename__ = Tables.RUN_STATUS_TABLE_NAME
    run_id = Column(Integer, ForeignKey(ScheduledRun.run_id), primary_key=True)
    duration_ms = Column(Integer)
    error_info = Column(String, nullable=True)
