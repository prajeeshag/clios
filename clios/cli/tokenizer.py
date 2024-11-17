from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class TokenError(Exception):
    def __init__(self, token: str = "", pos: int = 0, msg: str = "") -> None:
        self.pos = pos
        self.token = token
        if msg:
            super().__init__(msg)
        else:
            super().__init__()


@dataclass(frozen=True)
class Token(ABC):
    value: str

    @classmethod
    @abstractmethod
    def match(cls, string: str) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class StringToken(Token):
    """A string token will match any string"""

    @classmethod
    def match(cls, string: str) -> bool:
        return True


@dataclass(frozen=True)
class OperatorToken(Token):
    """An operator token will match any string starting with '-'"""

    @classmethod
    def match(cls, string: str) -> bool:
        return string.startswith("-") and not string.startswith("--")


@dataclass(frozen=True)
class LeftBracketToken(Token):
    value: str = "["

    @classmethod
    def match(cls, string: str) -> bool:
        return string == "["


@dataclass(frozen=True)
class RightBracketToken(Token):
    value: str = "]"

    @classmethod
    def match(cls, string: str) -> bool:
        return string == "]"


@dataclass(frozen=True)
class ColonToken(Token):
    value: str = ":"

    @classmethod
    def match(cls, string: str) -> bool:
        return string == ":"


class TokenType(Enum):
    COLON = ColonToken
    LEFT_BRACKET = LeftBracketToken
    RIGHT_BRACKET = RightBracketToken
    OPERATOR = OperatorToken
    STRING = StringToken

    @classmethod
    def _missing_(cls, value: object) -> "TokenType":
        if not isinstance(value, str):
            raise TokenError(msg="Invalid token type")
        for member in cls:
            if member is not cls.STRING and member.value.match(value):
                return member
        # if no match, return STRING
        return cls.STRING


def tokenize(args: list[str]) -> tuple[Token, ...]:
    tokens: list[Token] = []
    for arg in args:
        token = TokenType(arg)
        tokens.append(token.value(arg))
    return tuple(tokens)
