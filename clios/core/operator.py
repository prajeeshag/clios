from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import ValidationError

from .operator_fn import OperatorFn


class OperatorError(Exception):
    def __init__(self, message: str, ctx: dict[str, Any] = {}) -> None:
        self.message = message
        self.ctx = ctx
        super().__init__(self.message)

    def __str__(self) -> str:
        message = self.message
        if "error" in self.ctx:
            message += f"\n{str(self.ctx['error'])}"
        return message


@dataclass(frozen=True)
class OperatorAbc(ABC):
    @abstractmethod
    def execute(self) -> Any: ...  # pragma: no cover

    @abstractmethod
    def draw(self) -> str: ...  # pragma: no cover


@dataclass(frozen=True)
class SimpleOperator(OperatorAbc):
    name: str
    index: int
    input_: Any

    def execute(self) -> Any:
        return self.input_

    def draw(self) -> str:
        return self.name


@dataclass(frozen=True)
class BaseOperator(OperatorAbc):
    name: str
    index: int
    operator_fn: OperatorFn
    args: tuple[Any, ...] = ()
    kwds: tuple[tuple[str, Any], ...] = ()

    def _validate_arguments(self) -> list[Any]:
        arg_values: list[Any] = []
        iter_args = self.operator_fn.parameters.iter_positional_arguments()
        for val in self.args:
            param = next(iter_args)
            try:
                arg_values.append(param.execute_phase_validator.validate_python(val))
            except ValidationError as e:
                raise OperatorError(
                    f"Data validation failed for the argument `{param.name}` of operator `{self.name}`!",
                    ctx={"error": e},
                )
        return arg_values

    def _validate_keywords(self) -> dict[str, Any]:
        arg_values: dict[str, Any] = {}
        for key, val in self.kwds:
            param = self.operator_fn.parameters.get_keyword_argument(key)
            try:
                arg_values[key] = param.execute_phase_validator.validate_python(val)
            except ValidationError as e:
                raise OperatorError(
                    f"Data validation failed for the argument `{param.name}` of operator `{self.name}`!",
                    ctx={"error": e},
                )
        return arg_values

    def _compose_arg_values(self, args: list[Any], inputs: list[Any]) -> list[Any]:
        iter_params = self.operator_fn.parameters.iter_positional()
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
        try:
            return self.operator_fn.output.validator.validate_python(value)
        except ValidationError as e:
            raise OperatorError(
                f"Data validation failed for the output of operator `{self.name}`!\n"
                + f"Error: {e}\n"
                + "It's a bug! Please report it!",
            )

    def draw(self) -> str:
        return f"{self.name}"


@dataclass(frozen=True)
class LeafOperator(BaseOperator):
    pass


@dataclass(frozen=True)
class Operator(BaseOperator):
    name: str
    index: int
    inputs: tuple[OperatorAbc, ...] = ()

    def _validate_execute_inputs(self) -> list[Any]:
        input_values: list[Any] = []
        iter_inputs = self.operator_fn.parameters.iter_inputs()
        for input_ in self.inputs:
            input_param = next(iter_inputs)
            try:
                value = input_param.execute_phase_validator.validate_python(
                    input_.execute()
                )
            except ValidationError as e:
                raise OperatorError(
                    f"Data validation failed for the input of operator `{self.name}`!",
                    ctx={"error": e},
                )
            input_values.append(value)
        return input_values

    def execute(self) -> Any:
        arg_values = self._validate_arguments()
        kwds_values = self._validate_keywords()
        input_values = self._validate_execute_inputs()
        positional_args = self._compose_arg_values(arg_values, input_values)
        value = self.operator_fn.callback(*positional_args, **kwds_values)
        try:
            return self.operator_fn.output.validator.validate_python(value)
        except ValidationError as e:
            raise OperatorError(
                f"Data validation failed for the output of operator `{self.name}`!\n"
                + f"Error: {e}\n"
                + "It's a bug! Please report it!",
            )

    def draw(self) -> str:
        res = f"{self.name} [ "
        for input_ in self.inputs:
            res += f"{input_.draw()} "
        res += "]"
        return res


@dataclass(frozen=True)
class RootOperator(OperatorAbc):
    input: BaseOperator
    callback: Callable[..., Any]
    args: tuple[str, ...] = ()

    def execute(self) -> Any:
        value = self.input.execute()
        return self.callback(value, *self.args)

    def draw(self) -> str:
        res = ",".join(self.args)
        if res:
            res = f"{res} "
        res += f"[ {self.input.draw()} ]"
        return res
