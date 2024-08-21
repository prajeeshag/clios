import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, TypeGuard

from clio.exceptions import TokenError


class ArgumentToken(ABC):
    @classmethod
    @abstractmethod
    def factory(cls, string: str) -> "ArgumentToken | None":
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class LeftSquareBracket(ArgumentToken):
    @classmethod
    def factory(cls, string: str) -> ArgumentToken | None:
        if string == "[":
            return cls()
        return None

    def __str__(self) -> str:
        return "["


@dataclass(frozen=True)
class RightSquareBracket(ArgumentToken):
    @classmethod
    def factory(cls, string: str) -> ArgumentToken | None:
        if string == "]":
            return cls()
        return None

    def __str__(self) -> str:
        return "]"


@dataclass(frozen=True)
class Colon(ArgumentToken):
    @classmethod
    def factory(cls, string: str) -> ArgumentToken | None:
        if string == ":":
            return cls()
        return None

    def __str__(self) -> str:
        return ":"


def is_operator_token(val: object) -> TypeGuard["OperatorToken"]:
    return isinstance(val, OperatorToken)


@dataclass(frozen=True)
class OperatorToken(ArgumentToken):
    name: str
    params: tuple[str, ...] = ()
    kwparams: tuple[tuple[str, str], ...] = ()

    def __str__(self) -> str:
        args = ",".join(self.params)
        kwds = ",".join([f"{k}={v}" for k, v in self.kwparams])
        res = "-" + self.name
        if args:
            res += "," + args
        if kwds:
            res += "," + kwds
        return res

    @classmethod
    def factory(cls, string: str) -> ArgumentToken | None:
        pattern = re.compile(r"^-(\w\w+)(\,(\S)*)*\,?")
        if not bool(pattern.fullmatch(string)):
            return None

        argList = list(string.split(","))
        name = argList.pop(0).lstrip("-")
        params: list[str] = []
        kwparams: list[tuple[str, str]] = []
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
                if k in dict(kwparams):
                    raise TokenError(
                        string, pos=string.index(arg), msg="Parameter already assigned"
                    )

                kwparams.append((k, v))
            else:
                if len(kwparams) != 0:
                    raise TokenError(
                        string,
                        pos=string.index(arg),
                        msg="Positional parameter after keyword parameter is not allowed",
                    )

                params.append(arg)
        return OperatorToken(name, tuple(params), tuple(kwparams))


@dataclass(frozen=True)
class FilePathToken(ArgumentToken):
    path: str

    @classmethod
    def factory(cls, string: str) -> ArgumentToken | None:
        pattern = re.compile(r"(^[^\-\s\[\]\:].*$)|(^-\d+(\.\d+)?$)")
        if bool(pattern.fullmatch(string)):
            return FilePathToken(string)
        return None

    def __str__(self) -> str:
        return self.path


class Tokenizer:
    def __init__(self, token_classes: list[Type[ArgumentToken]]) -> None:
        self._token_classes = token_classes

    def tokenize(self, arg: str) -> ArgumentToken:
        for token_class in self._token_classes:
            token = token_class.factory(arg)
            if token is not None:
                return token
        raise TokenError(arg, msg="Unknown pattern")
