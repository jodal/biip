"""Support for parsing of GS1-128 data."""

from __future__ import annotations

from biip.gs1._application_identifiers import GS1ApplicationIdentifier
from biip.gs1._prefixes import GS1Prefix
from biip.gs1._element_strings import (  # noqa: Must be imported early
    GS1ElementString,
)
from biip.gs1._messages import GS1Message


__all__ = [
    "GS1ApplicationIdentifier",
    "GS1ElementString",
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
        >>> msg.as_hri()
        '(01)07032069804988(15)210526(10)0329'
        >>> len(msg.element_strings)
        3
        >>> msg.element_strings[0]
        GS1ElementString(ai=GS1ApplicationIdentifier(ai='01',
        description='Global Trade Item Number (GTIN)', data_title='GTIN',
        fnc1_required=False, format='N2+N14'), value='07032069804988',
        groups=['07032069804988'], date=None)
        >>> msg.element_strings[1]
        GS1ElementString(ai=GS1ApplicationIdentifier(ai='15',
        description='Best before date (YYMMDD)', data_title='BEST BEFORE or
        BEST BY', fnc1_required=False, format='N2+N6'), value='210526',
        groups=['210526'], date=datetime.date(2021, 5, 26))
        >>> msg.element_strings[2]
        GS1ElementString(ai=GS1ApplicationIdentifier(ai='10',
        description='Batch or lot number', data_title='BATCH/LOT',
        fnc1_required=True, format='N2+X..20'), value='0329',
        groups=['0329'], date=None)
    """
    element_strings = []
    rest = value[:]

    while rest:
        element_string = GS1ElementString.extract(rest)
        element_strings.append(element_string)
        rest = rest[len(element_string) :]

    return GS1Message(value=value, element_strings=element_strings)
