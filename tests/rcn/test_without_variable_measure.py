import pytest

from biip import EncodeError
from biip.checksums import gs1_standard_check_digit
from biip.gtin import Gtin
from biip.rcn import Rcn, RcnRegion


@pytest.mark.parametrize(
    ("rcn_region", "value", "expected"),
    [
        (RcnRegion.DENMARK, "2712341002251", "2712341000004"),  # GTIN-13
        (RcnRegion.DENMARK, "02712341002251", "2712341000004"),  # GTIN-14
        (RcnRegion.ESTONIA, "2311111112345", "2311111100007"),
        (RcnRegion.FINLAND, "2311111112345", "2311111100007"),
        (RcnRegion.GERMANY, "2811111068708", "2811110000006"),  # GTIN-13
        (RcnRegion.GERMANY, "02811111068708", "2811110000006"),  # GTIN-14
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
    assert stripped_rcn.as_gtin_13() == expected
    assert stripped_rcn.region == original_rcn.region


@pytest.mark.parametrize(
    ("rcn_region", "nonvariable_prefixes"),
    [
        (
            RcnRegion.DENMARK,
            ["02", "20", "25", "29"],
        ),
        (
            RcnRegion.ESTONIA,
            ["02", "20", "21", "22", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.FINLAND,
            ["02", "20", "21", "22", "26", "27", "28", "29"],
        ),
        (
            RcnRegion.GERMANY,
            ["02", "20", "21", "24", "27"],
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
    rcn_region: RcnRegion, nonvariable_prefixes: list[str]
) -> None:
    for prefix in nonvariable_prefixes:
        payload = f"{prefix}1111111111"
        value = f"{payload}{gs1_standard_check_digit(payload)}"
        original_rcn = Gtin.parse(value, rcn_region=rcn_region)
        assert isinstance(original_rcn, Rcn)

        stripped_rcn = original_rcn.without_variable_measure()

        assert isinstance(stripped_rcn, Rcn)
        assert stripped_rcn.value == original_rcn.value
        assert stripped_rcn.region == original_rcn.region


@pytest.mark.parametrize(
    ("rcn_region", "value"),
    [
        (RcnRegion.NORWAY, "00012348"),  # GTIN-8
        (RcnRegion.NORWAY, "412345678903"),  # GTIN-12
        (RcnRegion.NORWAY, "0412345678903"),  # GTIN-13
        (RcnRegion.NORWAY, "00412345678903"),  # GTIN-14
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


@pytest.mark.parametrize(
    "value",
    [
        "96385074",  # GTIN-8
        "614141000036",  # GTIN-12
        "5901234123457",  # GTIN-13
        "98765432109213",  # GTIN-14
    ],
)
def test_without_variable_measure_keeps_gtin_unchanged(value: str) -> None:
    original_gtin = Gtin.parse(value)
    assert isinstance(original_gtin, Gtin)
    assert not isinstance(original_gtin, Rcn)

    stripped_gtin = original_gtin.without_variable_measure()

    assert isinstance(stripped_gtin, Gtin)
    assert not isinstance(stripped_gtin, Rcn)
    assert stripped_gtin.value == original_gtin.value


def test_without_variable_measure_fails_if_rules_are_unknown() -> None:
    rcn = Gtin.parse("2302148210869", rcn_region=None)
    assert isinstance(rcn, Rcn)

    with pytest.raises(EncodeError) as exc_info:
        rcn.without_variable_measure()

    assert str(exc_info.value) == (
        "Cannot zero out the variable measure part of '2302148210869' "
        "as the RCN rules for the geographical region None are unknown."
    )
