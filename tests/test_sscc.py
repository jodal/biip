"""Tests of parsing SSCCs."""

from typing import Optional

import pytest

from biip import ParseError
from biip.gs1 import GS1Prefix
from biip.sscc import Sscc


def test_parse() -> None:
    sscc = Sscc.parse("376130321109103420")

    assert sscc == Sscc(
        value="376130321109103420",
        prefix=GS1Prefix(value="761", usage="GS1 Schweiz, Suisse, Svizzera"),
        extension_digit=3,
        payload="37613032110910342",
        check_digit=0,
    )


def test_parse_value_with_invalid_length() -> None:
    with pytest.raises(ParseError) as exc_info:
        Sscc.parse("123")

    assert (
        str(exc_info.value)
        == "Failed to parse '123' as SSCC: Expected 18 digits, got 3."
    )


def test_parse_nonnumeric_value() -> None:
    with pytest.raises(ParseError) as exc_info:
        Sscc.parse("012345678901234abc")

    assert (
        str(exc_info.value)
        == "Failed to parse '012345678901234abc' as SSCC: Expected a numerical value."
    )


def test_parse_with_invalid_check_digit() -> None:
    with pytest.raises(ParseError) as exc_info:
        Sscc.parse("376130321109103421")

    assert (
        str(exc_info.value)
        == "Invalid SSCC check digit for '376130321109103421': Expected 0, got 1."
    )


def test_parse_strips_surrounding_whitespace() -> None:
    sscc = Sscc.parse("  \t 376130321109103420 \n  ")

    assert sscc.value == "376130321109103420"


@pytest.mark.parametrize(
    "prefix_length, expected",
    [
        (None, "3 761 3032110910342 0"),
        (7, "3 761 3032 110910342 0"),
        (8, "3 761 30321 10910342 0"),
        (9, "3 761 303211 0910342 0"),
        (10, "3 761 3032110 910342 0"),
    ],
)
def test_as_hri(prefix_length: Optional[int], expected: str) -> None:
    sscc = Sscc.parse("376130321109103420")

    assert sscc.as_hri(company_prefix_length=prefix_length) == expected


def test_as_hri_with_too_low_company_prefix_length() -> None:
    sscc = Sscc.parse("376130321109103420")

    with pytest.raises(ValueError) as exc_info:
        sscc.as_hri(company_prefix_length=6)

    assert (
        str(exc_info.value)
        == "Expected company prefix length between 7 and 10, got 6."
    )


def test_as_hri_with_too_high_company_prefix_length() -> None:
    sscc = Sscc.parse("376130321109103420")

    with pytest.raises(ValueError) as exc_info:
        sscc.as_hri(company_prefix_length=11)

    assert (
        str(exc_info.value)
        == "Expected company prefix length between 7 and 10, got 11."
    )
