from typing import TypedDict

from pydantic import ValidationError


class TokenError(Exception):
    def __init__(self, token: str = "", pos: int = 0, msg: str = "") -> None:
        self.pos = pos
        self.token = token
        if msg:
            super().__init__(msg)
        else:
            super().__init__()


class CliosError(Exception):
    class CliosErrorCtx(TypedDict, total=False):
        token_index: int
        unchainable_token_index: int
        expected_num_args: int
        arg_key: str
        arg_index: int
        validation_error: ValidationError

    def __init__(self, msg: str = "", ctx: CliosErrorCtx = {}) -> None:
        self.ctx = ctx
        super().__init__(msg)
