from dataclasses import dataclass
from typing import Optional, Union

# I think amplitude doesn't really support nested objects,
# so flattening the object here.


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
    # TODO: set error_type to be string enums
    error_type: str
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


AllEvents = Union[
    CatalogEvent,
    LibImportEvent,
    ExceptionEvent,
    GetEvent,
    SaveEvent,
    ToPipelineEvent,
    GetCodeEvent,
    GetValueEvent,
    GetVersionEvent,
]
