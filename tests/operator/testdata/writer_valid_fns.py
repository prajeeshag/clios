# type: ignore

from clio.operator import Writer as W

passing = []


def fp00(i: int, c): ...


passing += [W(fp00, int, 1)]


def fp01(i: str, c, b, d): ...


passing += [W(fp01, str, 3)]


def fp02(i: str): ...


passing += [W(fp02, str)]
