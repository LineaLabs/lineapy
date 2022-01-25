from dataclasses import dataclass, field
from typing import Optional

from lineapy.global_context import GlobalContext


@dataclass
class BaseOperator:
    _context_manager: Optional[GlobalContext] = field(init=False)

    # def __post_init__(self, c_manager: GlobalContext = None):
    #     # this is dumb but trying out for now
    #     self._context_manager = c_manager  # LineaGlobalContext()

    @property
    def context_manager(self) -> Optional[GlobalContext]:
        return self._context_manager

    @context_manager.setter
    def context_manager(self, c_manager: GlobalContext) -> None:
        self._context_manager = c_manager
