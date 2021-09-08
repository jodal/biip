from typing import List

import pytest

from biip import EncodeError
from biip.gs1.checksums import numeric_check_digit
from biip.gtin import Gtin, Rcn, RcnRegion


@pytest.mark.parametrize(
    "rcn_region, value, expected",
    [
        (RcnRegion.ESTONIA, "2311111112345", "2311111100007"),
        (RcnRegion.FINLAND, "2311111112345", "2311111100007"),
        (RcnRegion.GREAT_BRITAIN, "2011122912346", "2011122000005"),
        (RcnRegion.LATVIA, "2311111112345", "2311111100007"),
        (RcnRegion.LITHUANIA, "2311111112345", "2311111100007"),
        (RcnRegion.NORWAY, "2302148210869", "2302148200006"),
        (RcnRegion.SWEDEN, "2088060112343", "2088060100005"),
    ],
)
def test_without_variable_measure_strips_variable_parts(
    rcn_region: RcnRegion, value: str, expected: str
) -> None:
    original_rcn = Gtin.parse(value, rcn_region=rcn_region)
    assert isinstance(original_rcn, Rcn)

    stripped_rcn = original_rcn.without_variable_measure()

    assert isinstance(stripped_rcn, Rcn)
    assert stripped_rcn.value == expected
    assert stripped_rcn.region == original_rcn.region


@pytest.mark.parametrize(
    "rcn_region, nonvariable_prefixes",
    [
        (
            RcnRegion.ESTONIA,
            ["02", "20", "21", "22", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.FINLAND,
            ["02", "20", "21", "22", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.GREAT_BRITAIN,
            ["21", "22", "23", "24", "25", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.LATVIA,
            ["02", "20", "21", "22", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.LITHUANIA,
            ["02", "20", "21", "22", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.NORWAY,
            ["02", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.SWEDEN,
            ["02", "26", "27", "28", "29"],
        ),
    ],
)
def test_without_variable_measure_keeps_nonvariable_rcn_unchanged(
    rcn_region: RcnRegion, nonvariable_prefixes: List[str]
) -> None:
    for prefix in nonvariable_prefixes:
        payload = f"{prefix}1111111111"
        value = f"{payload}{numeric_check_digit(payload)}"
        original_rcn = Gtin.parse(value, rcn_region=rcn_region)
        assert isinstance(original_rcn, Rcn)

        stripped_rcn = original_rcn.without_variable_measure()

        assert isinstance(stripped_rcn, Rcn)
        assert stripped_rcn.value == original_rcn.value
        assert stripped_rcn.region == original_rcn.region


@pytest.mark.parametrize(
    "rcn_region, value",
    [
        (RcnRegion.NORWAY, "00012348"),
        (RcnRegion.NORWAY, "0412345678903"),
    ],
)
def test_without_variable_measure_keeps_company_rcn_unchanged(
    rcn_region: RcnRegion, value: str
) -> None:
    original_rcn = Gtin.parse(value, rcn_region=rcn_region)
    assert isinstance(original_rcn, Rcn)

    stripped_rcn = original_rcn.without_variable_measure()

    assert isinstance(stripped_rcn, Rcn)
    assert stripped_rcn.value == original_rcn.value
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
