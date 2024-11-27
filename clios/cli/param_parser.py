import re
import typing as t
from dataclasses import dataclass

from pydantic import ValidationError

from clios.core.param_parser import (
    ParamParserAbc,
    ParamParserError,
)
from clios.core.parameter import Parameters


@dataclass(frozen=True)
class StandardParamParser(ParamParserAbc):
    arg_sep: str = ","
    kw_sep: str = "="
    """
    A basic parameter parser that parses a string into args and kwds

    Split the string by `,` and check if the arg is a keyword argument by checking if it contains `=`

    Example result:
        parse("a,b,c,d=1,e=2") -> (args=("a", "b", "c", "d", "e"), kwds=(KWd("d", "1"), KWd("e", "2")))
    """

    def parse_arguments(
        self,
        string: str,
        parameters: Parameters,
    ) -> tuple[tuple[t.Any, ...], tuple[tuple[str, t.Any], ...]]:
        arg_list = list(string.split(self.arg_sep))

        arg_values: list[t.Any] = []
        kwd_values: dict[str, t.Any] = {}

        positional_arg_iter = parameters.iter_positional_arguments()

        arg_list.reverse()

        spos = 0
        epos = -1
        while len(arg_list) > 0:
            arg = arg_list.pop()
            spos = epos + 1
            epos = spos + len(arg)
            if not arg:
                continue
            kwd = self.get_keyword(arg)
            if kwd is not None:
                k, v = kwd
                if k in kwd_values:
                    raise ParamParserError(
                        f"Duplicate keyword argument `{k}`!",
                        ctx={
                            "spos": spos,
                            "epos": epos,
                        },
                    )
                try:
                    param = parameters.get_keyword_argument(k)
                except KeyError:
                    raise ParamParserError(
                        f"Unknown keyword argument `{k}`!",
                        ctx={
                            "spos": spos,
                            "epos": epos,
                        },
                    )
                try:
                    value = param.build_phase_validator.validate_python(v)
                except ValidationError as e:
                    raise ParamParserError(
                        f"Data validation failed for argument `{k}`!",
                        ctx={
                            "spos": spos,
                            "epos": epos,
                            "error": e,
                        },
                    )
                kwd_values[k] = value
            else:
                if len(kwd_values) > 0:
                    raise ParamParserError(
                        "Positional argument after keyword argument is not allowed!",
                        ctx={
                            "spos": spos,
                            "epos": epos,
                        },
                    )
                try:
                    param = next(positional_arg_iter)
                except StopIteration:
                    raise ParamParserError(
                        f"Too many arguments: expected {len(arg_values)} argument(s)!",
                        ctx={
                            "spos": spos,
                            "epos": epos,
                        },
                    )

                try:
                    value = param.build_phase_validator.validate_python(arg)
                except ValidationError as e:
                    raise ParamParserError(
                        "Data validation failed for argument!",
                        ctx={
                            "spos": spos,
                            "epos": epos,
                            "error": e,
                        },
                    )
                arg_values.append(value)

        if len(arg_values) < parameters.num_required_args:
            raise ParamParserError(
                f"Missing arguments: expected atleast {parameters.num_required_args}, got {len(arg_values)} argument(s)!",
                ctx={
                    "spos": spos,
                    "epos": epos,
                },
            )

        for param_name in parameters.required_keywords.keys():
            if param_name not in kwd_values:
                raise ParamParserError(
                    f"Missing required keyword argument `{param_name}`!",
                    ctx={
                        "spos": spos,
                        "epos": epos,
                    },
                )

        return tuple(arg_values), tuple(kwd_values.items())

    def get_keyword(self, string: str) -> tuple[str, str] | None:
        """split the string into key and value"""

        # Find the first occurence of the kw_sep
        sep_index = string.find(self.kw_sep)

        if not is_valid_variable_name(string[:sep_index]):
            return None

        return string[:sep_index], string[sep_index + 1 :]

    def get_synopsis(self, parameters: Parameters) -> str:
        """get the synopsis of the operator function parameters"""
        required_positional_params: str = ""
        optional_positional_params: str = ""
        required_keyword_params: str = ""
        optional_keyword_params: str = ""

        for param in parameters:
            if param.is_positional_param:
                if param.is_required:
                    required_positional_params += f"{self.arg_sep}{param.name}"
                else:
                    optional_positional_params += f"{self.arg_sep}{param.name}"
            elif param.is_keyword_param:
                if param.is_required:
                    required_keyword_params += (
                        f"{self.arg_sep}{param.name}{self.kw_sep}<val>"
                    )
                else:
                    optional_keyword_params += (
                        f"{self.arg_sep}{param.name}{self.kw_sep}<val>"
                    )
            elif param.is_var_param:
                optional_positional_params += f"{self.arg_sep}*{param.name}"
            elif param.is_var_keyword:
                optional_keyword_params += f"{self.arg_sep}**{param.name}"

        res = required_positional_params
        if optional_positional_params:
            res += f"[{optional_positional_params}]"

        res += required_keyword_params

        if optional_keyword_params:
            res += f"[{optional_keyword_params}]"
        res = res.strip(self.arg_sep)
        return res


def is_valid_variable_name(name: str) -> bool:
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
    return re.match(pattern, name) is not None
