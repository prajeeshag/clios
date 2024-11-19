import re
from dataclasses import dataclass

from pydantic import ValidationError

from clios.core.operator_parser import OprParserAbc, OprParserError, ParamVal
from clios.core.parameter import Parameters


@dataclass(frozen=True)
class CliOprParser(OprParserAbc):
    arg_sep: str = ","
    kw_sep: str = "="
    """
    A basic parameter parser that parses a string into args and kwds

    Split the string by `,` and check if the arg is a keyword argument by checking if it contains `=`

    Example result:
        parse("a,b,c,d=1,e=2") -> (args=("a", "b", "c", "d", "e"), kwds=(KWd("d", "1"), KWd("e", "2")))
    """

    def get_name(self, string: str) -> str:
        return string.split(self.arg_sep)[0].strip("-")

    def parse_arguments(
        self,
        string: str,
        parameters: Parameters,
    ) -> tuple[ParamVal, ...]:
        arg_list = list(string.split(self.arg_sep))

        arg_values: list[ParamVal] = []
        kwd_values: list[ParamVal] = []

        positional_arg_iter = parameters.iter_positional_arguments()

        arg_list.reverse()
        name = arg_list.pop()  # remove the operator name

        spos = 0
        epos = len(name)
        while len(arg_list) > 0:
            arg = arg_list.pop()
            spos = epos + 1
            epos = spos + len(arg)

            kwd = self.get_keyword(arg)
            if kwd is not None:
                k, v = kwd
                if k in [p.key for p in kwd_values]:
                    raise OprParserError(
                        f"Duplicate keyword argument `{k}`!",
                        string,
                        spos=spos,
                        epos=epos,
                    )
                try:
                    param_name = parameters.get_keyword_argument(k)
                except KeyError:
                    raise OprParserError(
                        f"Unknown keyword argument `{k}`!",
                        string,
                        spos=spos,
                        epos=epos,
                    )
                try:
                    value = param_name.build_phase_validator.validate_python(v)
                except ValidationError as e:
                    raise OprParserError(
                        f"Data validation failed for argument `{k}`!",
                        string,
                        spos=spos,
                        epos=epos,
                        ctx={"validation_error": e},
                    )
                kwd_values.append(ParamVal(val=value, key=k))
            else:
                if len(kwd_values) > 0:
                    raise OprParserError(
                        "Positional argument after keyword argument is not allowed!",
                        string,
                        spos=spos,
                        epos=epos,
                    )
                try:
                    param_name = next(positional_arg_iter)
                except StopIteration:
                    raise OprParserError(
                        f"Too many arguments: expected {len(arg_values)} argument(s)!",
                        string,
                        spos=spos,
                        epos=epos,
                    )
                try:
                    value = param_name.build_phase_validator.validate_python(arg)
                except ValidationError as e:
                    raise OprParserError(
                        "Data validation failed for argument!",
                        string,
                        spos=spos,
                        epos=epos,
                        ctx={"validation_error": e},
                    )
                arg_values.append(ParamVal(val=value))

        if len(arg_values) < parameters.num_required_args:
            raise OprParserError(
                f"Missing arguments: expected atleast {parameters.num_required_args}, got {len(arg_values)} argument(s)!",
                string,
                spos=spos,
                epos=epos,
            )

        kwd_keys = [p.key for p in kwd_values]
        for param_name in parameters.required_keywords.keys():
            if param_name not in kwd_keys:
                raise OprParserError(
                    f"Missing required keyword argument `{param_name}`!",
                    string,
                    spos=spos,
                    epos=epos,
                )

        return tuple([*arg_values, *kwd_values])

    def get_keyword(self, string: str) -> tuple[str, str] | None:
        """split the string into key and value"""

        # Find the first occurence of the kw_sep
        sep_index = string.find(self.kw_sep)

        if not is_valid_variable_name(string[:sep_index]):
            return None

        return string[:sep_index], string[sep_index + 1 :]

    def get_synopsis(self, parameters: Parameters, name: str) -> str:
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

        res = name
        res += required_positional_params
        if optional_positional_params:
            res += f"[{optional_positional_params}]"

        res += required_keyword_params

        if optional_keyword_params:
            res += f"[{optional_keyword_params}]"

        return res


def is_valid_variable_name(name: str) -> bool:
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
    return re.match(pattern, name) is not None
