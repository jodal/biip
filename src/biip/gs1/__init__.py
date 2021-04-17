"""Support for barcode data with GS1 element strings.

The :mod:`biip.gs1` module contains biip's support for parsing data
consisting of GS1 Element Strings. Each Element String is identified by a GS1
Application Identifier (AI) prefix.

Data of this format is found in the following types of barcodes:

- GS1-128
- GS1 DataBar
- GS1 DataMatrix
- GS1 QR Code

Example:
    >>> from biip.gs1 import GS1Message
    >>> msg = GS1Message.parse("010703206980498815210526100329")
    >>> msg.value
    '010703206980498815210526100329'
    >>> msg.as_hri()
    '(01)07032069804988(15)210526(10)0329'
    >>> len(msg.element_strings)
    3
    >>> msg.element_strings[0]
    GS1ElementString(ai=GS1ApplicationIdentifier(ai='01', description='Global
    Trade Item Number (GTIN)', data_title='GTIN', fnc1_required=False,
    format='N2+N14'), value='07032069804988',
    pattern_groups=['07032069804988'], gtin=Gtin(value='07032069804988',
    format=GtinFormat.GTIN_13, prefix=GS1Prefix(value='703', usage='GS1
    Norway'), payload='703206980498', check_digit=8, packaging_level=None),
    sscc=None, date=None, decimal=None, money=None)
    >>> msg.get(data_title='BEST BY')
    GS1ElementString(ai=GS1ApplicationIdentifier(ai='15', description='Best
    before date (YYMMDD)', data_title='BEST BEFORE or BEST BY',
    fnc1_required=False, format='N2+N6'), value='210526',
    pattern_groups=['210526'], gtin=None, sscc=None, date=datetime.date(2021, 5, 26),
    decimal=None, money=None)
    >>> msg.get(ai="10")
    GS1ElementString(ai=GS1ApplicationIdentifier(ai='10', description='Batch
    or lot number', data_title='BATCH/LOT', fnc1_required=True,
    format='N2+X..20'), value='0329', pattern_groups=['0329'], gtin=None,
    sscc=None, date=None, decimal=None, money=None)
"""

from typing import Tuple

#: The default separator character is <GS>, ASCII value 29.
#:
#: References:
#:   GS1 General Specifications, section 7.8.3.
DEFAULT_SEPARATOR_CHARS: Tuple[str] = ("\x1d",)

# The following must be imported in this specific order.
from biip.gs1._symbology import GS1Symbology  # isort:skip  # noqa: E402
from biip.gs1._application_identifiers import (  # isort:skip  # noqa: E402
    GS1ApplicationIdentifier,
)
from biip.gs1._prefixes import GS1Prefix  # isort:skip  # noqa: E402
from biip.gs1._element_strings import (  # isort:skip  # noqa: E402
    GS1ElementString,
)
from biip.gs1._messages import GS1Message  # isort:skip  # noqa: E402

__all__ = [
    "GS1Message",
    "GS1ElementString",
    "GS1ApplicationIdentifier",
    "GS1Prefix",
    "GS1Symbology",
    "DEFAULT_SEPARATOR_CHARS",
]
