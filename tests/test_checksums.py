import pytest

from biip.checksums import gs1_price_weight_check_digit, gs1_standard_check_digit


@pytest.mark.parametrize("value", ["abc", "⁰⁰⁰"])
def test_gs1_standard_check_digit_with_nonnumeric_value(value: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^Expected numeric value, got {value!r}.$",
    ):
        gs1_standard_check_digit(value)


@pytest.mark.parametrize(
    ("value", "expected"),
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
def test_gs1_standard_check_digit(value: str, expected: int) -> None:
    assert gs1_standard_check_digit(value) == expected


@pytest.mark.parametrize("value", ["abc", "⁰⁰⁰"])
def test_gs1_price_weight_check_digit_with_nonnumeric_value(value: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^Expected numeric value, got {value!r}.$",
    ):
        gs1_price_weight_check_digit(value)


@pytest.mark.parametrize(
    "value",
    [
        # Too short
        "123",
        # Too long
        "123456",
    ],
)
def test_gs1_price_weight_check_digit_on_values_with_wrong_length(value: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^Expected input of length 4 or 5, got {value!r}.$",
    ):
        gs1_price_weight_check_digit(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Four-digit price field
        ("2875", 9),
        # Five-digit price field
        ("14685", 6),
    ],
)
def test_gs1_price_weight_check_digit(value: str, expected: int) -> None:
    assert gs1_price_weight_check_digit(value) == expected
