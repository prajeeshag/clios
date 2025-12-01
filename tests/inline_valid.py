from clios.cli.app import operator


@operator(implicit="input")
def op_1i(i: int):
    pass
