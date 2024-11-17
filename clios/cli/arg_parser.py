from dataclasses import dataclass

from clios.core.arg_parser import OprArgParserAbc, OprArgParserError, ParamVal
from clios.core.parameter import Parameter, Parameters

TokenError = OprArgParserError


@dataclass(frozen=True)
class CliOprArgParser(OprArgParserAbc):
    arg_sep: str = ","
    kw_sep: str = "="
    """
    A basic parameter parser that parses a string into args and kwds

    Split the string by `,` and check if the arg is a keyword argument by checking if it contains `=`

    Example result:
        parse("a,b,c,d=1,e=2") -> (args=("a", "b", "c", "d", "e"), kwds=(KWd("d", "1"), KWd("e", "2")))
    """

    def parse(
        self,
        string: str,
        parameters: Parameters,
    ) -> tuple[ParamVal, ...]:
        argList = list(string.split(self.arg_sep))
        param_values: list[ParamVal] = []
        spos = -1
        epos = 0
        for arg in argList[:]:
            spos = epos + 1
            epos = spos + len(arg)
            if self.kw_sep in arg:
                try:
                    k, v = arg.split(self.kw_sep)  # Should split to 2 items
                except ValueError:
                    raise TokenError(
                        f"Invalid parameter: `{arg}`!", string, spos=spos, epos=epos
                    )
                if not v or not k:
                    raise TokenError(
                        f"Invalid parameter: `{arg}`!", string, spos=spos, epos=epos
                    )

                if k in [p.key for p in param_values]:
                    raise TokenError(
                        f"Parameter already assigned: `{arg}`!",
                        string,
                        spos=spos,
                        epos=epos,
                    )
                param_values.append(ParamVal(val=v, key=k))
            else:
                if param_values[-1].key:
                    raise TokenError(
                        "Positional argument after keyword argument is not allowed!",
                        string,
                        spos=spos,
                        epos=epos,
                    )
                param_values.append(ParamVal(val=arg))

    def synopsis(self, parameters: list[Parameter]) -> str:
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
