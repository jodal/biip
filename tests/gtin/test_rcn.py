from decimal import Decimal
from typing import Optional

from moneyed import Money

import pytest

from biip import EncodeError, ParseError
from biip.gtin import Gtin, GtinFormat, Rcn, RcnRegion, RcnUsage


@pytest.mark.parametrize(
    "value, format, usage",
    [
        # RCN-8
        ("00011112", GtinFormat.GTIN_8, RcnUsage.COMPANY),
        ("00099998", GtinFormat.GTIN_8, RcnUsage.COMPANY),
        # RCN-12
        ("201111111115", GtinFormat.GTIN_12, RcnUsage.GEOGRAPHICAL),
        ("291111111116", GtinFormat.GTIN_12, RcnUsage.GEOGRAPHICAL),
        ("401111111119", GtinFormat.GTIN_12, RcnUsage.COMPANY),
        ("491111111110", GtinFormat.GTIN_12, RcnUsage.COMPANY),
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
        ("2302148210869", Decimal("1.086"), None, None),
        # Stange kyllingbryst
        ("2368091402263", Decimal("0.226"), None, None),
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


@pytest.mark.parametrize(
    "value, rcn_region, expected",
    [
        # Geopgraphical RCNs: Strip variable measure if we know how.
        ("2311111112345", RcnRegion.BALTICS, "2311111100007"),
        ("2011122912346", RcnRegion.GREAT_BRITAIN, "2011122000005"),
        ("2302148210869", RcnRegion.NORWAY, "2302148200006"),
        ("2088060112343", RcnRegion.SWEDEN, "2088060100005"),
        # Company RCNs: Return as is, as the data is opaque.
        ("00012348", RcnRegion.NORWAY, "00012348"),
        ("0412345678903", RcnRegion.NORWAY, "0412345678903"),
    ],
)
def test_without_variable_measure(
    value: str, rcn_region: RcnRegion, expected: str
) -> None:
    original_rcn = Gtin.parse(value, rcn_region=rcn_region)
    assert isinstance(original_rcn, Rcn)

    stripped_rcn = original_rcn.without_variable_measure()

    assert isinstance(stripped_rcn, Rcn)
    assert stripped_rcn.value == expected
    assert stripped_rcn.region == original_rcn.region


def test_without_variable_measure_fails_if_rules_are_unknown() -> None:
    rcn = Gtin.parse("2302148210869", rcn_region=None)
    assert isinstance(rcn, Rcn)

    with pytest.raises(EncodeError) as exc_info:
        rcn.without_variable_measure()

    assert str(exc_info.value) == (
        "Cannot zero out the variable measure part of '2302148210869' "
        "as the RCN rules for the geographical region None are unknown."
    )


@pytest.mark.parametrize(
    "value, rcn_region",
    [
        ("baltics", RcnRegion.BALTICS),
        ("gb", RcnRegion.GREAT_BRITAIN),
        ("no", RcnRegion.NORWAY),
        ("se", RcnRegion.SWEDEN),
    ],
)
def test_rcn_region_can_be_specified_as_string(
    value: str, rcn_region: RcnRegion
) -> None:
    rcn = Gtin.parse(
        "2311111112345",
        rcn_region=value,  # type: ignore
    )

    assert isinstance(rcn, Rcn)
    assert rcn.region == rcn_region


def test_fails_when_rcn_region_is_unknown_string() -> None:
    with pytest.raises(ValueError) as exc_info:
        Gtin.parse(
            "2311111112345",
            rcn_region="foo",  # type: ignore
        )

    assert str(exc_info.value) == "'foo' is not a valid RcnRegion"


def test_rcn_usage_repr() -> None:
    assert repr(RcnUsage.COMPANY) == "RcnUsage.COMPANY"


def test_rcn_region_repr() -> None:
    assert repr(RcnRegion.BALTICS) == "RcnRegion.BALTICS"
