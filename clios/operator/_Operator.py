import inspect
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import Annotated, Any, Callable, get_args, get_origin

from ..exceptions import InvalidArguments, InvalidFunction
from ._Reader import Reader
from ._utils import inspect_function, type2str

# Others should pass Readers
_BASE_DATA_READERS = {
    str: Reader(lambda x: x, str),
    int: Reader(int, int),
    float: Reader(float, float),
}

_EMPTY = inspect.Parameter.empty


@dataclass(frozen=True)
class _Input:
    dtypes: tuple[type, ...]
    var_tuple: bool = False
    var_list: bool = False

    def __post_init__(self):
        if self.var_tuple and self.var_list:
            raise TypeError("Class _Input: cannot be both var_tuple and var_list")
        if len(self.dtypes) < 1:
            raise TypeError("Class _Input: dtypes size cannot be Zero")
        if self.is_variadic and len(self.dtypes) > 1:
            raise TypeError(
                "Class _Input: if var_tuple or var_list cannot have multiple input types"
            )

    @property
    def is_variadic(self) -> bool:
        return self.var_list or self.var_tuple

    @property
    def len(self) -> int:
        return len(self.dtypes)


@dataclass(frozen=True)
class _Param:
    name: str
    dtype: type
    data_reader: Reader
    default: object = _EMPTY


@dataclass(frozen=True)
class BaseOperator:
    fn: Callable[..., object | None]
    output_type: type
    args: tuple[_Param, ...] = ()
    var_arg: _Param | None = None
    required_kwargs: tuple[_Param, ...] = ()
    optional_kwargs: tuple[_Param, ...] = ()
    var_kwarg: _Param | None = None

    @cached_property
    def num_args(self) -> int:
        return len(self.args)

    def get_arg(self, n: int) -> _Param:
        if n < self.num_args:
            return self.args[n]
        elif self.var_arg:
            return self.var_arg
        raise IndexError(f"No argument at position [{n}]")

    @cached_property
    def optional_kwarg_keys(self) -> tuple[str, ...]:
        return tuple(x.name for x in self.optional_kwargs)

    @cached_property
    def required_kwarg_keys(self) -> tuple[str, ...]:
        return tuple(x.name for x in self.required_kwargs)

    def get_kwarg(self, key: str) -> _Param:
        def get_key(obj: _Param) -> bool:
            return obj.name == key

        if key in self.optional_kwarg_keys:
            return next(filter(get_key, self.optional_kwargs))
        if key in self.required_kwarg_keys:
            return next(filter(get_key, self.required_kwargs))
        if self.var_kwarg:
            return self.var_kwarg
        raise KeyError(f"No keyword argument with key [{key}]")

    def load_kwargs(self, kwds: dict[str, str]) -> dict[str, object]:
        self._validate_kwargs(kwds)
        pkwds: dict[str, object] = {
            k: self.get_kwarg(k).data_reader(kwds[k]) for k in kwds
        }
        return pkwds

    def load_args(self, args: tuple[str, ...]) -> tuple[object, ...]:
        self._validate_args(args)
        pargs: tuple[object, ...] = tuple(
            self.get_arg(i).data_reader(args[i]) for i in range(len(args))
        )
        return pargs

    def _validate_args(self, args: tuple[str, ...]):
        if self.var_arg:
            if len(args) < self.num_args:
                raise InvalidArguments(
                    f"Expected at least {self.num_args} argument(s), got {len(args)}"
                )
        else:
            if len(args) != self.num_args:
                raise InvalidArguments(
                    f"Expected {self.num_args} argument(s), got {len(args)}"
                )

    def _validate_kwargs(self, kwds: dict[str, str]):
        for k in self.required_kwarg_keys:
            if k not in kwds:
                raise InvalidArguments(f"Missing required keyword argument [{k}]")

        for k in kwds:
            if (
                not self.var_kwarg
                and k not in self.required_kwarg_keys
                and k not in self.optional_kwarg_keys
            ):
                raise InvalidArguments(f"Got an unexpected keyword argument [{k}]")


@dataclass(frozen=True)
class Generator(BaseOperator):
    def __call__(self, *args: object, **kwds: object) -> object:
        output: object = self.fn(*args, **kwds)
        if not isinstance(output, self.output_type):
            raise TypeError(
                f"Expected <{type2str(self.output_type)}> but received"
                + f" <{type2str(type(output))}> from function <{self.fn.__name__}>"
            )
        return output


