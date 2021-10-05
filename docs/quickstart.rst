==========
Quickstart
==========

The following examples should get you started with parsing barcode data using Biip.

See the API reference for details on the API and data fields used in the examples below.


Parsing barcode data
====================

Biip's primary API is the :func:`biip.parse` function.
It accepts a string of data from a barcode scanner and
returns a :class:`biip.ParseResult` object with any results or
raises a :class:`biip.ParseError` if all parsers fail.

Nearly all products you can buy in a store are marked with an UPC or EAN-13 barcode.
These barcodes contain a number called GTIN,
short for Global Trade Item Number,
which can be parsed by Biip::

    >>> import biip
    >>> result = biip.parse("5901234123457")
    >>> result
    ParseResult(
        value='5901234123457',
        symbology_identifier=None,
        gtin=Gtin(
            value='5901234123457',
            format=GtinFormat.GTIN_13,
            prefix=GS1Prefix(value='590', usage='GS1 Poland'),
            payload='590123412345',
            check_digit=7,
            packaging_level=None,
        ),
        gtin_error=None,
        upc=None,
        upc_error="Failed to parse '5901234123457' as UPC: Expected 6, 7, 8, or 12 digits, got 13.",
        sscc=None,
        sscc_error="Failed to parse '5901234123457' as SSCC: Expected 18 digits, got 13.",
        gs1_message=None,
        gs1_message_error="Failed to get GS1 Application Identifier from '5901234123457'.",
    )


Error handling
==============

Biip can parse several different data formats.
Thus, it'll return a result object with a mix of results and errors.
In the above example,
we can see that the data is successfully parsed as a GTIN
while parsing as an SSCC or GS1 Message failed,
and Biip returned error messages explaining why.

If all parsers fail, Biip raises a :class:`biip.ParseError`.
The exception's string representation contains detailed error messages
explaining why each parser failed to interpret the provided data::

    >>> biip.parse("12345678")
    Traceback (most recent call last):
        ...
    biip._exceptions.ParseError: Failed to parse '12345678':
    - Invalid GTIN check digit for '12345678': Expected 0, got 8.
    - UPC: Invalid UPC-E check digit for '12345678': Expected 0, got 8.
    - Failed to parse '12345678' as SSCC: Expected 18 digits, got 8.
    - Failed to parse GS1 AI (12) date from '345678'.

Biip always checks that the GTIN check digit is correct.
If the check digit doesn't match the payload, parsing fails.
In this case, Biip rejected ``12345678`` as a GTIN-8.


Symbology Identifiers
=====================

If you're using a barcode scanner which has enabled Symbology Identifier prefixes,
your data will have a three letter prefix,
e.g. ``]E0`` for EAN-13 barcodes.
If a Symbology Identifier is detected,
Biip will detect it and only try the relevant parsers::

    >>> biip.parse("]E09781492053743")
    ParseResult(
        value=']E09781492053743',
        symbology_identifier=SymbologyIdentifier(
            value=']E0',
            symbology=Symbology.EAN_UPC,
            modifiers='0',
            gs1_symbology=GS1Symbology.EAN_13,
        ),
        gtin=Gtin(
            value='9781492053743',
            format=GtinFormat.GTIN_13,
            prefix=GS1Prefix(value='978', usage='Bookland (ISBN)'),
            payload='978149205374',
            check_digit=3,
            packaging_level=None,
        ),
        gtin_error=None,
        upc=None,
        upc_error=None,
        sscc=None,
        sscc_error=None,
        gs1_message=None,
        gs1_message_error=None,
    )

In this example, we used the ISBN from a book.
As ISBNs are a subset of GTINs, this worked just like before.
Because the data was prefixed by a Symbology Identifier,
Biip only tried the GTIN parser.
This is reflected in the lack of error messages from the SSCC and GS1 Message parsers.


Global Trade Item Number (GTIN)
===============================

GTINs comes in multiple formats:
They are either 8, 12, 13, or 14 characters long,
and the GTIN variants are accordingly named GTIN-8, GTIN-12, GTIN-13, or GTIN-14.
Biip supports all GTIN formats.

Let's use the GTIN-12 ``123601057072`` as another example::

    >>> import biip
    >>> result = biip.parse("123601057072")
    >>> result.gtin
    Gtin(
        value='123601057072',
        format=GtinFormat.GTIN_12,
        prefix=GS1Prefix(value='012', usage='GS1 US'),
        payload='12360105707',
        check_digit=2,
        packaging_level=None,
    )

All GTINs can be encoded as any other GTIN variant that is longer than itself.
Thus, the canonical way to store a GTIN in a database is as a GTIN-14.
Similarly, you'll want to convert a GTIN to GTIN-14
before using it for a database lookup::

    >>> result.gtin.value
    '123601057072'
    >>> result.gtin.as_gtin_14()
    '00123601057072'

By consistently using GTIN-14 internally in your application,
you can avoid a lot of substring matching
to find the database objects related to the barcode.


