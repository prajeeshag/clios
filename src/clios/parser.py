from .exceptions import ChainTypeError, OperatorNotFound, TokenError
from .operation import (
    ChainableOperation,
    GeneratorOperation,
    Operation,
    ReadOperation,
    WriteOperation,
)
from .operator import Generator, Operator
from .registry import OperatorRegistry, ReaderRegistry, WriterRegistry
from .tokenizer import Tokenizer
from .tokenizer.tokens import ArgumentToken, FilePathToken, OperatorToken

# TODO: Implement parameter validation during CallTree construction


class Parser:
    def __init__(
        self,
        operators: OperatorRegistry,
        writers: WriterRegistry,
        readers: ReaderRegistry,
    ) -> None:
        self._operators = operators
        self._writers = writers
        self._readers = readers
        self._tokenizer: Tokenizer = Tokenizer([FilePathToken, OperatorToken])

    def parse_tokens(
        self, tokens: list[ArgumentToken], index: int = 0
    ) -> WriteOperation:
        token_list = list(tokens)

        opTkn = token_list[0]
        token_list.pop(0)

        if not isinstance(opTkn, OperatorToken):
            raise OperatorNotFound(str(opTkn))

        try:
            op = self._operators.get(opTkn.name)
        except KeyError:
            raise OperatorNotFound(opTkn.name)

        wrtr = self._writers.get(op.output_type)

        output_file_paths: list[str] = []
        for _ in range(wrtr.num_outputs):
            try:
                outputtkn = token_list.pop()
                if not isinstance(outputtkn, FilePathToken):
                    raise TokenError(
                        msg=f"Missing output file: got '{outputtkn}' instead of filename"
                    )

                output_file_paths.append(str(outputtkn))
            except IndexError:
                raise TokenError(str(opTkn), msg="Missing output")

        token_list = list(reversed(token_list))

        optn = self._parse_tokens(token_list, opTkn, op)

        if len(token_list) != 0:
            raise TokenError(str(token_list[-1]), msg="Too many inputs")

        return WriteOperation(wrtr, optn, tuple(reversed(output_file_paths)))

    def _parse_tokens(
        self,
        token_list: list[ArgumentToken],
        opTkn: OperatorToken,
        op: Operator | Generator,
    ):
        if isinstance(op, Generator):
            return GeneratorOperation(op, opTkn.params, opTkn.kwparams)

        child_optns: list[ChainableOperation] = []

        if op.input.is_variadic:
            if len(token_list) == 0:
                raise TokenError(str(opTkn), msg="Missing inputs")

            while token_list:
                tkn = token_list.pop()
                if isinstance(tkn, OperatorToken):
                    child_op = self._get_operator(tkn)
                    if op.input.dtypes[0] != child_op.output_type:
                        raise ChainTypeError(
                            tkn.name,
                            opTkn.name,
                            op.input.dtypes[0],
                            child_op.output_type,
                        )
                    child_optn = self._parse_tokens(token_list, tkn, child_op)
                    child_optns.append(child_optn)
                else:
                    rdr = self._readers.get(op.input.dtypes[0])
                    child_optns.append(ReadOperation(rdr, str(tkn)))
        else:
            for i in range(op.input.len):
                try:
                    tkn = token_list.pop()
                except IndexError:
                    raise TokenError(str(opTkn), msg="Missing inputs")

                if isinstance(tkn, OperatorToken):
                    child_op = self._get_operator(tkn)
                    if op.input.dtypes[i] != child_op.output_type:
                        raise ChainTypeError(
                            tkn.name,
                            opTkn.name,
                            op.input.dtypes[i],
                            child_op.output_type,
                        )
                    child_optn = self._parse_tokens(token_list, tkn, child_op)
                    child_optns.append(child_optn)
                else:
                    rdr = self._readers.get(op.input.dtypes[i])
                    child_optns.append(ReadOperation(rdr, str(tkn)))

        optn = Operation(op, tuple(child_optns), opTkn.params, opTkn.kwparams)
        return optn

    def _get_operator(self, tkn: OperatorToken):
        try:
            op = self._operators.get(tkn.name)
        except KeyError:
            raise OperatorNotFound(tkn.name)
        return op

    def tokenize(self, args: list[str]) -> list[ArgumentToken]:
        tokens: list[ArgumentToken] = []
        for arg in args:
            tokens.append(self._tokenizer.tokenize(arg))
        return tokens
