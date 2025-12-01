# type: ignore
import pytest

from clios.core.operator_fn import OperatorFns


def test_set_key_exist():
    reg = OperatorFns()
    reg["k"] = "object"
    with pytest.raises(AssertionError) as e:
        reg["k"] = "object"
    assert str(e.value) == "Operator 'k' already exists. Reassignment is not allowed."


def test_update_key_exist():
    reg = OperatorFns()
    reg1 = OperatorFns()
    reg["k"] = "object"
    reg1["k"] = "object"
    with pytest.raises(AssertionError) as e:
        reg.update(reg1)
    assert str(e.value) == "Operator 'k' already exists. Reassignment is not allowed."


def test_update_only_take_same_type():
    reg = OperatorFns()
    reg["k"] = "object"
    with pytest.raises(TypeError) as e:
        reg.update({"k": "object"})
    assert (
        str(e.value)
        == f"update() only accept a single positional argument of type {OperatorFns}"
    )


def test_update_does_not_take_kwds():
    reg = OperatorFns()
    reg["k"] = "object"
    with pytest.raises(TypeError) as e:
        reg.update(k="object")
    assert (
        str(e.value)
        == f"update() only accept a single positional argument of type {OperatorFns}"
    )
