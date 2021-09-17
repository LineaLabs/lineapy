from typing import List
from operator import *  # Keep unused import for transitive import by Executor

# NOTE: previous attempt at some import issues with the operator model
#   from operator import *


def __build_list__(*items) -> List:
    return list(items)
