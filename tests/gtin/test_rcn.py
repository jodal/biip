from decimal import Decimal
from typing import Optional, Union

import pytest
from moneyed import Money

from biip import ParseError
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


def test_gtin_14_with_rcn_prefix_is_not_an_rcn() -> None:
    # The value below is a GTIN-14 composed of packaging level 1 and a valid RCN-13.
    gtin = Gtin.parse("12991111111110", rcn_region=None)

    assert isinstance(gtin, Gtin)
    assert not isinstance(gtin, Rcn)
    assert gtin.format == GtinFormat.GTIN_14


@pytest.mark.parametrize(
    "rcn_region, value, weight, price, money",
    [
        # NOTE: These examples are constructed from a template. This should be
        # extended with actual examples from either specifications or real
        # Baltic products.
        #
        # Estonia
        (RcnRegion.ESTONIA, "2311111112345", Decimal("1.234"), None, None),
        (RcnRegion.ESTONIA, "2411111112342", Decimal("12.34"), None, None),
        (RcnRegion.ESTONIA, "2511111112349", Decimal("123.4"), None, None),
        (RcnRegion.ESTONIA, "2911111111111", None, None, None),
        # Latvia
        (RcnRegion.LATVIA, "2311111112345", Decimal("1.234"), None, None),
        (RcnRegion.LATVIA, "2411111112342", Decimal("12.34"), None, None),
        (RcnRegion.LATVIA, "2511111112349", Decimal("123.4"), None, None),
        (RcnRegion.LATVIA, "2911111111111", None, None, None),
        # Lithuania
        (RcnRegion.LITHUANIA, "2311111112345", Decimal("1.234"), None, None),
        (RcnRegion.LITHUANIA, "2411111112342", Decimal("12.34"), None, None),
        (RcnRegion.LITHUANIA, "2511111112349", Decimal("123.4"), None, None),
        (RcnRegion.LITHUANIA, "2911111111111", None, None, None),
    ],
)
def test_region_baltics(
    rcn_region: RcnRegion,
    value: str,
    weight: Optional[Decimal],
    price: Optional[Decimal],
    money: Optional[Money],
) -> None:
    # The three Baltic countries share the same rules and allocation pool.
    #
    # References:
    #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf

    rcn = Gtin.parse(value, rcn_region=rcn_region)

    assert isinstance(rcn, Rcn)
    assert rcn.region == rcn_region
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
        ("2388060112344", Decimal("1.234"), None, None),
        ("2488060112341", Decimal("12.34"), None, None),
        ("2588060112348", Decimal("123.4"), None, None),
        ("2911111111111", None, None, None),
    ],
)
def test_region_finland(
    value: str,
    weight: Optional[Decimal],
    price: Optional[Decimal],
    money: Optional[Money],
) -> None:
    # References:
    #   https://gs1.fi/en/instructions/gs1-company-prefix/how-identify-product-gtin

    rcn = Gtin.parse(value, rcn_region=RcnRegion.FINLAND)

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.FINLAND
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


@pytest.mark.parametrize(
    "value, weight, price, money",
    [
        ("2302148210869", Decimal("1.086"), None, None),  # Norvegia 1kg
        ("2368091402263", Decimal("0.226"), None, None),  # Stange kyllingbryst
        ("2911111111111", None, None, None),
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
        ("2911111111111", None, None, None),
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
    "value, rcn_region",
    [
        ("ee", RcnRegion.ESTONIA),
        ("fi", RcnRegion.FINLAND),
        ("gb", RcnRegion.GREAT_BRITAIN),
        ("lv", RcnRegion.LATVIA),
        ("lt", RcnRegion.LITHUANIA),
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


@pytest.mark.parametrize(
    "value, rcn_region",
    [
        ("233", RcnRegion.ESTONIA),
        ("246", RcnRegion.FINLAND),
        ("826", RcnRegion.GREAT_BRITAIN),
        ("428", RcnRegion.LATVIA),
        ("440", RcnRegion.LITHUANIA),
        ("578", RcnRegion.NORWAY),
        ("752", RcnRegion.SWEDEN),
        # Unknown numeric codes returns None:
        ("999", None),
        # Integers are converted to strings before lookup:
        (233, RcnRegion.ESTONIA),
        # Integers are padded to three digits before lookup:
        (8, None),  # Albania, once supported by Biip.
    ],
)
def test_rcn_region_lookup_by_iso_3166_1_numeric_code(
    value: Union[int, str], rcn_region: RcnRegion
) -> None:
    result = RcnRegion.from_iso_3166_1_numeric_code(value)

    assert result == rcn_region


def test_fails_when_iso_3166_1_code_is_too_long() -> None:
    with pytest.raises(ValueError) as exc_info:
        RcnRegion.from_iso_3166_1_numeric_code("1234")

    assert (
        str(exc_info.value)
        == "Expected ISO 3166-1 numeric code to be 3 digits, got '1234'."
    )


def test_fails_when_iso_3166_1_code_is_unknown_string() -> None:
    with pytest.raises(ValueError) as exc_info:
        RcnRegion.from_iso_3166_1_numeric_code("foo")

    assert (
        str(exc_info.value)
        == "Expected ISO 3166-1 numeric code to be 3 digits, got 'foo'."
    )


def test_rcn_usage_repr() -> None:
    assert repr(RcnUsage.COMPANY) == "RcnUsage.COMPANY"


def test_rcn_region_repr() -> None:
    assert repr(RcnRegion.ESTONIA) == "RcnRegion.ESTONIA"
