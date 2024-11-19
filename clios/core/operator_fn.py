# from dataclasses import dataclass
import typing as t
from dataclasses import dataclass

from docstring_parser import parse as parse_docstring  # type: ignore

from .arg_parser import OprArgParserAbc
from .parameter import Parameter, Parameters, ReturnValue
from .utils import get_output_info, get_typed_signature

Implicit = t.Literal["input", "param"]


@dataclass(frozen=True)
class OperatorFn:
    """A dataclass to represent an operator function"""

    parameters: Parameters
    output: ReturnValue
    callback: t.Callable[..., t.Any]
    param_parser: OprArgParserAbc

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

    @classmethod
    def validate(
        cls,
        func: t.Callable[..., t.Any],
        arg_parser: OprArgParserAbc,
        implicit: Implicit = "input",
    ) -> "OperatorFn":
        signature = get_typed_signature(func)
        parameter_list: list[Parameter] = []
        for param in signature.parameters.values():
            parameter_list.append(Parameter.validate(param, implicit))
        return_annotation = signature.return_annotation
        output_info = get_output_info(return_annotation)
        return OperatorFn(
            parameters=Parameters(parameter_list),
            output=ReturnValue(return_annotation, output_info),
            callback=func,
            param_parser=arg_parser,
        )
