from typing import TypedDict

from pydantic import ValidationError

from .cli.tokenizer import Token


class CliosError(Exception):
    class CliosErrorCtx(TypedDict, total=False):
        token: Token
        unchainable_token: Token
        validation_error: ValidationError

    def __init__(self, msg: str = "", ctx: CliosErrorCtx = {}) -> None:
        self.ctx = ctx
        super().__init__(msg)


class ParserError(CliosError):
    pass


class OperatorError(CliosError):
    pass
