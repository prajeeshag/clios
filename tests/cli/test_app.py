# type: ignore
import sys

import pytest

from clios.cli.app import Clios


@pytest.fixture
def app():
    return Clios()


def test_operator_registration(app):
    @app.operator(name="test_op")
    def test_op():
        return "test"

    assert app.operators.get("test_op")


def test_click_app_list(app):
    sys.argv = ["cli", "--list"]
    result = app()
    assert result is None


def test_click_app_show(app):
    @app.operator(name="test_op")
    def test_op():
        return "test"

    sys.argv = ["cli", "--show", "test_op"]
    result = app()
    assert result is None


def test_click_app_dry_run(app):
    @app.operator(name="test_op")
    def test_op():
        return "test"

    sys.argv = ["cli", "--dry-run", "test_op"]
    result = app()
    assert result is None


def test_click_app_run(app):
    @app.operator(name="test_op")
    def test_op():
        return None

    sys.argv = ["cli", "test_op"]
    result = app()
    assert result is None
