import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..cli.tokenizer import TokenError
from .parameter import Parameter


class KWd(t.NamedTuple):
    key: str
    val: t.Any


@dataclass
class ParamParserAbc(ABC):
    @abstractmethod
    def parse(self, param_string: str) -> tuple[tuple[t.Any, ...], tuple[KWd, ...]]:
        """
        Parse a parameter string into args and kwds

        Args:
            string (str): The parameter string to parse

        Returns:
            tuple[tuple[str, ...], tuple[KWd, ...]]: A tuple containing a tuple of args and a tuple of kwds

        Raises:
            TokenError: If the parameter string is invalid
        """
        pass

    @abstractmethod
    def synopsis(self, parameters: list[Parameter]) -> str:
        pass


class ParamParserBasic(ParamParserAbc):
    """
    A basic parameter parser that parses a string into args and kwds

    Split the string by `,` and check if the arg is a keyword argument by checking if it contains `=`

    Example result:
        parse("a,b,c,d=1,e=2") -> (args=("a", "b", "c", "d", "e"), kwds=(KWd("d", "1"), KWd("e", "2")))
    """

    def parse(self, param_string: str) -> tuple[tuple[str, ...], tuple[KWd, ...]]:
        string = param_string
        argList = list(string.split(","))
        args: list[str] = []
        kwds: list[KWd] = []
        for arg in argList[:]:
            if "=" in arg:
                try:
                    k, v = arg.split("=")  # Should split to 2 items
                except ValueError:
                    raise TokenError(
                        string, pos=string.index(arg), msg="Invalid parameter"
                    )
                if not v:
                    raise TokenError(
                        string, pos=string.index(arg), msg="Invalid parameter"
                    )
                if k in dict(kwds):
                    raise TokenError(
                        string, pos=string.index(arg), msg="Parameter already assigned"
                    )

                kwds.append(KWd(k, v))
            else:
                if len(kwds) != 0:
                    raise TokenError(
                        string,
                        pos=string.index(arg),
                        msg="Positional parameter after keyword parameter is not allowed",
                    )

                args.append(arg)

        return tuple(args), tuple(kwds)

    def synopsis(self, parameters: list[Parameter]) -> str:
        """get the synopsis of the operator function parameters"""
        required_positional_params: str = ""
        optional_positional_params: str = ""
        required_keyword_params: str = ""
        optional_keyword_params: str = ""

        for param in parameters:
            if param.is_positional_param:
                if param.is_required:
                    required_positional_params += f",{param.name}"
                else:
                    optional_positional_params += f",{param.name}"
            elif param.is_keyword_param:
                if param.is_required:
                    required_keyword_params += f",{param.name}=<val>"
                else:
                    optional_keyword_params += f",{param.name}=<val>"
            elif param.is_var_param:
                optional_positional_params += f",*{param.name}"
            elif param.is_var_keyword:
                optional_keyword_params += f",**{param.name}"

        synopsis = required_positional_params
        if optional_positional_params:
            synopsis += f"[{optional_positional_params}]"

        synopsis += required_keyword_params

        if optional_keyword_params:
            synopsis += f"[{optional_keyword_params}]"

        synopsis = synopsis.strip(",")

        return synopsis
