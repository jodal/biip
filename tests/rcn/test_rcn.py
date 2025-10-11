from decimal import Decimal

import pytest
from moneyed import Money

from biip import ParseConfig
from biip.gs1_prefixes import GS1Prefix, GS18Prefix
from biip.gtin import Gtin, GtinFormat
from biip.rcn import Rcn, RcnRegion, RcnUsage


@pytest.mark.parametrize(
    ("value", "rcn_region", "expected"),
    [
        # RCN-8 for company internal use only
        (
            "00011112",
            None,
            Rcn(
                value="00011112",
                format=GtinFormat.GTIN_8,
                prefix=GS18Prefix.extract("000"),
                company_prefix=None,
                item_reference=None,
                payload="0001111",
                check_digit=2,
                packaging_level=None,
                usage=RcnUsage.COMPANY,
                region=None,
                weight=None,
                count=None,
                price=None,
                money=None,
            ),
        ),
        (
            "00099998",
            None,
            Rcn(
                value="00099998",
                format=GtinFormat.GTIN_8,
                prefix=GS18Prefix.extract("000"),
                company_prefix=None,
                item_reference=None,
                payload="0009999",
                check_digit=8,
                packaging_level=None,
                usage=RcnUsage.COMPANY,
                region=None,
                weight=None,
                count=None,
                price=None,
                money=None,
            ),
        ),
        #
        # RCN-12 for geographical use only
        (
            "201111111115",
            RcnRegion.SWEDEN,
            Rcn(
                value="201111111115",
                format=GtinFormat.GTIN_12,
                prefix=GS1Prefix.extract("020"),
                company_prefix=None,
                item_reference=None,
                payload="20111111111",
                check_digit=5,
                packaging_level=None,
                usage=RcnUsage.GEOGRAPHICAL,
                region=RcnRegion.SWEDEN,
                weight=None,
                count=None,
                price=None,
                money=None,
            ),
        ),
        (
            "291111111116",
            RcnRegion.SWEDEN,
            Rcn(
                value="291111111116",
                format=GtinFormat.GTIN_12,
                prefix=GS1Prefix.extract("029"),
                company_prefix=None,
                item_reference=None,
                payload="29111111111",
                check_digit=6,
                packaging_level=None,
                usage=RcnUsage.GEOGRAPHICAL,
                region=RcnRegion.SWEDEN,
                weight=None,
                count=None,
                price=None,
                money=None,
            ),
        ),
        #
        # RCN-12 for company internal use only
        (
            "401111111119",
            None,
            Rcn(
                value="401111111119",
                format=GtinFormat.GTIN_12,
                prefix=GS1Prefix.extract("040"),
                company_prefix=None,
                item_reference=None,
                payload="40111111111",
                check_digit=9,
                packaging_level=None,
                usage=RcnUsage.COMPANY,
                region=None,
                weight=None,
                count=None,
                price=None,
                money=None,
            ),
        ),
        (
            "491111111110",
            None,
            Rcn(
                value="491111111110",
                format=GtinFormat.GTIN_12,
                prefix=GS1Prefix.extract("049"),
                company_prefix=None,
                item_reference=None,
                payload="49111111111",
                check_digit=0,
                packaging_level=None,
                usage=RcnUsage.COMPANY,
                region=None,
                weight=None,
                count=None,
                price=None,
                money=None,
            ),
        ),
        #
        # RCN-13 for geographical use only
        (
            "2001111111119",
            RcnRegion.SWEDEN,
            Rcn(
                value="2001111111119",
                format=GtinFormat.GTIN_13,
                prefix=GS1Prefix.extract("200"),
                company_prefix=None,
                item_reference=None,
                payload="200111111111",
                check_digit=9,
                packaging_level=None,
                usage=RcnUsage.GEOGRAPHICAL,
                region=RcnRegion.SWEDEN,
                weight=None,
                count=None,
                price=Decimal("11.11"),
                money=Money("11.11", "SEK"),
            ),
        ),
        (
            "2302148210869",
            RcnRegion.NORWAY,
            Rcn(
                value="2302148210869",
                format=GtinFormat.GTIN_13,
                prefix=GS1Prefix.extract("230"),
                company_prefix=None,
                item_reference=None,
                payload="230214821086",
                check_digit=9,
                packaging_level=None,
                usage=RcnUsage.GEOGRAPHICAL,
                region=RcnRegion.NORWAY,
                weight=Decimal("1.086"),
                count=None,
                price=None,
                money=None,
            ),
        ),
    ],
)
def test_parse_rcn(value: str, rcn_region: RcnRegion | None, expected: Rcn) -> None:
    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=rcn_region))

    assert rcn == expected


def test_rcn_without_specified_region() -> None:
    rcn = Gtin.parse("2001111111119", config=ParseConfig(rcn_region=None))

    assert isinstance(rcn, Rcn)
    assert rcn.format == GtinFormat.GTIN_13
    assert rcn.usage == RcnUsage.GEOGRAPHICAL
    assert rcn.region is None
    assert rcn.weight is None
    assert rcn.price is None
    assert rcn.money is None


def test_gtin_14_with_rcn_prefix_is_not_an_rcn() -> None:
    # The value below is a GTIN-14 composed of packaging level 1 and a valid RCN-13.
    gtin = Gtin.parse("12991111111110", config=ParseConfig(rcn_region=None))

    assert isinstance(gtin, Gtin)
    assert not isinstance(gtin, Rcn)
    assert gtin.format == GtinFormat.GTIN_14


@pytest.mark.parametrize(
    ("value", "rcn_region"),
    [
        ("de", RcnRegion.GERMANY),
        ("dk", RcnRegion.DENMARK),
        ("ee", RcnRegion.ESTONIA),
        ("fi", RcnRegion.FINLAND),
        ("gb", RcnRegion.GREAT_BRITAIN),
        ("lt", RcnRegion.LITHUANIA),
        ("lv", RcnRegion.LATVIA),
        ("no", RcnRegion.NORWAY),
        ("se", RcnRegion.SWEDEN),
    ],
)
def test_rcn_region_can_be_specified_as_string(
    value: str, rcn_region: RcnRegion
) -> None:
    rcn = Gtin.parse("0211111111114", config=ParseConfig(rcn_region=value))

    assert isinstance(rcn, Rcn)
    assert rcn.region == rcn_region


def test_fails_when_rcn_region_is_unknown_string() -> None:
    with pytest.raises(
        ValueError,
        match=r"^'foo' is not a valid RcnRegion$",
    ):
        Gtin.parse("2311111112345", config=ParseConfig(rcn_region="foo"))


def test_rcn_usage_repr() -> None:
    assert repr(RcnUsage.COMPANY) == "RcnUsage.COMPANY"


def test_rcn_region_repr() -> None:
    assert repr(RcnRegion.ESTONIA) == "RcnRegion.ESTONIA"
