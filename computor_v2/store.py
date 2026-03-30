from __future__ import annotations
from computor_v2.errors import ComputorNameError
from computor_v2.builtins import BUILTINS

_RESERVED = frozenset(BUILTINS.keys())


class Store:
    """Case-insensitive variable/function store with built-in fallback layer."""

    def __init__(self):
        self._data: dict[str, object] = {}

    def _key(self, name: str) -> str:
        return name.lower()

    def get(self, name: str) -> object:
        key = self._key(name)
        if key in self._data:
            return self._data[key]
        if key in BUILTINS:
            return BUILTINS[key]
        raise ComputorNameError(f"Undefined variable: '{name}'")

    def set(self, name: str, value: object) -> None:
        key = self._key(name)
        if key in _RESERVED:
            raise ComputorNameError(f"'{name}' is reserved and cannot be assigned")
        self._data[key] = value

    def has(self, name: str) -> bool:
        key = self._key(name)
        return key in self._data or key in BUILTINS

    def __contains__(self, name: str) -> bool:
        return self.has(name)

    def __repr__(self) -> str:
        return f"Store({self._data})"