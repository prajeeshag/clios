import inspect

from clios.operator.utils import get_typed_signature


class Test_get_typed_signature:
    def test_(self):
        def test_function(a: int, b: str, c: float = 3.14) -> None:
            pass

        expected_signature = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    name="a",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=int,
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="b",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=str,
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="c",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=float,
                    default=3.14,
                ),
            ],
            return_annotation=None,
        )

        assert get_typed_signature(test_function) == expected_signature

    def test_with_forward_ref(self):
        def test_function(a: "int", b: str, c: float = 3.14) -> None:
            pass

        expected_signature = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    name="a",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=int,
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="b",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=str,
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="c",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=float,
                    default=3.14,
                ),
            ],
            return_annotation=None,
        )

        assert get_typed_signature(test_function) == expected_signature

    def test_with_no_type_hints(self):
        def test_function(a, b, c=3.14) -> None:  # type: ignore
            pass

        expected_signature = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    name="a",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=inspect.Parameter.empty,
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="b",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=inspect.Parameter.empty,
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="c",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=inspect.Parameter.empty,
                    default=3.14,
                ),
            ],
            return_annotation=None,
        )

        assert get_typed_signature(test_function) == expected_signature  # type: ignore

    def test_with_complex_type_hints(self):
        from typing import Dict, List, Tuple

        def test_function(
            a: List[int], b: Tuple[str, float], c: Dict[str, int] = {"a": 1}
        ) -> None:
            pass

        expected_signature = inspect.Signature(
            parameters=[
                inspect.Parameter(
                    name="a",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=List[int],
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="b",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Tuple[str, float],
                    default=inspect.Parameter.empty,
                ),
                inspect.Parameter(
                    name="c",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Dict[str, int],
                    default={"a": 1},
                ),
            ],
            return_annotation=None,
        )

        assert get_typed_signature(test_function) == expected_signature
