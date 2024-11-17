from typing import Hashable

from .core.operator_fn import OperatorFn


class KeyExistsError(Exception):
    def __init__(self, key: Hashable):
        super().__init__(f"Key '{key}' already exists. Reassignment is not allowed.")
        self.key = key


class _Registry[K, O]:
    def __init__(self) -> None:
        self._db: dict[K, O] = {}

    def get(self, key: K) -> O:
        return self._db[key]

    def add(self, key: K, obj: O) -> None:
        if key in self._db:
            raise KeyExistsError(key)
        self._db[key] = obj

    def has_key(self, key: K) -> bool:
        return key in self._db

    def items(self):
        return self._db.items()


class OperatorRegistry(_Registry[str, OperatorFn]):
    pass
