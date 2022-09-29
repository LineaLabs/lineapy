from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

# I think amplitude doesn't really support nested objects,
# so flattening the object here.


class ErrorType(Enum):
    SAVE = "save_API_exception"
    DELETE = "delete_API_exception"
    RETRIEVE = "retrieve_API_exception"
    PIPELINE = "pipeline_API_exception"
    DATABASE = "database_error"
    USER = "user_exception"

    def __str__(self):
        return str(self.value)


@dataclass
class SaveEvent:
    side_effect: str  # "file_system", "db", or "" (for variables)


@dataclass
class GetEvent:
    version_specified: bool


@dataclass
class CatalogEvent:
    catalog_size: int


@dataclass
class ToPipelineEvent:
    engine: str  # AIRFLOW, SCRIPT
    artifact_count: int
    has_task_dependency: bool
    has_config: bool


@dataclass
class LibImportEvent:
    name: str
    version: str


@dataclass
class ExceptionEvent:
    error_type: ErrorType
    error_msg: Optional[str] = None


@dataclass
class GetValueEvent:
    has_value: bool


@dataclass
class GetCodeEvent:
    use_lineapy_serialization: bool
    is_session_code: bool


@dataclass
class GetVersionEvent:
    dummy_entry: str  # just a dummy entry for now


@dataclass
class CyclicGraphEvent:
    dummy_entry: str  # dummy entry, may populate with extra information later


@dataclass
class TagEvent:
    tag: str  # dummy entry, may populate with extra information later


TrackingEvent = Union[
    CatalogEvent,
    LibImportEvent,
    ExceptionEvent,
    GetEvent,
    SaveEvent,
    ToPipelineEvent,
    GetCodeEvent,
    GetValueEvent,
    GetVersionEvent,
    CyclicGraphEvent,
    TagEvent,
]
