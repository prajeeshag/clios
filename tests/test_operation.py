# type: ignore

import pytest
from pytest_mock import MockerFixture

from clios.operation import (
    GeneratorOperation,
    Operation,
    ReadOperation,
    WriteOperation,
)


@pytest.mark.parametrize(
    "args,kwargs,res",
    [
        [(), (), "s"],
        [("a", "1", "c"), (), 1],
        [("a", "1", "c"), (("k", "s"), ("l", "1")), 10.5],
    ],
)
def test_GeneratorOperation(mocker: MockerFixture, args, kwargs, res):
    generator = mocker.patch("clios.operator.Generator", autospec=True).return_value
    generator.load_args.return_value = args
    generator.load_kwargs.return_value = dict(kwargs)
    generator.return_value = res

    op = GeneratorOperation(generator, args=args, kwargs=kwargs)
    result = op.execute()
    generator.load_args.assert_called_once_with(args)
    generator.load_kwargs.assert_called_once_with(dict(kwargs))
    generator.assert_called_once_with(*args, **dict(kwargs))
    assert result == res


@pytest.mark.parametrize(
    "args,kwargs,res",
    [
        [(), (), "s"],
        [("a", "1", "c"), (), 1],
        [("a", "1", "c"), (("k", "s"), ("l", "1")), 10.5],
    ],
)
def test_Operation(mocker: MockerFixture, args, kwargs, res):
    operator = mocker.patch("clios.operator.Operator", autospec=True).return_value
    operator.load_args.return_value = args
    operator.load_kwargs.return_value = dict(kwargs)
    operator.return_value = res

    child_op1 = mocker.Mock()
    child_op2 = mocker.Mock()
    child_op1.execute.return_value = "op1"
    child_op2.execute.return_value = "op2"

    op = Operation(operator, args=args, kwargs=kwargs, children=(child_op1, child_op2))
    result = op.execute()
    operator.load_args.assert_called_once_with(args)
    operator.load_kwargs.assert_called_once_with(dict(kwargs))
    child_op1.execute.assert_called_once()
    child_op2.execute.assert_called_once()
    operator.assert_called_once_with(("op1", "op2"), *args, **dict(kwargs))
    assert result == res


@pytest.mark.parametrize(
    "filepath,res",
    [
        ["file1", "s"],
        ["file2", 1],
    ],
)
def test_ReaderOperation(mocker, filepath, res):
    reader = mocker.patch("clios.operator.Reader", autospec=True).return_value
    op = ReadOperation(reader, filepath)
    reader.return_value = res
    result = op.execute()
    reader.assert_called_once_with(filepath)
    assert result == res


@pytest.mark.parametrize(
    "filepaths,input",
    [
        [(), "s"],
        [("file1",), "s"],
        [("file1", "file2"), 1],
    ],
)
def test_WriterOperation(mocker, filepaths, input):
    writer = mocker.patch("clios.operator.Writer", autospec=True).return_value
    child_op = mocker.Mock()
    child_op.execute.return_value = input
    op = WriteOperation(writer, child_op, filepaths)
    op.execute()
    child_op.execute.assert_called_once()
    writer.assert_called_once_with(input, *filepaths)
