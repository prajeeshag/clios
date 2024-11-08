from typing import Any, Callable


class TokenError(Exception):
    def __init__(self, token: str = "", pos: int = 0, msg: str = "") -> None:
        self.pos = pos
        self.token = token
        if msg:
            super().__init__(msg)
        else:
            super().__init__()


class OperatorNotFound(Exception):
    def __init__(self, operator: str) -> None:
        self.operator = operator


class InvalidFunction(Exception):
    def __init__(
        self,
        msg: object,
        fn: Callable[..., Any] | None = None,
        pname: str = "",
    ) -> None:
        self.fn = fn
        self.pname = pname
        super().__init__(msg)


class InvalidArguments(Exception):
    pass


class ChainTypeError(Exception):
    def __init__(
        self,
        upstream_op: str,
        downstream_op: str,
        expected_type: type,
        received_type: type,
    ):
        self.upstream_op = upstream_op
        self.downstream_op = downstream_op
        self.expected_type = expected_type
        self.received_type = received_type