Restricted Circulation Number (RCN)
-----------------------------------

If you have products where the price depends on the weight of each item,
and either the price or the weight are encoded in the GTIN,
you are dealing with Restricted Circulation Numbers, or RCN,
another subset of GTIN::

    >>> result = biip.parse("2011122912346")
    >>> result.gtin
    Rcn(
        value='2011122912346',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(
            value='201',
            usage='Used to issue Restricted Circulation Numbers within a geographic region (MO defined)',
        ),
        payload='201112291234',
        check_digit=6,
        packaging_level=None,
        usage=RcnUsage.GEOGRAPHICAL,
        region=None,
        weight=None,
        price=None,
        money=None,
    )

In the example above,
the number is detected to be an RCN,
and an instance of ``Rcn``,
a subclass of ``Gtin`` with a few additional fields,
is returned.

The rules for how to encode weight or price into an RCN
varies between geographical regions.
The national GS1 Member Organizations (MO) specify the rules for their region.
Biip already supports a few of these rulesets,
and you can easily add more
if detailed documentation on the market's rules is available.

Because of the market variations,
you must specify your geographical region
for Biip to be able to extract price and weight from the RCN::

    >>> from biip.gtin import RcnRegion
    >>> result = biip.parse("2011122912346", rcn_region=RcnRegion.GREAT_BRITAIN)
    >>> result.gtin
    Rcn(
        value='2011122912346',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(
            value='201',
            usage='Used to issue Restricted Circulation Numbers within a geographic region (MO defined)'
        ),
        payload='201112291234',
        check_digit=6,
        packaging_level=None,
        usage=RcnUsage.GEOGRAPHICAL,
        region=RcnRegion.GREAT_BRITAIN,
        weight=None,
        price=Decimal('12.34'),
        money=Money('12.34', 'GBP'),
    )

The ``price`` and ``money`` fields contain the same data.
The difference is that while ``price`` is a simple ``Decimal`` type,
``money`` also carries currency information.
The ``money`` field is only set if
the optional dependency ``py-moneyed`` is installed.


GS1 AI Element Strings
======================

Let us move away from consumer products.

The GS1 organization has specified a comprehensive system of
Application Identifiers (AI) covering most industry use cases.

It is helpful to get the terminology straight here,
as we use it throughout the Biip API:

- An *Application Identifier* (AI) is a number with 2-4 digits
  that specifies a data field's format and use.
- An AI prefix, together with its data field, is called an *Element String*.
- Multiple Element Strings read from a single barcode is called a *Message*.

AI Element Strings can be encoded using several different barcode types,
but the linear GS1-128 barcode format is the most common.


Serial Shipping Container Code (SSCC)
-------------------------------------

If we scan a GS1-128 barcode on a pallet,
we might get the data string ``00376130321109103420``:

    >>> result = biip.parse("00376130321109103420")
    >>> result.gs1_message
    GS1Message(
        value='00376130321109103420',
        element_strings=[
            GS1ElementString(
                ai=GS1ApplicationIdentifier(
                    ai='00',
                    description='Serial Shipping Container Code (SSCC)',
                    data_title='SSCC',
                    fnc1_required=False,
                    format='N2+N18',
                ),
                value='376130321109103420',
                pattern_groups=['376130321109103420'],
                gln=None,
                gtin=None,
                sscc=Sscc(
                    value='376130321109103420',
                    prefix=GS1Prefix(value='761', usage='GS1 Schweiz, Suisse, Svizzera'),
                    extension_digit=3,
                    payload='37613032110910342',
                    check_digit=0,
                ),
                date=None,
                decimal=None,
                money=None,
            ),
        ],
    )

From the above result,
we can see that the data is a Message that contains a single Element String.
The Element String has the AI ``00``,
which is the code for Serial Shipping Container Code, or SSCC for short.

Biip extracts the SSCC payload and validates its check digit.
The result is an :class:`~biip.sscc.Sscc` instance,
with fields like ``prefix`` and ``extension_digit``.

You can extract the Element String using
:meth:`~biip.gs1.GS1Message.get` and :meth:`~biip.gs1.GS1Mesage.filter`::

    >>> element_string = result.gs1_message.get(ai="00")
    >>> element_string.ai.data_title
    'SSCC'
    >>> element_string.sscc.prefix.usage
    'GS1 Schweiz, Suisse, Svizzera'

In case SSCCs are what you are primarily working with,
the :class:`~biip.sscc.Sscc` instance is also available directly from :class:`~biip.ParseResult`::

    >>> result.sscc == element_string.sscc
    True

If you need to display the barcode data in a more human readable way,
e.g. to print below a barcode,
you can use :meth:`~biip.gs1.GS1Message.as_hri`::

    >>> result.gs1_message.as_hri()
    '(00)376130321109103420'


Product IDs, expiration dates, and lot numbers
----------------------------------------------

