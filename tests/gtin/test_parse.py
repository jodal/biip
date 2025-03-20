"""Tests of parsing GTINs."""

import pytest

from biip import ParseError
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix
from biip.gtin import Gtin, GtinFormat


def test_parse_value_with_invalid_length() -> None:
    with pytest.raises(ParseError) as exc_info:
        Gtin.parse("123")

    assert (
        str(exc_info.value)
        == "Failed to parse '123' as GTIN: Expected 8, 12, 13, or 14 digits, got 3."
    )


@pytest.mark.parametrize("value", ["0123456789abc", "0123456789⁰⁰⁰"])
def test_parse_nonnumeric_value(value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        Gtin.parse(value)

    assert (
        str(exc_info.value)
        == f"Failed to parse {value!r} as GTIN: Expected a numerical value."
    )


def test_parse_gtin_13_with_invalid_check_digit() -> None:
    with pytest.raises(ParseError) as exc_info:
        Gtin.parse("5901234123458")

    assert (
        str(exc_info.value)
        == "Invalid GTIN check digit for '5901234123458': Expected 7, got 8."
    )


def test_parse_strips_surrounding_whitespace() -> None:
    gtin = Gtin.parse("  \t 5901234123457 \n  ")

    assert gtin.value == "5901234123457"


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
    assert Gtin.parse(value) == Gtin(
        value=value,
        format=GtinFormat.GTIN_8,
        prefix=GS1Prefix(value="00009", usage="GS1 US"),
        company_prefix=GS1CompanyPrefix(value="0000963"),
        payload="9638507",
        check_digit=4,
    )


@pytest.mark.parametrize(
    "value",
    [
        "00000017",
        "00000123",
        "00001236",
        "00012348",
        "00123457",
        "01234565",
        "07038013",
    ],
)
def test_parse_gtin_8_with_leading_zeros(value: str) -> None:
    gtin = Gtin.parse(value)
    assert gtin.value == value
    assert gtin.format == GtinFormat.GTIN_8


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-12
        "614141000036",
        # 0-padded to GTIN-13
        "0614141000036",
        # 0-padded to GTIN-14
        "00614141000036",
    ],
)
def test_parse_gtin_12_without_leading_zero(value: str) -> None:
    assert Gtin.parse(value) == Gtin(
        value=value,
        format=GtinFormat.GTIN_12,
        prefix=GS1Prefix(value="061", usage="GS1 US"),
        company_prefix=GS1CompanyPrefix(value="0614141"),
        payload="61414100003",
        check_digit=6,
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
    assert Gtin.parse(value) == Gtin(
        value=value,
        format=GtinFormat.GTIN_12,
        prefix=GS1Prefix(value="003", usage="GS1 US"),
        company_prefix=GS1CompanyPrefix(value="0036000"),
        payload="03600029145",
        check_digit=2,
    )


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-12
        "006000291455",
        # 0-padded to GTIN-13
        "00006000291455",
        # 0-padded to GTIN-14
        "00006000291455",  # noqa: PT014
    ],
)
def test_parse_gtin_12_with_2_leading_zero(value: str) -> None:
    assert Gtin.parse(value) == Gtin(
        value=value,
        format=GtinFormat.GTIN_12,
        prefix=GS1Prefix(value="0006", usage="GS1 US"),
        company_prefix=None,
        payload="00600029145",
        check_digit=5,
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
    assert Gtin.parse(value) == Gtin(
        value=value,
        format=GtinFormat.GTIN_12,
        prefix=GS1Prefix(value="00009", usage="GS1 US"),
        company_prefix=GS1CompanyPrefix(value="0000902"),
        payload="00090291451",
        check_digit=1,
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
    assert Gtin.parse(value) == Gtin(
        value=value,
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(value="590", usage="GS1 Poland"),
        company_prefix=None,
        payload="590123412345",
        check_digit=7,
    )


def test_parse_gtin_14() -> None:
    assert Gtin.parse("98765432109213") == Gtin(
        value="98765432109213",
        format=GtinFormat.GTIN_14,
        prefix=GS1Prefix(value="876", usage="GS1 Netherlands"),
        company_prefix=None,
        payload="9876543210921",
        check_digit=3,
        packaging_level=9,
    )


def test_parse_gtin_with_unknown_gs1_prefix() -> None:
    assert Gtin.parse("6712670000276") == Gtin(
        value="6712670000276",
        format=GtinFormat.GTIN_13,
        prefix=None,
        company_prefix=None,
        payload="671267000027",
        check_digit=6,
    )
