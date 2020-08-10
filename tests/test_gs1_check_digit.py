import pytest

from biip.gs1_check_digit import numeric_check_digit


def test_numeric_check_digit_with_nonnumeric_value() -> None:
    with pytest.raises(ValueError) as exc_info:
        numeric_check_digit("abc")

    assert str(exc_info.value) == "Expected numeric value, got 'abc'."


@pytest.mark.parametrize(
    "value, expected",
    [
        # Example from reference
        ("37610425002123456", 9),
        # GTIN-13 from a product
        ("629104150021", 3),
        ("703801005447", 1),
        # ISBN from a book
        ("978820551237", 5),
        # GLN for an organization
        ("708000382434", 9),
    ],
)
def test_numeric_check_digit(value: str, expected: int) -> None:
    assert numeric_check_digit(value) == expected
