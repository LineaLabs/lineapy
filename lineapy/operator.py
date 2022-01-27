from lineapy.global_context import GlobalContext


class BaseOperator:
    _context_manager: GlobalContext

    # def __post_init__(self, context_manager: GlobalContext):
    #     # this is dumb but trying out for now
    #     self._context_manager = context_manager  # LineaGlobalContext()

    @property
    def context_manager(self) -> GlobalContext:
        return self._context_manager

    @context_manager.setter
    def context_manager(self, c_manager: GlobalContext) -> None:
        self._context_manager = c_manager
