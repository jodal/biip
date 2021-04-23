"""Tests of parsing UPC."""

import pytest

from biip import ParseError
from biip.upc import Upc, UpcFormat


def test_parse_upc_a() -> None:
    upc = Upc.parse("042100005264")

    assert upc == Upc(
        value="042100005264",
        format=UpcFormat.UPC_A,
        payload="04210000526",
        check_digit=4,
    )


def test_parse_upc_e() -> None:
    upc = Upc.parse("425261")

    assert upc == Upc(
        value="425261",
        format=UpcFormat.UPC_E,
        payload="425261",
        check_digit=None,
    )


def test_parse_value_with_invalid_length() -> None:
    with pytest.raises(ParseError) as exc_info:
        Upc.parse("123")

    assert (
        str(exc_info.value)
        == "Failed to parse '123' as UPC: Expected 6 or 12 digits, got 3."
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
