# type: ignore
import sys

import pytest

from clios.cli.app import Clios, OperatorFns


@pytest.fixture
def app():
    return OperatorFns()


def test_click_app_help(app):
    sys.argv = ["cli", "--help"]
    result = Clios(app)()
    assert result is None


def test_click_app_list(app):
    sys.argv = ["cli", "--list"]
    result = Clios(app)()
    assert result is None


def test_click_usage_error(app):
    sys.argv = ["cli", "--show"]
    with pytest.raises(SystemExit):
        Clios(app)()


def test_click_app_show(app):
    @app.register(name="test_op")
    def test_op():
        return "test"

    sys.argv = ["cli", "--show", "test_op"]
    result = Clios(app)()
    assert result is None


def test_click_app_dry_run(app):
    @app.register(name="test_op")
    def test_op():
        return "test"

    sys.argv = ["cli", "--dry-run", "test_op"]
    result = Clios(app)()
    assert result is None


def test_click_app_run(app):
    @app.register(name="test_op")
    def test_op():
        return None

    sys.argv = ["cli", "test_op"]
    result = Clios(app)()
    assert result is None
