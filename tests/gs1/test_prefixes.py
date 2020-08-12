"""Test of GS1 prefixes."""

import pytest

from biip import ParseError
from biip.gs1 import GS1Prefix


@pytest.mark.parametrize("bad_value", ["abcdef", "199999"])
def test_invalid_gs1_prefix(bad_value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1Prefix.extract(bad_value)

    assert (
        str(exc_info.value) == f"Failed to get GS1 Prefix from {bad_value!r}."
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "0000001999",
            GS1Prefix(
                value="0000001", usage="Unused to avoid collision with GTIN-8",
            ),
        ),
        ("060999", GS1Prefix(value="060", usage="GS1 US")),
        ("139999", GS1Prefix(value="139", usage="GS1 US")),
        ("701999", GS1Prefix(value="701", usage="GS1 Norway")),
        ("978-1-492-05374-3", GS1Prefix(value="978", usage="Bookland (ISBN)")),
    ],
)
def test_gs1_prefix(value: str, expected: GS1Prefix) -> None:
    assert GS1Prefix.extract(value) == expected
