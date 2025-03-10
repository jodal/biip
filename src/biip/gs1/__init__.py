"""Support for barcode data with GS1 element strings.

The `biip.gs1` module contains Biip's support for parsing data consisting of GS1
Element Strings. Each Element String is identified by a GS1 Application
Identifier (AI) prefix.

Data of this format is found in the following types of barcodes:

- GS1-128
- GS1 DataBar
- GS1 DataMatrix
- GS1 QR Code

If you only want to parse GS1 Messages, you can import the GS1 Message parser
directly instead of using `biip.parse()`.

    >>> from biip.gs1 import GS1Message

If the parsing succeeds, it returns a `GS1Message` object.

    >>> msg = GS1Message.parse("010703206980498815210526100329")

The `GS1Message` has a raw value as well as an HRI, short for "human readable
interpretation". The HRI is the text usually printed below or next to the
barcode.

    >>> msg.value
    '010703206980498815210526100329'
    >>> msg.as_hri()
    '(01)07032069804988(15)210526(10)0329'

HRI can also be parsed.

    >>> msg = GS1Message.parse_hri("(01)07032069804988(15)210526(10)0329")

A message can contain multiple element strings.

    >>> len(msg.element_strings)
    3

In this example, the first element string is a GTIN.

    >>> pprint(msg.element_strings[0])
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='01',
            description='Global Trade Item Number (GTIN)',
            data_title='GTIN',
            fnc1_required=False,
            format='N2+N14'
        ),
        value='07032069804988',
        pattern_groups=[
            '07032069804988'
        ],
        gln=None,
        gln_error=None,
        gtin=Gtin(
            value='07032069804988',
            format=GtinFormat.GTIN_13,
            prefix=GS1Prefix(
                value='703',
                usage='GS1 Norway'
            ),
            company_prefix=GS1CompanyPrefix(
                value='703206'
            ),
            payload='703206980498',
            check_digit=8,
            packaging_level=None
        ),
        gtin_error=None,
        sscc=None,
        sscc_error=None,
        date=None,
        datetime=None,
        decimal=None,
        money=None
    )

The message object has `GS1Message.get()` and `GS1Message.filter()`
methods to lookup element strings either by the Application Identifier's
"data title" or its AI number.

    >>> pprint(msg.get(data_title='BEST BY'))
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='15',
            description='Best before date (YYMMDD)',
            data_title='BEST BEFORE or BEST BY',
            fnc1_required=False,
            format='N2+N6'
        ),
        value='210526',
        pattern_groups=[
            '210526'
        ],
        gln=None,
        gln_error=None,
        gtin=None,
        gtin_error=None,
        sscc=None,
        sscc_error=None,
        date=datetime.date(2021, 5, 26),
        datetime=None,
        decimal=None,
        money=None
    )
    >>> pprint(msg.get(ai="10"))
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='10',
            description='Batch or lot number',
            data_title='BATCH/LOT',
            fnc1_required=True,
            format='N2+X..20'
        ),
        value='0329',
        pattern_groups=[
            '0329'
        ],
        gln=None,
        gln_error=None,
        gtin=None,
        gtin_error=None,
        sscc=None,
        sscc_error=None,
        date=None,
        datetime=None,
        decimal=None,
        money=None
    )
"""

ASCII_GROUP_SEPARATOR = "\x1d"

DEFAULT_SEPARATOR_CHARS: tuple[str] = (ASCII_GROUP_SEPARATOR,)
"""The default separator character is `<GS>`, ASCII value 29.

References:
   GS1 General Specifications, section 7.8.3.
"""

# The following must be imported in this specific order.
# ruff: noqa: E402, I001
from biip.gs1._symbology import GS1Symbology
from biip.gs1._application_identifiers import GS1ApplicationIdentifier
from biip.gs1._prefixes import GS1CompanyPrefix, GS1Prefix
from biip.gs1._element_strings import GS1ElementString
from biip.gs1._messages import GS1Message

__all__ = [
    "DEFAULT_SEPARATOR_CHARS",
    "GS1ApplicationIdentifier",
    "GS1CompanyPrefix",
    "GS1ElementString",
    "GS1Message",
    "GS1Prefix",
    "GS1Symbology",
]
