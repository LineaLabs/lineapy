from functools import cached_property
from typing import Any, Optional

from lineapy.data.types import ValueType

"""
User exposed APIs.
Should keep it very clean.
"""

class LineaArtifact:
    """
    LineaArtifact exposes functionalities we offer around the artifact.
    The current list is:
    - code
    - value
    """

    def __init__(self):
        pass

    @cached_property
    def code(self) -> str:
        pass

    @cached_property
    def value(self) -> Any:
        pass

    @cached_property
    def versions(self):
        pass

class LineaCatalog:
    """
    """
    def __init__(self) -> None:
        pass

    def list_artifacts(self, filter_type: Optional[ValueType]=None, include_versions=False):


