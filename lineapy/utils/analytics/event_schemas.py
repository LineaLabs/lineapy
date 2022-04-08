from dataclasses import dataclass
from typing import List, Union


@dataclass
class LibInfo:
    name: str
    version: str


@dataclass
class SaveGetParam:
    side_effect: str  # "file_system", "db", or "" (for variables)


@dataclass
class ToPipelineParam:
    engine: str  # AIRFLOW, SCRIPT


AllParams = Union[SaveGetParam, ToPipelineParam]


@dataclass
class LineapyAPIEvent:
    # TODO: we can have more rigorous typing later...
    event: str  # save, get, catalog, to_pipeline
    params: AllParams  #


@dataclass
class LibInfoEvent:
    libs: List[LibInfo]

@dataclass
class ExceptionEvent:
    error: str

AllEvents = Union[LineapyAPIEvent, LibInfoEvent, ExceptionEvent]
