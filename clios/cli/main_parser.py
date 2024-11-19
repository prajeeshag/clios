import typing as t
from dataclasses import dataclass

from pydantic import ValidationError

from clios.core.main_parser import ParserAbc, ParserError
from clios.core.operator import BaseOperator, LeafOperator, SimpleOperator
from clios.core.operator_fn import OperatorFn
from clios.core.tokenizer import Token

from .tokenizer import OperatorToken, StringToken


@dataclass(frozen=True)
class CliOpParser(ParserAbc):
    def get_name(self, string: str) -> str:
        return string.split(",")[0].strip("-")

    def get_param_string(self, string: str) -> str:
        return ",".join(string.split(",")[1:])

    def get_operator(
        self,
        name: str,
        index: int,
        operator_fn: OperatorFn,
        args: tuple[t.Any, ...],
        kwds: tuple[tuple[str, t.Any], ...],
        input_tokens: list[Token],
    ) -> BaseOperator:
        if not operator_fn.parameters.input_present:
            return LeafOperator(name, index, operator_fn, args, kwds)

        child_operators: list[BaseOperator] = []

        child_index = index
        for input_param in operator_fn.parameters.iter_inputs():
            if len(input_tokens) == 0:
                break
            tkn = input_tokens.pop()
            child_index += 1
            if isinstance(tkn, OperatorToken):
                operator_name = self.get_name(tkn.value)
                child_op = self._get_operator(operator_name, child_index)
                in_type = input_param.type_
                if in_type is not t.Any and in_type != child_op.output.type_:
                    raise ParserError(
                        "These operators cannot be chained together!",
                        ctx={
                            "token_index": index,
                            "unchainable_token_index": child_index,
                        },
                    )
                num_tokens_before = len(input_tokens)
                child_operator = self._parse_tokens(
                    input_tokens, tkn, child_op, child_index
                )
                child_operators.append(child_operator)
                child_index += num_tokens_before - len(input_tokens)
            elif isinstance(tkn, StringToken):
                try:
                    value = input_param.validate_build(tkn.value)
                except ValidationError as e:
                    raise ParserError(
                        "Data validation error!",
                        ctx={
                            "token_index": child_index,
                            "validation_error": e,
                        },
                    )
                child_operators.append(
                    SimpleOperator(tkn, input_param.validate_execute, value)
                )
            else:
                raise ParserError(
                    "This syntax is not supported yet!",
                    ctx={"token_index": child_index},
                )

    def _get_operator(self, tkn: OperatorToken, index: int) -> OperatorFn:
        try:
            op = self._operators.get(tkn.name)
        except KeyError:
            raise ParserError(
                f"Operator `{tkn.name}` not found!", ctx={"token_index": index}
            )
        return op
