# type: ignore


def e_args(fn):
    res = []
    docstring = fn.__doc__.split("\n")
    res.append(docstring[0].strip())
    res.append(fn)
    if len(docstring) > 3:
        res.append(docstring[2].strip())
    return tuple(res)


def list_functions(current_module, startswith):
    ff_functions = [
        getattr(current_module, func)
        for func in dir(current_module)
        if func.startswith(startswith) and callable(getattr(current_module, func))
    ]
    return ff_functions
