# from dataclasses import dataclass
import typing as t
from dataclasses import dataclass

from griffe import Docstring, DocstringSectionKind, parse_google

from .param_parser import ParamParserAbc
from .parameter import Parameter, Parameters, ReturnValue
from .utils import get_output_info, get_typed_signature

Implicit = t.Literal["input", "param"]


@dataclass(frozen=True)
class OperatorFn:
    """A dataclass to represent an operator function"""

    parameters: Parameters
    output: ReturnValue
    callback: t.Callable[..., t.Any]
    param_parser: ParamParserAbc

    @property
    def short_description(self):
        """Get the short description of the operator"""
        if not self.callback.__doc__:
            return ""
        parsed_docstring = parse_google(Docstring(self.callback.__doc__))

        if parsed_docstring[0].kind != DocstringSectionKind.text:
            return ""

        return parsed_docstring[0].value

    @property
    def long_description(self):
        """Get the long description of the operator"""
        if not self.callback.__doc__:
            return ""
        parsed_docstring = parse_google(Docstring(self.callback.__doc__))

        for section in parsed_docstring:
            if section.title and section.title.lower() == "description":
                return section.value.contents
        return ""

    @property
    def examples(self) -> list[tuple[str, str]]:
        """Get the examples of the operator"""
        if not self.callback.__doc__:
            return []

        parsed_docstring = parse_google(Docstring(self.callback.__doc__))

        for section in parsed_docstring:
            if section.title and (
                section.title.lower() == "operator examples"
                or section.title.lower() == "operator example"
            ):
                example_docstring = parse_google(Docstring(section.value.contents))
                examples: list[tuple[str, str]] = []
                for example in example_docstring:
                    title = "" if example.title is None else example.title
                    contents = (
                        example.value
                        if example.kind == DocstringSectionKind.text
                        else example.value.contents
                    )
                    examples.append((title, contents))
                return examples
        return []

    @classmethod
    def validate(
        cls,
        func: t.Callable[..., t.Any],
        param_parser: ParamParserAbc,
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
            output=ReturnValue.validate(return_annotation, output_info),
            callback=func,
            param_parser=param_parser,
        )


class OperatorFns(dict[str, OperatorFn]):
    def __setitem__(self, key: str, value: OperatorFn) -> None:
        assert (
            key not in self
        ), f"Operator '{key}' already exists. Reassignment is not allowed."
        super().__setitem__(key, value)

    def update(self, *arg, **kwds) -> None:
        if kwds or not isinstance(arg[0], OperatorFns):
            raise TypeError(
                f"update() only accept a single positional argument of type {OperatorFns}"
            )
        for key in arg[0].keys():
            assert (
                key not in self
            ), f"Operator '{key}' already exists. Reassignment is not allowed."
        super().update(arg[0])

    def register(
        self,
        *,
        name: str = "",
        param_parser: ParamParserAbc,
        implicit: t.Literal["input", "param"] = "input",
    ) -> t.Callable[..., t.Any]:
        def _decorator(func: t.Callable[..., t.Any]):
            key = name if name else func.__name__
            self[key] = OperatorFn.validate(
                func,
                param_parser=param_parser,
                implicit=implicit,
            )
            return func

        return _decorator
