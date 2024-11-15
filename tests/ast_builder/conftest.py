# type: ignore
import pytest
from pytest_mock import MockerFixture

from clios.ast_builder import ASTBuilder


@pytest.fixture
def operators(mocker: MockerFixture):
    return mocker.patch("clios.registry.OperatorRegistry", autospec=True).return_value


@pytest.fixture
def parser(
    operators,
):
    return ASTBuilder(
        operators,
    )
