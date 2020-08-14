import pytest

from biip.gs1.checksums import (
    numeric_check_digit,
    price_check_digit,
)


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
        ("950110153100", 0),
        # ISBN from a book
        ("978820551237", 5),
        # GLN for an organization
        ("708000382434", 9),
    ],
)
def test_numeric_check_digit(value: str, expected: int) -> None:
    assert numeric_check_digit(value) == expected


def test_price_check_digit_with_nonnumeric_value() -> None:
    with pytest.raises(ValueError) as exc_info:
        price_check_digit("abc")

    assert str(exc_info.value) == "Expected numeric value, got 'abc'."


@pytest.mark.parametrize(
    "value",
    [
        # Too short
        "123",
        # Too long
        "123456",
    ],
)
def test_price_check_digit_on_values_with_wrong_length(value: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        price_check_digit(value)

    assert (
        str(exc_info.value)
        == f"Expected input of length 4 or 5, got {value!r}."
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        # Four-digit price field
        ("2875", 9),
        # Five-digit price field
        ("14685", 6),
    ],
)
def test_price_check_digit(value: str, expected: int) -> None:
    assert price_check_digit(value) == expected
