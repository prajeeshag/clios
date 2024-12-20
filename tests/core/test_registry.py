import pytest

from clios.core.registry import KeyExistsError
from clios.core.registry import _Registry as Registry  # type: ignore


def test_set_get():
    reg = Registry[str, str]()
    reg.add("k", "object")
    assert reg.get("k") == "object"
    assert reg.has_key("k") is True


def test_get_none():
    reg = Registry[str, str]()
    assert reg.has_key("k") is False
    with pytest.raises(KeyError):
        reg.get("k")


def test_set_key_exist():
    reg = Registry[str, str]()
    reg.add("k", "object")
    with pytest.raises(KeyExistsError) as e:
        reg.add("k", "object")
    assert str(e.value) == "Key 'k' already exists. Reassignment is not allowed."


def test_items():
    reg = Registry[str, str]()
    reg.add("k", "object")
    assert list(reg.items()) == [("k", "object")]
