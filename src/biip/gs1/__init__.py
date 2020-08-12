"""Support for parsing of GS1-128 data."""

from __future__ import annotations

from biip.gs1._application_identifiers import GS1ApplicationIdentifier
from biip.gs1._prefixes import GS1Prefix
from biip.gs1._elements import GS1Element  # noqa: Must be imported early
from biip.gs1._messages import GS1Message


__all__ = [
    "GS1ApplicationIdentifier",
    "GS1Element",
    "GS1Message",
    "GS1Prefix",
    "parse",
]


def parse(value: str) -> GS1Message:
    """Parse a GS1-128 barcode data string.

    Args:
        value: The string to parse.

    Returns:
        ``GS1Message`` with one or more ``GS1Element``.
    """
    elements = []
    rest = value[:]

    while rest:
        element = GS1Element.extract(rest)
        elements.append(element)
        rest = rest[len(element) :]

    return GS1Message(value=value, elements=elements)
