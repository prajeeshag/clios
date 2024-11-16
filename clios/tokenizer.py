import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple, TypeGuard

from .exceptions import TokenError


@dataclass(frozen=True)
class Token(ABC):
    value: str

    @classmethod
    @abstractmethod
    def match(cls, string: str) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.value


class KWd(NamedTuple):
    key: str
    val: str


class Params(NamedTuple):
    args: tuple[str, ...]
    kwds: tuple[KWd, ...]


@dataclass(frozen=True)
class OperatorToken(Token):
    name: str = field(init=False)
    args: tuple[str, ...] = field(init=False)
    kwds: tuple[KWd, ...] = field(init=False)

    @classmethod
    def match(cls, string: str) -> bool:
        pattern = re.compile(r"^-[a-zA-Z](\w+)(\,(\S)*)*\,?")
        return bool(pattern.fullmatch(string))

    def __post_init__(self):
        string = self.value
        argList = list(self.value.split(","))
        name = argList.pop(0).strip("-")
        args: list[str] = []
        kwds: list[KWd] = []
        for arg in argList[:]:
            if "=" in arg:
                try:
                    k, v = arg.split("=")  # Should split to 2 items
                except ValueError:
                    raise TokenError(
                        string, pos=string.index(arg), msg="Invalid parameter"
                    )
                if not v:
                    raise TokenError(
                        string, pos=string.index(arg), msg="Invalid parameter"
                    )
                if k in dict(kwds):
                    raise TokenError(
                        string, pos=string.index(arg), msg="Parameter already assigned"
                    )

                kwds.append(KWd(k, v))
            else:
                if len(kwds) != 0:
                    raise TokenError(
                        string,
                        pos=string.index(arg),
                        msg="Positional parameter after keyword parameter is not allowed",
                    )

                args.append(arg)

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "args", tuple(args))
        object.__setattr__(self, "kwds", tuple(kwds))


@dataclass(frozen=True)
class StringToken(Token):
    @classmethod
    def match(cls, string: str) -> bool:
        pattern = re.compile(r"(^[^\-\s].*$)|(^-\d+(\.\d+)?$)")
        return bool(pattern.fullmatch(string))


@dataclass(frozen=True)
class NoneToken(Token):
    @classmethod
    def match(cls, string: str) -> bool:
        return False


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
    INVALID = NoneToken

    @classmethod
    def _missing_(cls, value: object) -> "TokenType":
        if not isinstance(value, str):
            return cls.INVALID
        for member in cls:
            if member.value.match(value):
                return member
        return cls.INVALID


def is_operator_token(val: object) -> TypeGuard["OperatorToken"]:
    return isinstance(val, OperatorToken)


def tokenize(args: list[str]) -> tuple[Token, ...]:
    tokens: list[Token] = []
    for arg in args:
        token = TokenType(arg)
        if token is TokenType.INVALID:
            raise TokenError(arg, msg="Unknown pattern")
        tokens.append(token.value(arg))
    return tuple(tokens)
