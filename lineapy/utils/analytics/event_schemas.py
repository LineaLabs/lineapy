from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class LibInfo:
    name: str
    version: str


@dataclass
class SaveParam:
    side_effect: str  # "file_system", "db", or "" (for variables)


@dataclass
class GetParam:
    version_specified: bool


@dataclass
class ToPipelineParam:
    engine: str  # AIRFLOW, SCRIPT
    artifact_count: int
    has_task_dependency: bool
    has_config: bool


AllParams = Union[GetParam, SaveParam, ToPipelineParam]


@dataclass
class LineapyAPIEvent:
    # TODO: we can have more rigorous typing later...
    event: str  # save, get, catalog, to_pipeline, to_code
    params: Optional[AllParams] = None


@dataclass
class LibInfoEvent:
    libs: List[LibInfo]


@dataclass
class ExceptionEvent:
    error: str


AllEvents = Union[LineapyAPIEvent, LibInfoEvent, ExceptionEvent]
