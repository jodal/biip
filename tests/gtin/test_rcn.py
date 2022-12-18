import pytest

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
    "value, rcn_region",
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
    rcn = Gtin.parse(
        "0211111111114",
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
    assert repr(RcnRegion.ESTONIA) == "RcnRegion.ESTONIA"
