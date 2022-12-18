"""Tests of parsing SSCCs."""

import pytest

from biip import ParseError
from biip.gs1 import GS1CompanyPrefix, GS1Prefix
from biip.sscc import Sscc


def test_parse() -> None:
    sscc = Sscc.parse("157035381410375177")

    assert sscc == Sscc(
        value="157035381410375177",
        prefix=GS1Prefix(value="570", usage="GS1 Denmark"),
        company_prefix=GS1CompanyPrefix(value="5703538"),
        extension_digit=1,
        payload="15703538141037517",
        check_digit=7,
    )


def test_parse_strips_surrounding_whitespace() -> None:
    sscc = Sscc.parse("  \t 157035381410375177 \n  ")

    assert sscc.value == "157035381410375177"


def test_parse_value_with_invalid_length() -> None:
    with pytest.raises(ParseError) as exc_info:
        Sscc.parse("123")

    assert (
        str(exc_info.value)
        == "Failed to parse '123' as SSCC: Expected 18 digits, got 3."
    )


@pytest.mark.parametrize("value", ["012345678901234abc", "012345678901234⁰⁰⁰"])
def test_parse_nonnumeric_value(value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        Sscc.parse(value)

    assert (
        str(exc_info.value)
        == f"Failed to parse {value!r} as SSCC: Expected a numerical value."
    )


def test_parse_with_invalid_check_digit() -> None:
    with pytest.raises(ParseError) as exc_info:
        Sscc.parse("376130321109103421")

    assert (
        str(exc_info.value)
        == "Invalid SSCC check digit for '376130321109103421': Expected 0, got 1."
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        ("157035381410375177", "1 5703538 141037517 7"),
        ("357081300469846950", "3 5708130 046984695 0"),
        ("370595680445154697", "3 705956 8044515469 7"),
        # GS1 Prefix 671 is currently unassigned:
        ("376130321109103420", "3 7613032110910342 0"),
    ],
)
def test_as_hri(value: str, expected: str) -> None:
    sscc = Sscc.parse(value)

    assert sscc.as_hri() == expected


def test_as_hri_with_too_low_company_prefix_length() -> None:
    sscc = Sscc.parse("376130321109103420")

    with pytest.raises(ValueError) as exc_info:
        sscc.as_hri(company_prefix_length=6)

    assert (
        str(exc_info.value) == "Expected company prefix length between 7 and 10, got 6."
    )


def test_as_hri_with_too_high_company_prefix_length() -> None:
    sscc = Sscc.parse("376130321109103420")

    with pytest.raises(ValueError) as exc_info:
        sscc.as_hri(company_prefix_length=11)

    assert (
        str(exc_info.value)
        == "Expected company prefix length between 7 and 10, got 11."
    )
