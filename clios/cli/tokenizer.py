import re
from dataclasses import dataclass
from enum import Enum

from clios.core.tokenizer import Token, TokenError, Tokenizer


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
        pattern = r"^-[a-zA-Z]"
        return re.match(pattern, string) is not None


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
            raise TokenError("Invalid token type")
        for member in cls:
            if member.value.match(value) and member is not cls.STRING:
                return member
        # if no match, return STRING
        return cls.STRING


class CliTokenizer(Tokenizer[list[str]]):
    def tokenize(self, input: list[str]) -> tuple[Token, ...]:
        tokens: list[Token] = []
        for arg in input:
            token = TokenType(arg)
            tokens.append(token.value(arg))
        return tuple(tokens)
