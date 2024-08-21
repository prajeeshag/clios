# type: ignore
import pytest

import clios
from clios.operator import Reader, Writer


@pytest.fixture
def app():
    return clios.Clios()


def test_operator(mocker, app: clios.Clios):
    operator_factory_mock = mocker.patch(
        "clios._Clios.operator_factory", return_value="Operator object"
    )
    mock_operator_registry = mocker.patch.object(app, "_operators", autospec=True)

    @app.operator()
    def op1(input: int, k: float, i: str = "s") -> int:
        pass

    operator_factory_mock.assert_called_once_with(op1)
    mock_operator_registry.add.assert_called_once_with("op1", "Operator object")


def test_operator_with_name(mocker, app: clios.Clios):
    operator_factory_mock = mocker.patch(
        "clios._Clio.operator_factory", return_value="Operator object"
    )
    mock_operator_registry = mocker.patch.object(app, "_operators", autospec=True)

    @app.operator(name="operator1")
    def op1(input: int, k: float, i: str = "s") -> int:
        pass

    operator_factory_mock.assert_called_once_with(op1)
    mock_operator_registry.add.assert_called_once_with("operator1", "Operator object")


def test_writer(mocker, app: clios.Clios):
    wrtr = Writer(None, int, 1)
    factory_mock = mocker.patch("clios._Clio.writer_factory", return_value=wrtr)
    mock_registry = mocker.patch.object(app, "_writers", autospec=True)

    @app.writer()
    def w1(input: int, i: str):
        pass

    factory_mock.assert_called_once_with(w1)
    mock_registry.add.assert_called_once_with(int, wrtr)


def test_reader(mocker, app: clios.Clios):
    rdr = Reader(None, int)
    factory_mock = mocker.patch("clios._Clio.reader_factory", return_value=rdr)
    mock_registry = mocker.patch.object(app, "_readers", autospec=True)

    @app.reader()
    def r1(i: str) -> int:
        pass

    factory_mock.assert_called_once_with(r1)
    mock_registry.add.assert_called_once_with(int, rdr)


def test_parse_args(mocker, app):
    # Mock the Parser class
    mock_parser_class = mocker.patch("clios._Clio.Parser", autospec=True)

    # Create a mock Parser instance
    mock_parser_instance = mock_parser_class.return_value

    # Mock the tokenize and parse_tokens methods
    mock_tokens = ["mocked", "tokens"]
    mock_parser_instance.tokenize.return_value = mock_tokens
    mock_parsed_result = "Parsed Result"
    mock_parser_instance.parse_tokens.return_value = mock_parsed_result

    # Call the parse_args method
    args = ["arg1", "arg2", "arg3"]
    result = app.parse_args(args)

    # Verify the method interactions and result
    mock_parser_class.assert_called_once_with(
        app._operators, app._writers, app._readers
    )
    mock_parser_instance.tokenize.assert_called_once_with(args)
    mock_parser_instance.parse_tokens.assert_called_once_with(mock_tokens)
    assert result == mock_parsed_result
