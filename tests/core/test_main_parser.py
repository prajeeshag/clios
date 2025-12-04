from unittest.mock import Mock

from clios.core.main_parser import ParserAbc, _KnownTypes


def make_param(
    name,
    type_,
    is_positional=True,
    is_required=True,
    default="",
    description="",
    choices=None,
    is_var=False,
    is_kw=False,
    is_varkw=False,
):
    """Small helper to create a fake parameter object."""
    p = Mock()
    p.name = name
    p.type_ = type_
    p.is_positional_param = is_positional
    p.is_required = is_required
    p.default = default
    p.description = description
    p.choices = choices or []
    p.is_var_param = is_var
    p.is_keyword_param = is_kw
    p.is_var_keyword = is_varkw
    p.empty = object()
    return p


class DummyParser(ParserAbc):
    """Concrete subclass to allow instantiation while mocking methods."""

    def get_operator(self, *a, **k):
        raise NotImplementedError()

    def is_inline_operator_name(self, *a, **k):
        raise NotImplementedError()

    def get_inline_operator_fn(self, *a, **k):
        raise NotImplementedError()

    def get_synopsis(self, operator_fn, operator_name, **kw):
        return f" {operator_name} SYNOPSIS"  # simple predictable return


def test_get_details_basic():
    parser = DummyParser()

    # Fake operator function
    op_fn = Mock()
    op_fn.short_description = "Short desc"
    op_fn.long_description = "Long desc"

    op_fn.parameters = [
        make_param("x", int, default=10, description="integer value"),
        make_param("y", str, is_required=False, default="", description="text"),
        make_param(
            "mode",
            str,
            is_positional=False,
            is_kw=True,
            default="fast",
            description="execution mode",
            choices=["fast", "slow"],
        ),
    ]

    synopsis, short_desc, long_desc, args_doc, kwds_doc = parser.get_details(
        name="foo",
        op_fn=op_fn,
        exe_name="xcdo-",
    )

    # --- Assertions ---
    assert synopsis == "xcdo- foo SYNOPSIS"
    assert short_desc == "Short desc"
    assert long_desc == "Long desc"

    # Positional args
    assert len(args_doc) == 2
    assert args_doc[0]["name"] == "x"
    assert args_doc[0]["type"] == _KnownTypes.INT.name
    assert args_doc[0]["default_value"] == "10"

    assert args_doc[1]["name"] == "y"
    assert args_doc[1]["default_value"] == "''"  # empty string case

    # Keyword args
    assert len(kwds_doc) == 1
    mode_doc = kwds_doc[0]
    assert mode_doc["name"] == "mode"
    assert mode_doc["choices"] == "fast, slow"
    assert mode_doc["required"] == "Required"
