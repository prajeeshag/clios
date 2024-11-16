class TokenError(Exception):
    def __init__(self, token: str = "", pos: int = 0, msg: str = "") -> None:
        self.pos = pos
        self.token = token
        if msg:
            super().__init__(msg)
        else:
            super().__init__()