@dataclass(frozen=True)
class Operator(BaseOperator):
    _: KW_ONLY
    input: _Input

    def num_input(self):
        return

    def __call__(
        self, input: tuple[object, ...], *args: object, **kwds: object
    ) -> object:
        output: object
        if self.input.len == 1 and not self.input.is_variadic:
            output = self.fn(input[0], *args, **kwds)
        elif self.input.var_list:
            output = self.fn(list(input), *args, **kwds)
        else:
            output = self.fn(input, *args, **kwds)

        if not isinstance(output, self.output_type):
            raise TypeError(
                f"Expected <{type2str(self.output_type)}> but received"
                + f" <{type2str(type(output))}> from function <{self.fn.__name__}>"
            )
        return output


def operator_factory(fn: Callable[..., object]) -> Operator | Generator:
    _, params, output_type = inspect_function(fn)

    if output_type is None or output_type is type(None):
        raise InvalidFunction("Return type cannot be 'None'", fn)

    try:
        isinstance("", output_type)
    except Exception:
        raise InvalidFunction(f"Type <{type2str(output_type)}> is not supported", fn)

    input = None
    args: list[_Param] = []
    var_arg: _Param | None = None
    required_kwargs: list[_Param] = []
    optional_kwargs: list[_Param] = []
    var_kwarg: _Param | None = None

    for i, param in enumerate(params):
        if param[1] is None:
            raise InvalidFunction("Should have valid type annotation", fn, param[0])

        if param[0] == "input":
            if i > 0:
                raise InvalidFunction(
                    "If present, the 'input' parameter should be the first parameter",
                    fn,
                )
            if param[2] is not _EMPTY:
                raise InvalidFunction(
                    "The name 'input' is reserved for the `input` parameter and cannot used as an optional parameter",
                    fn,
                )
            input = _input_factory(fn, param[1])
        elif param[0].startswith("**"):
            var_kwarg = _param_factory(fn, *param)
        elif param[0].startswith("*"):
            if optional_kwargs:
                raise InvalidFunction(
                    "Variadic positional arguments should be before keyword-arguments",
                    fn,
                    param[0],
                )
            var_arg = _param_factory(fn, *param)
        elif param[2] is _EMPTY and not var_arg:
            args.append(_param_factory(fn, *param))
        elif param[2] is _EMPTY:
            required_kwargs.append(_param_factory(fn, *param))
        else:
            optional_kwargs.append(_param_factory(fn, *param))

    if input:
        return Operator(
            fn,
            output_type,
            tuple(args),
            var_arg,
            tuple(required_kwargs),
            tuple(optional_kwargs),
            var_kwarg,
            input=input,
        )
    return Generator(
        fn,
        output_type,
        tuple(args),
        var_arg,
        tuple(required_kwargs),
        tuple(optional_kwargs),
        var_kwarg,
    )


def _param_factory(
    fn: Callable[..., object], pname: str, ptype: Any, default: object
) -> _Param:
    name = pname
    data_reader = None

    torigin = get_origin(ptype)
    dtype = ptype
    if torigin is Annotated:
        targs = get_args(ptype)
        dtype = targs[0]
        for m in targs[1:]:
            if isinstance(m, Reader):
                data_reader = m
                break
    elif ptype in _BASE_DATA_READERS:
        dtype = ptype
        data_reader = _BASE_DATA_READERS[ptype]
    if data_reader is None:
        _base_types = "(" + ",".join(map(type2str, _BASE_DATA_READERS)) + ")"
        raise InvalidFunction(
            f"Non-{_base_types} types should be annotated with a <Reader>", fn, pname
        )
    return _Param(name, dtype, data_reader, default)


def _input_factory(fn: Callable[..., object], ptype: Any = None) -> _Input:
    dtypes: list[type] = []
    var_list = False
    var_tuple = False

    pname = "input"

    torigin = get_origin(ptype)
    targs = get_args(ptype)
    if torigin is tuple:
        if Ellipsis in targs and (len(targs) != 2 or targs[0] is Ellipsis):
            raise InvalidFunction("Should have valid type annotation", fn, pname)

    if torigin is list and len(targs) != 1:
        raise InvalidFunction("Should have valid type annotation", fn, pname)

    if torigin not in (list, tuple):
        dtypes = [ptype]
    elif torigin is list:
        var_list = True
        dtypes = [targs[0]]
    elif torigin is tuple and targs[-1] is Ellipsis:
        var_tuple = True
        dtypes = [targs[0]]
    elif torigin is tuple:
        for targ in targs:
            dtypes.append(targ)
    return _Input(tuple(dtypes), var_tuple=var_tuple, var_list=var_list)
