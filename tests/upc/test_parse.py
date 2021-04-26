"""Tests of parsing UPCs."""

import pytest

from biip import ParseError
from biip.upc import Upc, UpcFormat


def test_parse_upc_a() -> None:
    upc = Upc.parse("042100005264")

    assert upc == Upc(
        value="042100005264",
        format=UpcFormat.UPC_A,
        number_system_digit=0,
        payload="04210000526",
        check_digit=4,
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "425261",  # Length is 6: Implicit number system 0, no check digit.
            Upc(
                value="425261",
                format=UpcFormat.UPC_E,
                number_system_digit=0,
                payload="0425261",
                check_digit=4,
            ),
        ),
        (
            "1425261",  # Length is 7: Explicit number system 1, no check digit.
            Upc(
                value="1425261",
                format=UpcFormat.UPC_E,
                number_system_digit=1,
                payload="1425261",
                check_digit=1,
            ),
        ),
        (
            "14252611",  # Length is 8: Explicit number system 1 and check digit.
            Upc(
                value="14252611",
                format=UpcFormat.UPC_E,
                number_system_digit=1,
                payload="1425261",
                check_digit=1,
            ),
        ),
    ],
)
def test_parse_upc_e(value: str, expected: Upc) -> None:
    assert Upc.parse(value) == expected


def test_parse_value_with_invalid_length() -> None:
    with pytest.raises(ParseError) as exc_info:
        Upc.parse("123")

    assert (
        str(exc_info.value)
        == "Failed to parse '123' as UPC: Expected 6, 7, 8, or 12 digits, got 3."
    )


def test_parse_nonnumeric_value() -> None:
    with pytest.raises(ParseError) as exc_info:
        Upc.parse("012345678abc")

    assert (
        str(exc_info.value)
        == "Failed to parse '012345678abc' as UPC: Expected a numerical value."
    )


def test_parse_upc_a_with_invalid_check_digit() -> None:
    with pytest.raises(ParseError) as exc_info:
        Upc.parse("042100005263")

    assert (
        str(exc_info.value)
        == "Invalid UPC-A check digit for '042100005263': Expected 4, got 3."
    )


def test_parse_upc_e_with_invalid_check_digit() -> None:
    with pytest.raises(ParseError) as exc_info:
        Upc.parse("04252613")

    assert (
        str(exc_info.value)
        == "Invalid UPC-E check digit for '04252613': Expected 4, got 3."
    )


@pytest.mark.parametrize("number_system", range(2, 10))
def test_parse_upc_e_with_invalid_number_system(number_system: int) -> None:
    with pytest.raises(ParseError) as exc_info:
        Upc.parse(f"{number_system}425261")

    assert str(exc_info.value) == (
        f"Invalid UPC-E number system for '{number_system}425261': "
        f"Expected 0 or 1, got {number_system}."
    )


def test_parse_strips_surrounding_whitespace() -> None:
    upc = Upc.parse("  \t 042100005264 \n  ")

    assert upc.value == "042100005264"
