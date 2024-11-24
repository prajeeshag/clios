import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass


class TokenError(Exception):
    pass


@dataclass(frozen=True)
class Token(ABC):
    value: str

    @classmethod
    @abstractmethod
    def match(cls, string: str) -> bool: ...  # pragma: no cover


INPUT = t.TypeVar("INPUT")


class Tokenizer[INPUT](ABC):
    @abstractmethod
    def tokenize(self, input: INPUT) -> tuple[Token, ...]: ...  # pragma: no cover
