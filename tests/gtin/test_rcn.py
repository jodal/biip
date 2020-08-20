import pytest

from biip.gtin import Gtin, GtinFormat, Rcn, RcnUsage


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
    rcn = Gtin.parse(value)

    assert isinstance(rcn, Rcn)
    assert rcn.format == format
    assert rcn.usage == usage
