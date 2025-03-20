"""Support for barcode data with GS1 messages.

The `biip.gs1_messages` module contains Biip's support for parsing data
consisting of GS1 messages and element strings. GS1 messages are text strings
consisting of one or more GS1 element strings. Each GS1 Element String is
identified by a GS1 Application Identifier (AI) prefix followed by the element's
value.

Data of this format is found in the following types of barcodes:

- [GS1-128](https://en.wikipedia.org/wiki/Code_128)
- [GS1 DataBar](https://en.wikipedia.org/wiki/GS1_DataBar_Coupon)
- [GS1 DataMatrix](https://en.wikipedia.org/wiki/Data_Matrix)
- [GS1 QR Code](https://en.wikipedia.org/wiki/QR_code)

If you only want to parse GS1 Messages, you can import the GS1 Message parser
directly instead of using [`biip.parse()`][biip.parse].

    >>> from biip.gs1_messages import GS1Message

If the parsing succeeds, it returns a [`GS1Message`][biip.gs1_messages.GS1Message]
object.

    >>> msg = GS1Message.parse("010703206980498815210526100329")

The [`GS1Message`][biip.gs1_messages.GS1Message] can be represented as an HRI,
short for "human readable interpretation", using
[`msg.as_hri()`][biip.gs1_messages.GS1Message.as_hri]. The HRI is the text
usually printed below or next to the barcode.

    >>> msg.value
    '010703206980498815210526100329'
    >>> msg.as_hri()
    '(01)07032069804988(15)210526(10)0329'

HRI can also be parsed using
[`GS1Message.parse_hri()`][biip.gs1_messages.GS1Message.parse_hri].

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
            check_digit=8
        )
    )

The message object has [`msg.get()`][biip.gs1_messages.GS1Message.get] and
[`msg.filter()`][biip.gs1_messages.GS1Message.filter] methods to lookup element
strings either by the Application Identifier's "data title" or its AI number.

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
        date=datetime.date(2021, 5, 26)
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
        ]
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
from biip.gs1_messages._element_strings import GS1ElementString
from biip.gs1_messages._messages import GS1Message

__all__ = [
    "DEFAULT_SEPARATOR_CHARS",
    "GS1ElementString",
    "GS1Message",
]
