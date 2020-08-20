from decimal import Decimal
from typing import Optional

from moneyed import Money

import pytest

from biip import ParseError
from biip.gtin import Gtin, GtinFormat, Rcn, RcnRegion, RcnUsage


@pytest.mark.parametrize(
    "value, format, usage",
    [
        # RCN-8
        ("00011112", GtinFormat.GTIN_8, RcnUsage.COMPANY),
        ("00099998", GtinFormat.GTIN_8, RcnUsage.COMPANY),
        # RCN-12
        ("020111111112", GtinFormat.GTIN_12, RcnUsage.GEOGRAPHICAL),
        ("029111111115", GtinFormat.GTIN_12, RcnUsage.GEOGRAPHICAL),
        ("040111111110", GtinFormat.GTIN_12, RcnUsage.COMPANY),
        ("049111111113", GtinFormat.GTIN_12, RcnUsage.COMPANY),
        ("200111111118", GtinFormat.GTIN_12, RcnUsage.GEOGRAPHICAL),
        ("299111111112", GtinFormat.GTIN_12, RcnUsage.GEOGRAPHICAL),
        # RCN-13
        ("2001111111119", GtinFormat.GTIN_13, RcnUsage.GEOGRAPHICAL),
        ("2991111111113", GtinFormat.GTIN_13, RcnUsage.GEOGRAPHICAL),
    ],
)
def test_gtin_parse_may_return_rcn_instance(
    value: str, format: GtinFormat, usage: RcnUsage
) -> None:
    rcn = Gtin.parse(value, rcn_region=RcnRegion.SWEDEN)

    assert isinstance(rcn, Rcn)
    assert rcn.format == format
    assert rcn.usage == usage
    if usage == RcnUsage.GEOGRAPHICAL:
        assert rcn.region == RcnRegion.SWEDEN
    else:
        assert rcn.region is None


def test_rcn_without_specified_region() -> None:
    rcn = Gtin.parse("2991111111113", rcn_region=None)

    assert isinstance(rcn, Rcn)
    assert rcn.format == GtinFormat.GTIN_13
    assert rcn.usage == RcnUsage.GEOGRAPHICAL
    assert rcn.region is None
    assert rcn.weight is None
    assert rcn.price is None
    assert rcn.money is None


@pytest.mark.parametrize(
    "value, weight, price, money",
    [
        # NOTE: These examples are constructed from a template. This should be
        # extended with actual examples from either specifications or real
        # Baltic products.
        ("2311111112345", Decimal("1.234"), None, None),
        ("2411111112342", Decimal("12.34"), None, None),
        ("2511111112349", Decimal("123.4"), None, None),
        ("2911111111111", None, None, None),
    ],
)
def test_region_baltics(
    value: str,
    weight: Optional[Decimal],
    price: Optional[Decimal],
    money: Optional[Money],
) -> None:
    # The three Baltic countries share the same rules and allocation pool.
    #
    # References:
    #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf

    rcn = Gtin.parse(value, rcn_region=RcnRegion.BALTICS)

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.BALTICS
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


@pytest.mark.parametrize(
    "value, weight, price, money",
    [
        # NOTE: These examples are constructed from a template. This should be
        # extended with actual examples from either specifications or real
        # British products.
        ("2011122912346", None, Decimal("12.34"), Money("12.34", "GBP")),
        ("2911111111111", None, None, None),
    ],
)
def test_region_great_britain(
    value: str,
    weight: Optional[Decimal],
    price: Optional[Decimal],
    money: Optional[Money],
) -> None:
    # References:
    #   https://www.gs1uk.org/how-to-barcode-variable-measure-items

    rcn = Gtin.parse(value, rcn_region=RcnRegion.GREAT_BRITAIN)

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.GREAT_BRITAIN
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


def test_region_great_britain_fails_with_invalid_price_check_digit() -> None:
    # The digit 8 in the value below is the price check digit. The correct value is 9.

    with pytest.raises(ParseError) as exc_info:
        Gtin.parse("2011122812349", rcn_region=RcnRegion.GREAT_BRITAIN)

    assert str(exc_info.value) == (
        "Invalid price check digit for price data '1234' in RCN '2011122812349': "
        "Expected 9, got 8."
    )


@pytest.mark.parametrize(
    "value, weight, price, money",
    [
        # Norvegia 1kg
        ("2302148210869", Decimal("1.086"), None, None)
    ],
)
def test_region_norway(
    value: str,
    weight: Optional[Decimal],
    price: Optional[Decimal],
    money: Optional[Money],
) -> None:
    # References: TODO: Find specification.

    rcn = Gtin.parse(value, rcn_region=RcnRegion.NORWAY)

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.NORWAY
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


@pytest.mark.parametrize(
    "value, weight, price, money",
    [
        ("2088060112343", None, Decimal("12.34"), Money("12.34", "SEK")),
        ("2188060112340", None, Decimal("123.4"), Money("123.4", "SEK")),
        ("2288060112347", None, Decimal("1234"), Money("1234", "SEK")),
        ("2388060112344", Decimal("1.234"), None, None),
        ("2488060112341", Decimal("12.34"), None, None),
        ("2588060112348", Decimal("123.4"), None, None),
    ],
)
def test_region_sweden(
    value: str,
    weight: Optional[Decimal],
    price: Optional[Decimal],
    money: Optional[Money],
) -> None:
    # References:
    #   https://www.gs1.se/en/our-standards/Identify/variable-weight-number1/

    rcn = Gtin.parse(value, rcn_region=RcnRegion.SWEDEN)

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.SWEDEN
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money
