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
        A message object with one or more element strings.

    Example:
        >>> from biip.gs1 import parse
        >>> msg = parse("010703206980498815210526100329")
        >>> msg.value
        '010703206980498815210526100329'
        >>> len(msg.elements)
        3
        >>> msg.elements[0]
        GS1Element(value='07032069804988', ai=GS1ApplicationIdentifier(ai='01',
        description='Global Trade Item Number (GTIN)', data_title='GTIN',
        fnc1_required=False, format='N2+N14'), groups=['07032069804988'],
        date=None)
        >>> msg.elements[1]
        GS1Element(value='210526', ai=GS1ApplicationIdentifier(ai='15',
        description='Best before date (YYMMDD)', data_title='BEST BEFORE or
        BEST BY', fnc1_required=False, format='N2+N6'), groups=['210526'],
        date=datetime.date(2021, 5, 26))
        >>> msg.elements[2]
        GS1Element(value='0329', ai=GS1ApplicationIdentifier(ai='10',
        description='Batch or lot number', data_title='BATCH/LOT',
        fnc1_required=True, format='N2+X..20'), groups=['0329'], date=None)
    """
    elements = []
    rest = value[:]

    while rest:
        element = GS1Element.extract(rest)
        elements.append(element)
        rest = rest[len(element) :]

    return GS1Message(value=value, elements=elements)
