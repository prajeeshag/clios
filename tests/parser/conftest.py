# type: ignore
import pytest
from pytest_mock import MockerFixture

from clios.parser import Parser


@pytest.fixture
def operators(mocker: MockerFixture):
    return mocker.patch("clios.registry.OperatorRegistry", autospec=True).return_value


@pytest.fixture
def readers(mocker: MockerFixture):
    return mocker.patch("clios.registry.ReaderRegistry", autospec=True).return_value


@pytest.fixture
def writers(mocker: MockerFixture):
    return mocker.patch("clios.registry.WriterRegistry", autospec=True).return_value


@pytest.fixture
def parser(
    operators,
    readers,
    writers,
):
    return Parser(
        operators,
        writers,
        readers,
    )
