import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass


class TokenError(Exception):
    def __init__(self, message: str, token: str = "", pos: int = 0) -> None:
        self.pos = pos
        self.token = token
        self.message = message
        super().__init__(message)


@dataclass(frozen=True)
class Token(ABC):
    value: str

    @classmethod
    @abstractmethod
    def match(cls, string: str) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.value


INPUT = t.TypeVar("INPUT")


class Tokenizer[INPUT](ABC):
    @abstractmethod
    def tokenize(self, input: INPUT) -> tuple[Token, ...]:
        raise NotImplementedError
