"""Tests of parsing GLNs."""

import pytest

from biip import ParseError
from biip.gln import Gln
from biip.gs1 import GS1Prefix


def test_parse() -> None:
    gln = Gln.parse("1234567890128")

    assert gln == Gln(
        value="1234567890128",
        prefix=GS1Prefix(value="123", usage="GS1 US"),
        payload="123456789012",
        check_digit=8,
    )


def test_parse_strips_surrounding_whitespace() -> None:
    gln = Gln.parse("  \t 1234567890128 \n  ")

    assert gln.value == "1234567890128"


def test_parse_value_with_invalid_length() -> None:
    with pytest.raises(ParseError) as exc_info:
        Gln.parse("123")

    assert (
        str(exc_info.value)
        == "Failed to parse '123' as GLN: Expected 13 digits, got 3."
    )


def test_parse_nonnumeric_value() -> None:
    with pytest.raises(ParseError) as exc_info:
        Gln.parse("123456789o128")

    assert (
        str(exc_info.value)
        == "Failed to parse '123456789o128' as GLN: Expected a numerical value."
    )


def test_parse_with_invalid_check_digit() -> None:
    with pytest.raises(ParseError) as exc_info:
        Gln.parse("1234567890127")

    assert (
        str(exc_info.value)
        == "Invalid GLN check digit for '1234567890127': Expected 8, got 7."
    )


def test_as_gln() -> None:
    gln = Gln.parse("  \t 1234567890128 \n  ")

    assert gln.as_gln() == "1234567890128"
