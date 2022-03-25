from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class GlobalsDict(Dict[str, object]):
    """
    A custom dict that is meant to be accessed in a particular way, in order
    to record getitems. It is used for setting as the globals when execing some
    code, so we can try to understand which globals were accessed.

    It is meant to be used like:

    1. Instantiate it empty like `GlobalsDict()`
    2. Call `setup_globals(d)` to update it with the input globals
    3. Execute some code that uses it as globals, which will call `__setitem__`
       as well as our custom `__getitem__`.
    4. Call `teardown_globals()` which will return the `Result`, containing the
       a record of all the original globals that were accessed and any new
       globals that were updated or added.

    We cannot overload the `__setitem__` method, since Python will not respect
    it for custom globals, but we can overload the __getitem__ method.

    See https://stackoverflow.com/a/12185315/907060
    which refers to https://bugs.python.org/issue14385
    """

    def __init__(self):
        self._state: Optional[State] = None
        super().__init__()

    def __getitem__(self, k):
        v = super().__getitem__(k)
        if not self._state:
            raise RuntimeError("GlobalsDict not setup")
        self._state.process_getitem(k, v)
        return v

    def setup_globals(self, inputs: Dict[str, object]) -> None:
        self._state = State(inputs)
        self.update(inputs)
        self["__builtins__"] = builtins

    def teardown_globals(self) -> GlobalsDictResult:
        if not self._state:
            raise RuntimeError("GlobalsDict not setup")
        state = self._state
        # Calculate what globals have changed or have been added. Compare by pointer,
        # not by value, since we want to see if the global variable has been re-assigned
        # not if the value has been mutated
        changed_globals = {
            k: v
            for k, v, in self.items()
            if k != "__builtins__"
            and (
                # The global was changed if it is new, i.e. was not in the our variables
                k not in state.inputs
                # Or if it is different
                or state.inputs[k] is not v
            )
        }

        self._state = None
        self.clear()

        return GlobalsDictResult(state.accessed_inputs, changed_globals)


@dataclass
class State:
    # The mapping of input globals
    inputs: Dict[str, object]

    # A subset of the input globals, containing only the keys that were accessed
    # from it
    accessed_inputs: List[str] = field(default_factory=list)

    def process_getitem(self, k: str, v: object) -> None:
        """
        If we haven't recorded this key and its value is the same as the value
        in the input globals (meaning we haven't overwritten it), then record
        it as a getitem.
        """
        if (
            k != "__builtins__"
            and k not in self.accessed_inputs
            and k in self.inputs
            and self.inputs[k] is v
        ):
            self.accessed_inputs.append(k)


@dataclass
class GlobalsDictResult:
    accessed_inputs: List[str]
    added_or_modified: Dict[str, object]
