from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from .model import OperatorFn


@dataclass(frozen=True)
class BaseOperator(ABC):
    @abstractmethod
    def execute(self) -> Any:
        pass


@dataclass(frozen=True)
class SimpleOperator(BaseOperator):
    fn: Callable[[Any], Any]
    input: Any

    def execute(self) -> Any:
        return self.fn(self.input)


@dataclass(frozen=True)
class LeafOperator(BaseOperator):
    operator_fn: OperatorFn
    args: tuple[Any, ...] = ()
    kwds: dict[str, Any] = field(default_factory=dict)

    def _validate_arguments(self) -> list[Any]:
        arg_values: list[Any] = []
        iter_args = self.operator_fn.iter_args()
        for val in self.args:
            param = next(iter_args)
            arg_values.append(param.validate_execute(val))
        return arg_values

    def _validate_keywords(self) -> dict[str, Any]:
        arg_values: dict[str, Any] = {}
        for key, val in self.kwds.items():
            param = self.operator_fn.get_kwd(key)
            arg_values[key] = param.validate_execute(val)
        return arg_values

    def _compose_arg_values(self, args: list[Any], inputs: list[Any]) -> list[Any]:
        iter_params = self.operator_fn.iter_positional_params()
        args_rev = list(args[::-1])
        inputs_rev = list(inputs[::-1])
        param_values: list[Any] = []
        for param in iter_params:
            if len(args_rev) == 0 and len(inputs_rev) == 0:
                break
            if param.is_input:
                param_values.append(inputs_rev.pop())
            else:
                param_values.append(args_rev.pop())
        return param_values

    def execute(self) -> Any:
        arg_values = self._validate_arguments()
        kwds_values = self._validate_keywords()
        value = self.operator_fn.callback(*arg_values, **kwds_values)
        return self.operator_fn.return_type.validate(value)


@dataclass(frozen=True)
class Operator(LeafOperator):
    inputs: tuple[BaseOperator, ...] = ()

    def _validate_execute_inputs(self) -> list[Any]:
        input_values: list[Any] = []
        iter_inputs = self.operator_fn.iter_inputs()
        for input_ in self.inputs:
            input_param = next(iter_inputs)
            value = input_param.validate_execute(input_.execute())
            input_values.append(value)
        return input_values

    def execute(self) -> Any:
        arg_values = self._validate_arguments()
        kwds_values = self._validate_keywords()
        input_values = self._validate_execute_inputs()
        positional_args = self._compose_arg_values(arg_values, input_values)
        value = self.operator_fn.callback(*positional_args, **kwds_values)
        return self.operator_fn.return_type.validate(value)


@dataclass(frozen=True)
class RootOperator:
    input: BaseOperator
    file_saver: Callable[[Any, str], None] | None = None
    args: tuple[str, ...] = ()

    def execute(self):
        value = self.input.execute()
        if value is None:
            return
        assert self.file_saver is not None
        self.file_saver(value, *self.args)