If we unpack the pallet and scan the GS1-128 barcode on a logistic unit,
containing multiple trade units, we might get the data string
``010703206980498815210526100329``::

    >>> result = biip.parse("010703206980498815210526100329")
    >>> result.gs1_message.as_hri()
    '(01)07032069804988(15)210526(10)0329'

From the human-readable interpretation (HRI) above,
we can see that the data contains three Element Strings::

    >>> result.gs1_message.element_strings
    [
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='01',
                description='Global Trade Item Number (GTIN)',
                data_title='GTIN',
                fnc1_required=False,
                format='N2+N14',
            ),
            value='07032069804988',
            pattern_groups=['07032069804988'],
            gln=None,
            gtin=Gtin(
                value='07032069804988',
                format=GtinFormat.GTIN_13,
                prefix=GS1Prefix(value='703', usage='GS1 Norway'),
                payload='703206980498',
                check_digit=8,
                packaging_level=None,
            ),
            sscc=None,
            date=None,
            decimal=None,
            money=None,
        ),
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='15',
                description='Best before date (YYMMDD)',
                data_title='BEST BEFORE or BEST BY',
                fnc1_required=False,
                format='N2+N6',
            ),
            value='210526',
            pattern_groups=['210526'],
            gln=None,
            gtin=None,
            sscc=None,
            date=datetime.date(2021, 5, 26),
            decimal=None,
            money=None,
        ),
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='10',
                description='Batch or lot number',
                data_title='BATCH/LOT',
                fnc1_required=True,
                format='N2+X..20'
            ),
            value='0329',
            pattern_groups=['0329'],
            gln=None,
            gtin=None,
            sscc=None,
            date=None,
            decimal=None,
            money=None,
        ),
    ]

The first Element String is the GTIN of the trade item inside the logistic unit.
As with SSCC's,
this is also available directly from the :class:`~biip.ParseResult` instance::

    >>> result.gtin == result.gs1_message.element_strings[0].gtin
    True

The second Element String is the expiration date of the contained trade items.
To save you from interpreting the date value correctly yourself,
Biip does the job for you and exposes a :class:`~datetime.date` instance::

    >>> element_string = result.gs1_message.get(data_title="BEST BY")
    >>> element_string.date
    datetime.date(2021, 5, 26)

The last Element String is the batch or lot number of the items::

    >>> element_string = result.gs1_message.get(ai="10")
    >>> element_string.value
    '0329'


Variable-length fields
----------------------

About a third of the specified AIs don't have a fixed length.
How do we then know where the Element Strings ends,
and the next one starts?

In the example above,
the batch/lot number, with AI ``10``, is a variable-length field.
You can see this from the AI format, ``N2+X...20``,
which indicates a two-digit AI prefix
followed by a payload of up to 20 alphanumeric characters.
In this case,
we didn't need to do anything to handle the variable-length data field
because the batch/lot number Element String was the last one in the Message.

Let's try to reorder the expiration date and batch/lot number,
so that the batch/lot number comes in the middle of the Message::

    >>> result = biip.parse("010703206980498810032915210525")
    >>> result.gs1_message.as_hri()
    '(01)07032069804988(10)032915210525'

As we can see,
the batch/lot number didn't know where to stop,
so it consumed the remainder of the data,
including the full expiration date.

GS1-128 barcodes mark the end of variable-length Element Strings
with a *Function Code 1* (FNC1) symbol.
When the barcode scanner converts the barcode to a string of text,
it substitutes the FNC1 symbol with something else,
often with the "Group Separator" or "GS" ASCII character.
The GS ASCII character has a decimal value of 29 or hexadecimal value of 0x1D.

If we insert a byte with value 0x1D, after the end of the batch/lot number,
we get the following result::

    >>> result = biip.parse("0107032069804988100329\x1d15210525")
    >>> result.gs1_message.as_hri()
    '(01)07032069804988(10)0329(15)210525'

Once again, we've correctly detected all three Element Strings.

You might need to reconfigure your barcode scanner hardware
to use another separator character if:

- your barcode scanner doesn't insert the GS character, or
- some part of your scanning data pipeline cannot maintain the character as-is.

A reasonable choice for an alternative separator character
might be the pipe character, ``|``,
as this character cannot legally be a part of the payload in Element Strings.

If we configure the barcode scanner to use an alternative separator character,
we also need to tell Biip what character to expect::

    >>> result = biip.parse("0107032069804988100329|15210525", separator_chars=["|"])
    >>> result.gs1_message.as_hri()
    '(01)07032069804988(10)0329(15)210525'

Once again, all three Element Strings was successfully extracted.


Deep dive
=========

This quickstart guide covers the surface of Biip
and should get you quickly up and running.

If you need to dive deeper,
all parts of Biip have extensive docstrings
with references to the relevant parts of specifications from GS1 and ISO.
As a last resource, you have the code as well as a test suite with 100% code coverage.

Happy barcode scanning!
