import typing as t
from dataclasses import dataclass

from pydantic import ValidationError

from clios.core.main_parser import ParserAbc, ParserError
from clios.core.operator import (
    BaseOperator,
    LeafOperator,
    Operator,
    OperatorAbc,
    RootOperator,
    SimpleOperator,
)
from clios.core.operator_fn import OperatorFn
from clios.core.param_parser import ParamParserError
from clios.core.registry import OperatorRegistry
from clios.core.tokenizer import Token

from .tokenizer import OperatorToken, StringToken, Tokenizer


@dataclass(frozen=True)
class CliParser(ParserAbc):
    operator_fns: OperatorRegistry
    tokenizer: Tokenizer[list[str]]

    def get_name(self, string: str) -> str:
        return string.split(",")[0].strip("-")

    def get_param_string(self, string: str) -> str:
        return ",".join(string.split(",")[1:])

    def get_operator(
        self,
        input: list[str],
        callback: t.Callable[[t.Any], t.Any] | None = None,
        **kwargs: t.Any,
    ) -> RootOperator:
        if not input:
            raise ParserError("Input is empty!")
        tokens = list(self.tokenizer.tokenize(input))
        num_tokens = len(tokens)
        token = tokens.pop(0)
        operator_name = self.get_name(token.value)
        param_string = self.get_param_string(token.value)
        operator_fn = self._get_operator_fn(operator_name, 0)

        num_outputs = 0
        if callback is None and operator_fn.output.type_ is not None:
            callback = operator_fn.output.info.callback
            if callback is None:
                raise ParserError(
                    f"Operator `{operator_name}` cannot be used as root operator!",
                    ctx={"token_index": 0},
                )
            num_outputs = operator_fn.output.info.num_outputs

        output_file_paths: list[str] = []
        for i in range(num_outputs):
            try:
                output_token = tokens.pop()
                if not isinstance(output_token, StringToken):
                    raise ParserError(
                        "Output file path must be a string",
                        ctx={"token_index": num_tokens - 1 - i},
                    )
                output_file_paths.append(str(output_token))
            except IndexError:
                raise ParserError(
                    "Missing output(s)!", ctx={"token_index": num_tokens - 1 - i}
                )

        tokens.reverse()

        operator = self._get_operator(
            operator_name=operator_name,
            param_string=param_string,
            operator_fn=operator_fn,
            token_index=0,
            input_tokens=tokens,
        )

        if len(tokens) != 0:
            raise ParserError(
                "Got too many inputs!",
                ctx={
                    "num_extra_tokens": len(tokens),
                    "token_index": num_tokens - len(tokens),
                },
            )

        return RootOperator(
            input=operator,
            callback=callback,
            args=tuple(output_file_paths),
        )

    def get_synopsis(self, operator_name: str) -> str:
        try:
            op = self.operator_fns.get(operator_name)
        except KeyError:
            raise ParserError(f"Operator `{operator_name}` not found!")
        param_synopsis = op.param_parser.get_synopsis(op.parameters)
        input_synopsis = " ".join([i.name for i in op.parameters if i.is_input])
        output_synopsis = " ".join(
            [f"output{i+1}" for i in range(op.output.info.num_outputs)]
        )
        if op.output.info.num_outputs == 1:
            output_synopsis = "output"
        return f"{operator_name},{param_synopsis} {input_synopsis} {output_synopsis}"

    def _get_operator(
        self,
        operator_name: str,
        param_string: str,
        operator_fn: OperatorFn,
        token_index: int,
        input_tokens: list[Token],
    ) -> BaseOperator:
        try:
            args, kwds = operator_fn.param_parser.parse_arguments(
                string=param_string,
                parameters=operator_fn.parameters,
            )
        except ParamParserError as e:
            raise ParserError(
                f"Failed to parse arguments for operator `{operator_name}`!",
                ctx={"error": e, "token_index": token_index},
            )

        if not operator_fn.parameters.input_present:
            return LeafOperator(
                name=operator_name,
                index=token_index,
                operator_fn=operator_fn,
                args=args,
                kwds=kwds,
            )

        child_operators: list[OperatorAbc] = []

        child_index = token_index
        for input_param in operator_fn.parameters.iter_inputs():
            if len(input_tokens) == 0:
                break
            child_token = input_tokens.pop()
            child_index += 1
            if isinstance(child_token, OperatorToken):
                child_op_name = self.get_name(child_token.value)
                child_op_param_string = self.get_param_string(child_token.value)
                child_op_fn = self._get_operator_fn(child_op_name, child_index)
                in_type = input_param.type_
                if in_type is not t.Any and in_type != child_op_fn.output.type_:
                    raise ParserError(
                        "These operators cannot be chained together!",
                        ctx={
                            "unchainable_token_index": child_index,
                            "token_index": token_index,
                        },
                    )
                num_tokens_before = len(input_tokens)
                child_operator = self._get_operator(
                    operator_name=child_op_name,
                    param_string=child_op_param_string,
                    operator_fn=child_op_fn,
                    token_index=child_index,
                    input_tokens=input_tokens,
                )
                child_operators.append(child_operator)
                child_index += num_tokens_before - len(input_tokens)
            elif isinstance(child_token, StringToken):
                try:
                    value = input_param.build_phase_validator.validate_python(
                        child_token.value
                    )
                except ValidationError as e:
                    raise ParserError(
                        f"Data validation failed for input {child_token.value}!",
                        ctx={"error": e, "token_index": child_index},
                    )
                child_operators.append(
                    SimpleOperator(
                        name=child_token.value,
                        index=child_index,
                        fn=input_param.execute_phase_validator.validate_python,
                        input_=value,
                    )
                )
            else:
                raise ParserError(
                    "This syntax is not supported yet!",
                    ctx={"token_index": child_index},
                )

        if len(child_operators) < operator_fn.parameters.num_minimum_inputs:
            raise ParserError(
                f"Missing inputs for operator {operator_name}!",
                ctx={"token_index": token_index},
            )

        return Operator(
            name=operator_name,
            index=token_index,
            operator_fn=operator_fn,
            inputs=tuple(child_operators),
            args=args,
            kwds=kwds,
        )

    def _get_operator_fn(self, name: str, index: int) -> OperatorFn:
        try:
            op = self.operator_fns.get(name)
        except KeyError:
            raise ParserError(
                f"Operator `{name}` not found!", ctx={"token_index": index}
            )
        return op
