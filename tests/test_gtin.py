"""Tests of Global Trade Item Number (GTIN)."""

import pytest

from biip import ParseError
from biip.gs1_prefixes import GS1Prefix
from biip.gtin import GTIN, GTINFormat, parse


def test_parse_value_with_invalid_length() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse("123")

    assert (
        str(exc_info.value)
        == "Failed parsing '123' as GTIN: Expected 8, 12, 13, or 14 characters, got 3."
    )


def test_parse_nonnumeric_value() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse("0123456789abc")

    assert (
        str(exc_info.value)
        == "Failed parsing '0123456789abc' as GTIN: Expected a numerical value."
    )


def test_parse_gtin_13_with_invalid_check_digit() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse("5901234123458")

    assert (
        str(exc_info.value)
        == "Invalid GTIN check digit for '5901234123458': Expected 7, got 8."
    )


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-8
        "96385074",
        # 0-padded to GTIN-12
        "000096385074",
        # 0-padded to GTIN-13
        "0000096385074",
        # 0-padded to GTIN-14
        "00000096385074",
    ],
)
def test_parse_gtin_8(value: str) -> None:
    assert parse(value) == GTIN(
        value=value,
        format=GTINFormat.GTIN_8,
        prefix=GS1Prefix(value="963", usage="Global Office - GTIN-8"),
        payload="9638507",
        check_digit=4,
        packaging_level=None,
    )


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-12
        "123601057072",
        # 0-padded to GTIN-13
        "0123601057072",
        # 0-padded to GTIN-14
        "00123601057072",
    ],
)
def test_parse_gtin_12_without_leading_zero(value: str) -> None:
    assert parse(value) == GTIN(
        value=value,
        format=GTINFormat.GTIN_12,
        prefix=GS1Prefix(value="123", usage="GS1 US"),
        payload="12360105707",
        check_digit=2,
        packaging_level=None,
    )


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-12
        "036000291452",
        # 0-padded to GTIN-13
        "0036000291452",
        # 0-padded to GTIN-14
        "00036000291452",
    ],
)
def test_parse_gtin_12_with_1_leading_zero(value: str) -> None:
    assert parse(value) == GTIN(
        value=value,
        format=GTINFormat.GTIN_12,
        prefix=GS1Prefix(value="036", usage="GS1 US"),
        payload="03600029145",
        check_digit=2,
        packaging_level=None,
    )


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-12
        "006000291455",
        # 0-padded to GTIN-13
        "00006000291455",
        # 0-padded to GTIN-14
        "00006000291455",
    ],
)
def test_parse_gtin_12_with_2_leading_zero(value: str) -> None:
    assert parse(value) == GTIN(
        value=value,
        format=GTINFormat.GTIN_12,
        prefix=GS1Prefix(value="006", usage="GS1 US"),
        payload="00600029145",
        check_digit=5,
        packaging_level=None,
    )


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-12
        "000902914511",
        # 0-padded to GTIN-13
        "0000902914511",
        # 0-padded to GTIN-14
        "00000902914511",
    ],
)
def test_parse_gtin_12_with_3_leading_zero(value: str) -> None:
    assert parse(value) == GTIN(
        value=value,
        format=GTINFormat.GTIN_12,
        prefix=GS1Prefix(value="0009", usage="GS1 US"),
        payload="00090291451",
        check_digit=1,
        packaging_level=None,
    )


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-13
        "5901234123457",
        # 0-padded to GTIN-14
        "05901234123457",
    ],
)
def test_parse_gtin_13(value: str) -> None:
    assert parse(value) == GTIN(
        value=value,
        format=GTINFormat.GTIN_13,
        prefix=GS1Prefix(value="590", usage="GS1 Poland"),
        payload="590123412345",
        check_digit=7,
        packaging_level=None,
    )


def test_parse_gtin_14() -> None:
    assert parse("98765432109213") == GTIN(
        value="98765432109213",
        format=GTINFormat.GTIN_14,
        prefix=GS1Prefix(value="876", usage="GS1 Netherlands"),
        payload="9876543210921",
        check_digit=3,
        packaging_level=9,
    )
