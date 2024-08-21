import pytest

from clio.registry import KeyExistsError, Registry


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
