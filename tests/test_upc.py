"""Tests of parsing UPC."""

import pytest

from biip import EncodeError, ParseError
from biip.upc import Upc, UpcFormat


def test_parse_upc_a() -> None:
    upc = Upc.parse("042100005264")

    assert upc == Upc(
        value="042100005264",
        format=UpcFormat.UPC_A,
        payload="04210000526",
        number_system_digit=0,
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
                payload="0425261",
                number_system_digit=0,
                check_digit=0,
            ),
        ),
        (
            "1425261",  # Length is 7: Explicit number system 1, no check digit.
            Upc(
                value="1425261",
                format=UpcFormat.UPC_E,
                payload="1425261",
                number_system_digit=1,
                check_digit=7,
            ),
        ),
        (
            "14252617",  # Length is 8: Explicit number system 1 and check digit.
            Upc(
                value="14252617",
                format=UpcFormat.UPC_E,
                payload="1425261",
                number_system_digit=1,
                check_digit=7,
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


def test_parse_strips_surrounding_whitespace() -> None:
    upc = Upc.parse("  \t 042100005264 \n  ")

    assert upc.value == "042100005264"


@pytest.mark.parametrize(
    "value, expected",
    [
        (  # UPC-A to UPC-A
            "123456789012",
            "123456789012",
        ),
        (  # Reverse of UPC-A suppression, condition A
            "02345673",
            "023456000073",
        ),
        (  # Reverse of UPC-A suppression, condition B
            "02345147",
            "023450000017",
        ),
        (  # Reverse of UPC-A suppression, condition C
            "06397126",
            "063200009716",
        ),
        (  # Reverse of UPC-A suppression, condition D
            "08679339",
            "086700000939",
        ),
    ],
)
def test_as_upc_a(value: str, expected: str) -> None:
    assert Upc.parse(value).as_upc_a() == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (  # 6-digit UPC-E, implicit number system 0, no check digit.
            "425261",
            "04252610",
        ),
        (  # 7-digit UPC-E, explicit number system 1, no check digit.
            "1425261",
            "14252617",
        ),
        (  # 8-digit UPC-E, explicit number system 1, with check digit.
            "14252617",
            "14252617",
        ),
        (  # UPC-A suppression, condition A
            "023456000073",
            "02345673",
        ),
        (  # UPC-A suppression, condition B
            "023450000017",
            "02345147",
        ),
        (  # UPC-A suppression, condition C
            "063200009716",
            "06397126",
        ),
        (  # UPC-A suppression, condition D
            "086700000939",
            "08679339",
        ),
    ],
)
def test_as_upc_e(value: str, expected: str) -> None:
    assert Upc.parse(value).as_upc_e() == expected


def test_as_upc_e_when_suppression_is_not_possible() -> None:
    with pytest.raises(EncodeError) as exc_info:
        Upc.parse("123456789012").as_upc_e()

    assert str(exc_info.value) == "UPC-A '123456789012' cannot be represented as UPC-E."
