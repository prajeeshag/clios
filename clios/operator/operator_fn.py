# from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable

from docstring_parser import parse as parse_docstring  # type: ignore
from pydantic.dataclasses import dataclass

from .param_parser import ParamParserAbc
from .parameter import ParamDoc, Parameter, ReturnType


@dataclass(frozen=True)
class OperatorFn:
    """A dataclass to represent an operator function"""

    parameters: tuple[Parameter, ...]
    output: ReturnType
    callback: Callable[..., Any]
    param_parser: ParamParserAbc

    @property
    def short_description(self):
        """Get the short description of the operator"""
        if not self.callback.__doc__:
            return ""
        return parse_docstring(self.callback.__doc__).short_description

    @property
    def long_description(self):
        """Get the long description of the operator"""
        if not self.callback.__doc__:
            return ""
        return parse_docstring(self.callback.__doc__).long_description

    def get_args_doc(self) -> list[ParamDoc]:
        """Get the documentation of the arguments"""
        docs = [param.get_doc() for param in self.args]
        if self.var_args is not None:
            docs.append(self.var_args.get_doc())
        return docs

    def get_kwds_doc(self) -> list[ParamDoc]:
        """Get the documentation of the keyword arguments"""
        docs = [param.get_doc() for param in self.kwds.values()]
        if self.var_kwds is not None:
            docs.append(self.var_kwds.get_doc())
        return docs

    def get_synopsis(self, name: str) -> str:
        """get the synopsis of the operator"""
        required_args = ",".join(param.repr for param in self.required_args)
        optional_args = ",".join(
            param.repr for param in self.args if not param.is_required
        )
        if self.var_args is not None:
            optional_args += "," + self.var_args.repr

        if optional_args:
            optional_args = f"[{optional_args},]"

        required_kwds = ",".join(param.repr for param in self.required_kwds.values())
        optional_kwds = ",".join(
            param.repr for param in self.kwds.values() if not param.is_required
        )
        if self.var_kwds is not None:
            optional_kwds += "," + self.var_kwds.repr

        if optional_kwds:
            optional_kwds = f"[{optional_kwds},]"

        inputs = " ".join(param.repr for param in self.inputs)

        if self.var_input is not None:
            inputs += " " + self.var_input.repr

        if self.output.info.num_outputs == 1:
            output = "output"
        else:
            output = " ".join(
                [f"output{i+1}" for i in range(self.output.info.num_outputs)]
            )

        synopsis = name
        if required_args:
            synopsis += f",{required_args}"
        if optional_args:
            synopsis += f",{optional_args}"
        if required_kwds:
            synopsis += f",{required_kwds}"
        if optional_kwds:
            synopsis += f",{optional_kwds}"
        if inputs:
            synopsis += f" {inputs}"
        if output:
            synopsis += f" {output}"

        return synopsis

    @cached_property
    def args(self) -> tuple[Parameter, ...]:
        """Get a tuple of positional arguments"""
        params = [param for param in self.parameters if param.is_positional_param]
        return tuple(params)

    @cached_property
    def var_args(self) -> Parameter | None:
        """Get the variable positional argument, if any"""
        for param in self.parameters:
            if param.is_var_param:
                return param
        return None

    @cached_property
    def kwds(self) -> dict[str, Parameter]:
        """Get a dictionary of keyword arguments"""
        return {
            param.name: param for param in self.parameters if param.is_keyword_param
        }

    @cached_property
    def var_kwds(self) -> Parameter | None:
        """Get the variable keyword argument, if any"""
        for param in self.parameters:
            if param.is_var_keyword:
                return param
        return None

    @cached_property
    def inputs(self) -> tuple[Parameter, ...]:
        """Get a tuple of input parameters"""
        params = [
            param
            for param in self.parameters
            if param.is_input and not param.is_var_input
        ]
        return tuple(params)

    @cached_property
    def num_inputs(self) -> int:
        """Get the number of input parameters"""
        if self.var_input is not None:
            return -1
        return len(self.inputs)

    @cached_property
    def input_present(self) -> int:
        """Check if there is any input parameter"""
        return not self.num_inputs == 0

    @cached_property
    def var_input(self) -> Parameter | None:
        """Get the variable input parameter, if any"""
        for param in self.parameters:
            if param.is_var_input:
                return param
        return None

    @cached_property
    def num_required_args(self) -> int:
        """Get the number of required positional arguments"""
        params = [param for param in self.parameters if param.is_required_arg]
        return len(params)

    @cached_property
    def required_kwds(self) -> dict[str, Parameter]:
        """Get a dictionary of required keyword arguments"""
        return {
            param.name: param
            for param in self.parameters
            if param.is_keyword_param and param.is_required
        }

    def iter_args(self):
        """Iterate over positional arguments"""
        for param in self.args:
            yield param
        while self.var_args is not None:
            yield self.var_args

    def iter_inputs(self):
        """Iterate over input parameters"""
        for param in self.inputs:
            yield param
        while self.var_input is not None:
            yield self.var_input

    def iter_positional(self):
        """Iterate over positional parameters (i.e. both input and arguments)"""
        var_param = None
        for param in self.parameters:
            if param.is_var_positional:
                var_param = param
                break
            if param.is_keyword_param or param.is_var_keyword:
                break
            yield param

        while var_param is not None:
            yield var_param

    def get_kwd(self, key: str) -> Parameter:
        """Get the keyword argument by key"""
        if key in self.kwds:
            return self.kwds[key]
        if self.var_kwds is not None:
            return self.var_kwds
        raise KeyError(f"Unexpected keyword argument: {key}")
