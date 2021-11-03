class RecordGetitemDict(dict):
    """
    A custom dict that records which keys have been succesfully accessed.

    We cannot overload the `__setitem__` method, since Python will not respect
    it for custom globals, but we can overload the __getitem__ method.

    See https://stackoverflow.com/a/12185315/907060
    which refers to https://bugs.python.org/issue14385
    """

    def __init__(self, *args, **kwargs):
        self._getitems: list[str] = []
        super().__init__(*args, **kwargs)

    def __getitem__(self, k):
        r = super().__getitem__(k)
        if k not in self._getitems:
            self._getitems.append(k)
        return r

    def clear(self) -> None:
        self._getitems = []
        return super().clear()
