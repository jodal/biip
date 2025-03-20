"""Test of GS1 prefixes."""

import pytest

from biip import ParseError
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix


@pytest.mark.parametrize("bad_value", ["abcdef", "1a2b3c"])
def test_invalid_gs1_prefix(bad_value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1Prefix.extract(bad_value)

    assert str(exc_info.value) == f"Failed to get GS1 Prefix from {bad_value!r}."


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "0000001999",
            GS1Prefix(value="0000001", usage="Unused to avoid collision with GTIN-8"),
        ),
        ("060999", GS1Prefix(value="060", usage="GS1 US")),
        ("139999", GS1Prefix(value="139", usage="GS1 US")),
        ("6712670000276", None),  # Unassigned prefix
        ("701999", GS1Prefix(value="701", usage="GS1 Norway")),
        ("9781492053743", GS1Prefix(value="978", usage="Bookland (ISBN)")),
    ],
)
def test_gs1_prefix(value: str, expected: GS1Prefix) -> None:
    assert GS1Prefix.extract(value) == expected


def test_gs1_prefix_is_hashable() -> None:
    prefix = GS1Prefix.extract("978")

    assert hash(prefix) is not None


@pytest.mark.parametrize("bad_value", ["abcdef", "1a2b3c"])
def test_invalid_gs1_company_prefix(bad_value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1CompanyPrefix.extract(bad_value)

    assert (
        str(exc_info.value) == f"Failed to get GS1 Company Prefix from {bad_value!r}."
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            # Undefined prefix
            "0",
            None,
        ),
        (
            # Undefined prefix
            "0000031000000",
            None,
        ),
        # GLNs
        (
            # Oda's fulfillment center in Helsinki
            "6429830062707",
            GS1CompanyPrefix(value="64298300627"),
        ),
        # GTINs
        (
            # Soda from Ringnes AS
            "7044610873466",
            GS1CompanyPrefix(value="704461"),
        ),
        (
            # Chocolate from Ferrero SpA
            "8000500247167",
            GS1CompanyPrefix(value="8000500"),
        ),
        (
            # ISBNs are defined to have a prefix length of 0.
            "9781492053743",
            None,
        ),
        # SSCCs
        (
            # Coffee delivery from Nestlé
            "376130321109103420",
            GS1CompanyPrefix(value="376130321"),
        ),
    ],
)
def test_gs1_company_prefix(value: str, expected: GS1CompanyPrefix) -> None:
    assert GS1CompanyPrefix.extract(value) == expected


def test_gs1_company_prefix_is_hashable() -> None:
    prefix = GS1CompanyPrefix.extract("7044610873466")

    assert hash(prefix) is not None
