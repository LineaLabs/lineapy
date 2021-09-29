from typing import List, Optional
from operator import *  # Keep unused import for transitive import by Executor

# NOTE: previous attempt at some import issues with the operator model
#   from operator import *


def __build_list__(*items) -> List:
    return list(items)


def __assert__(v: object, message: Optional[str] = None) -> None:
    if message is None:
        assert v
    else:
        assert v, message
