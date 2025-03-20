# Quickstart

The following examples should get you started with parsing barcode data
using Biip.

Throughout the examples, we'll use [Rich](https://rich.readthedocs.io/) for
pretty-printing the results. This is entirely optional, but it makes the output
more readable. The examples are complete, so you can copy and paste them into
your own Python shell to follow along.

```python
>>> from rich import print
>>> import biip
```

See the [API reference](../api/) for details on the API and data fields used
in the examples below.

## Parsing barcode data

Biip's primary API is the [`biip.parse()`][biip.parse] function. It accepts a
string of data from a barcode scanner and returns a
[`ParseResult`][biip.ParseResult] object with any results.

Nearly all products you can buy in a store are marked with an UPC or
EAN-13 barcode. These barcodes contain a number called GTIN, short for
Global Trade Item Number, which can be parsed by Biip:

```python hl_lines="4-11"
>>> print(biip.parse("7032069804988"))
ParseResult(
    value='7032069804988',
    gtin=Gtin(
        value='7032069804988',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(value='703', usage='GS1 Norway'),
        company_prefix=GS1CompanyPrefix(value='703206'),
        payload='703206980498',
        check_digit=8
    ),
    upc_error="Failed to parse '7032069804988' as UPC: Expected 6, 7, 8, or 12 digits, got 13.",
    sscc_error="Failed to parse '7032069804988' as SSCC: Expected 18 digits, got 13.",
    gs1_message=GS1Message(
        value='7032069804988',
        element_strings=[
            GS1ElementString(
                ai=GS1ApplicationIdentifier(
                    ai='7032',
                    description='Number of processor with three-digit ISO country code',
                    data_title='PROCESSOR # 2',
                    fnc1_required=True,
                    format='N3+X..27'
                ),
                value='069804988',
                pattern_groups=['069', '804988']
            )
        ]
    )
)
```

## Error handling

Biip can parse several different data formats. Thus, it'll return a
result object with a mix of results and errors. In the above example, we
can see that the data is successfully parsed as a GTIN while parsing as
an SSCC or GS1 Message failed, and Biip returned error messages
explaining why.

If all parsers fail, Biip still returns a
[`ParseResult`][biip.ParseResult]. The result's error fields contains
detailed error messages explaining why each parser failed to interpret the
provided data:

```python
>>> print(biip.parse("12345678"))
ParseResult(
    value='12345678',
    gtin_error="Invalid GTIN check digit for '12345678': Expected 0, got 8.",
    upc_error="Invalid UPC-E check digit for '12345678': Expected 0, got 8.",
    sscc_error="Failed to parse '12345678' as SSCC: Expected 18 digits, got 8.",
    gs1_message_error="Failed to match '12345678' with GS1 AI (12) pattern '^12(\\d{2}(?:0\\d|1[0-2])(?:[0-2]\\d|3[01]))$'."
)
```

Biip always checks that the GTIN check digit is correct. If the check
digit doesn't match the payload, parsing fails. In this case, Biip
rejected `12345678` as a GTIN-8.

## Symbology Identifiers

If you're using a barcode scanner which has enabled Symbology
Identifier prefixes, your data will have a three letter prefix, e.g.
`]E0` for EAN-13 barcodes. If a Symbology Identifier is detected, Biip
will detect it and use the symbology identifier to only try parsing the payload
with the parsers relevant for the specified symbology:

```python
>>> print(biip.parse("]E09781492053743"))
ParseResult(
    value=']E09781492053743',
    symbology_identifier=SymbologyIdentifier(
        value=']E0',
        iso_symbology=ISOSymbology.EAN_UPC,
        modifiers='0',
        gs1_symbology=GS1Symbology.EAN_13
    ),
    gtin=Gtin(
        value='9781492053743',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(value='978', usage='Bookland (ISBN)'),
        company_prefix=None,
        payload='978149205374',
        check_digit=3
    )
)
```

In this example, we used the ISBN from a book. As ISBNs are a subset of
GTINs, this worked just like before. Because the data was prefixed by a
Symbology Identifier, Biip only tried the GTIN parser. This is reflected
in the lack of both results and error messages from the UPC, SSCC and GS1
Message parsers.

## Global Trade Item Number (GTIN)

GTINs comes in multiple formats: They are either 8, 12, 13, or 14
characters long, and the GTIN variants are accordingly named GTIN-8,
GTIN-12, GTIN-13, or GTIN-14. Biip supports all GTIN formats.

Let's use the GTIN-12 `123601057072` as another example:

```python hl_lines="5-12"
>>> result = biip.parse("123601057072")
>>> print(result)
ParseResult(
    value='123601057072',
    gtin=Gtin(
        value='123601057072',
        format=GtinFormat.GTIN_12,
        prefix=GS1Prefix(value='012', usage='GS1 US'),
        company_prefix=None,
        payload='12360105707',
        check_digit=2
    ),
    upc=Upc(
        value='123601057072',
        format=UpcFormat.UPC_A,
        number_system_digit=1,
        payload='12360105707',
        check_digit=2
    ),
    sscc_error="Failed to parse '123601057072' as SSCC: Expected 18 digits, got 12.",
    gs1_message_error="Failed to get GS1 Application Identifier from '7072'."
)
```

### Use GTIN-14 in databases

All GTINs can be encoded as any other GTIN variant that is longer than
itself. Thus, the canonical way to store a GTIN in a database is as a
GTIN-14. Similarly, you'll want to convert a GTIN to GTIN-14 using
[`as_gtin_14()`][biip.gtin.Gtin.as_gtin_14] before using it for a database
lookup:

```python
>>> result.gtin.value
'123601057072'
>>> result.gtin.as_gtin_14()
'00123601057072'
```

By consistently using GTIN-14 internally in your application, you can
avoid a lot of substring matching to find the database objects related
to the barcode.

### Restricted Circulation Number (RCN)

If you have products where the price depends on the weight of each item,
and either the price or the weight are encoded in the GTIN, you are
dealing with Restricted Circulation Numbers, or RCN, another subset of
GTIN:

```python hl_lines="4-14"
>>> print(biip.parse("2011122912346"))
ParseResult(
    value='2011122912346',
    gtin=Rcn(
        value='2011122912346',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(
            value='201',
            usage='Used to issue GS1 Restricted Circulation Numbers within a geographic region (MO defined)'
        ),
        company_prefix=None,
        payload='201112291234',
        check_digit=6
    ),
    upc_error="Failed to parse '2011122912346' as UPC: Expected 6, 7, 8, or 12 digits, got 13.",
    sscc_error="Failed to parse '2011122912346' as SSCC: Expected 18 digits, got 13.",
    gs1_message_error="Failed to match '122912346' with GS1 AI (12) pattern
'^12(\\d{2}(?:0\\d|1[0-2])(?:[0-2]\\d|3[01]))$'."
)
```

In the example above, the number is detected to be an RCN, and an instance of
[`Rcn`][biip.rcn.Rcn], a subclass of [`Gtin`][biip.gtin.Gtin], which may
contain a few additional fields, is returned.

The rules for how to encode weight or price into an RCN varies between
geographical regions. The national GS1 Member Organizations (MO) specify
the rules for their region. Biip already supports a few of these
rulesets, and you can easily add more if detailed documentation on the
market's rules is available.

Because of the market variations, you must specify your geographical
region for Biip to be able to extract price or weight from the RCN:

```python hl_lines="1-2 15-18"
>>> from biip.gtin import RcnRegion
>>> print(biip.parse("2011122912346", rcn_region=RcnRegion.GREAT_BRITAIN))
ParseResult(
    value='2011122912346',
    gtin=Rcn(
        value='2011122912346',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(
            value='201',
            usage='Used to issue GS1 Restricted Circulation Numbers within a geographic region (MO defined)'
        ),
        company_prefix=None,
        payload='201112291234',
        check_digit=6,
        usage=RcnUsage.GEOGRAPHICAL,
        region=RcnRegion.GREAT_BRITAIN,
        price=Decimal('12.34'),
        money=Money('12.34', 'GBP')
    ),
    upc_error="Failed to parse '2011122912346' as UPC: Expected 6, 7, 8, or 12 digits, got 13.",
    sscc_error="Failed to parse '2011122912346' as SSCC: Expected 18 digits, got 13.",
    gs1_message_error="Failed to match '122912346' with GS1 AI (12) pattern
'^12(\\d{2}(?:0\\d|1[0-2])(?:[0-2]\\d|3[01]))$'."
)
```

The [`price`][biip.rcn.Rcn.price] and [`money`][biip.rcn.Rcn.money] fields
contain the same data. The difference is that while `price` is a simple
[`Decimal`][decimal.Decimal] type, `money` also carries currency information.
The `money` field is only set if the optional dependency
[`py-moneyed`](https://pypi.org/project/py-moneyed/) is installed.

## GS1 messages with AIs

Let us move away from consumer products.

The GS1 organization has specified a comprehensive system of Application
Identifiers (AI) covering most industry use cases.

It is helpful to get the terminology straight here, as we use it
throughout the Biip API:

- An _Application Identifier_ (AI) is a number with 2-4 digits that
  specifies a data field's format and use.
- An AI prefix, together with its data field, is called an _Element
  String_.
- Multiple Element Strings read from a single barcode is called a
  _Message_.

AI Element Strings can be encoded using several different barcode types,
but the linear barcode format GS1-128 is the most common.

### Serial Shipping Container Code (SSCC)

If we scan a GS1-128 barcode on a pallet, we might get the data string
`00157035381410375177`:

```python
>>> result = biip.parse("00157035381410375177")
>>> print(result.gs1_message)
GS1Message(
    value='00157035381410375177',
    element_strings=[
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='00',
                description='Serial Shipping Container Code (SSCC)',
                data_title='SSCC',
                fnc1_required=False,
                format='N2+N18'
            ),
            value='157035381410375177',
            pattern_groups=['157035381410375177'],
            sscc=Sscc(
                value='157035381410375177',
                prefix=GS1Prefix(value='570', usage='GS1 Denmark'),
                company_prefix=GS1CompanyPrefix(value='5703538'),
                extension_digit=1,
                payload='15703538141037517',
                check_digit=7
            )
        )
    ]
)
```

From the above result, we can see that the data is a Message that
contains a single Element String. The Element String has the AI `00`,
which is the code for Serial Shipping Container Code, or SSCC for short.

Biip extracts the SSCC payload and validates its check digit. The result
is an [`Sscc`][biip.sscc.Sscc] instance, with fields like
[`prefix`][biip.sscc.Sscc.prefix] and
[`extension_digit`][biip.sscc.Sscc.extension_digit].

You can extract the Element String using
[`GS1Message.get()`][biip.gs1_messages.GS1Message.get] and
[`GS1Message.filter()`][biip.gs1_messages.GS1Message.filter]:

```python
>>> element_string = result.gs1_message.get(ai="00")
>>> element_string.ai.data_title
'SSCC'
>>> element_string.sscc.prefix.usage
'GS1 Denmark'
>>> element_string.sscc.as_hri()
'1 5703538 141037517 7'
```

In case SSCCs are what you are primarily working with, the
[`Sscc`][biip.sscc.Sscc] instance is also available directly from
[`ParseResult`][biip.ParseResult]:

```python
>>> result.sscc == element_string.sscc
True
>>> print(result.sscc)
Sscc(
    value='157035381410375177',
    prefix=GS1Prefix(value='570', usage='GS1 Denmark'),
    company_prefix=GS1CompanyPrefix(value='5703538'),
    extension_digit=1,
    payload='15703538141037517',
    check_digit=7
)
```

If you need to display the barcode data in a more human readable way,
e.g. to print below a barcode, you can use
[`GS1Message.as_hri()`][biip.gs1_messages.GS1Message.as_hri]:

```python
>>> result.gs1_message.as_hri()
'(00)157035381410375177'
```

### Product IDs, expiration dates, and lot numbers

If we unpack the pallet and scan the GS1-128 barcode on a logistic unit,
containing multiple trade units, we might get the data string
`010703206980498815210526100329`:

```python
>>> result = biip.parse("010703206980498815210526100329")
```

We can have a quick look at the human-readable interpretation (HRI) to get a
feel for how the data groups into three Element Strings:

```python
>>> result.gs1_message.as_hri()
'(01)07032069804988(15)210526(10)0329'
```

And we can dig into the parsed Element Strings to get all the details:

```python hl_lines="13-20 25 32 37 42"
>>> print(result.gs1_message.element_strings)
[
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='01',
            description='Global Trade Item Number (GTIN)',
            data_title='GTIN',
            fnc1_required=False,
            format='N2+N14'
        ),
        value='07032069804988',
        pattern_groups=['07032069804988'],
        gtin=Gtin(
            value='07032069804988',
            format=GtinFormat.GTIN_13,
            prefix=GS1Prefix(value='703', usage='GS1 Norway'),
            company_prefix=GS1CompanyPrefix(value='703206'),
            payload='703206980498',
            check_digit=8
        )
    ),
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='15',
            description='Best before date (YYMMDD)',
            data_title='BEST BEFORE or BEST BY',
            fnc1_required=False,
            format='N2+N6'
        ),
        value='210526',
        pattern_groups=['210526'],
        date=datetime.date(2021, 5, 26)
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
        pattern_groups=['0329']
    )
]
```

The first Element String is the GTIN of the trade item inside the
logistic unit. As with SSCC's, this is also available directly from the
[`ParseResult`][biip.ParseResult] instance:

```python
>>> result.gtin == result.gs1_message.element_strings[0].gtin
True
>>> print(result.gtin)
Gtin(
    value='07032069804988',
    format=GtinFormat.GTIN_13,
    prefix=GS1Prefix(value='703', usage='GS1 Norway'),
    company_prefix=GS1CompanyPrefix(value='703206'),
    payload='703206980498',
    check_digit=8
)
```

The second Element String is the expiration date of the contained trade
items. To save you from interpreting the date value correctly yourself,
Biip does the job for you and exposes a
[`datetime.date`][datetime.date] instance:

```python
>>> element_string = result.gs1_message.get(data_title="BEST BY")
>>> element_string.date
datetime.date(2021, 5, 26)
```

The last Element String is the batch or lot number of the items:

```python
>>> element_string = result.gs1_message.get(ai="10")
>>> element_string.value
'0329'
```

### Variable-length fields

About a third of the specified AIs don't have a fixed length. How do we
then know where the Element Strings ends, and the next one starts?

Let's look closer at the batch/lot number in the example in the previous
section. It has the following AI defintion:

```python hl_lines="6"
GS1ApplicationIdentifier(
    ai='10',
    description='Batch or lot number',
    data_title='BATCH/LOT',
    fnc1_required=True,
    format='N2+X..20'
)
```

The batch/lot number, with AI `10`, is a variable-length field.
You can see this from the
[`format`][biip.gs1_application_identifiers.GS1ApplicationIdentifier.format],
`N2+X...20`, which indicates a two-digit AI prefix followed by a payload of up
to 20 alphanumeric characters.

In the last example, we didn't need to do anything to handle the variable-length
data field because the batch/lot number Element String was the last one in the
Message.

Let's try to reorder the expiration date and batch/lot number, so that
the batch/lot number comes in the middle of the Message:

```python
>>> result = biip.parse("010703206980498810032915210525")
>>> result.gs1_message.as_hri()
'(01)07032069804988(10)032915210525'
```

As we can see, the batch/lot number didn't know where to stop, so it
consumed the remainder of the data, including the full expiration date.

GS1-128 barcodes mark the end of variable-length Element Strings with a
_Function Code 1_ (FNC1) symbol. When the barcode scanner converts the
barcode to a string of text, it substitutes the FNC1 symbol with
something else, often with the "Group Separator" or "GS" ASCII
character. The GS ASCII character has a decimal value of 29 or
hexadecimal value of `0x1D`.

If we insert a byte with value `0x1D`, after the end of the batch/lot
number, we get the following result:

```python
>>> result = biip.parse("0107032069804988100329\x1d15210525")
>>> result.gs1_message.as_hri()
'(01)07032069804988(10)0329(15)210525'
```

Once again, we've correctly detected all three Element Strings.

### Barcode scanner configuration

To make variable-length fields work correctly, you might need to reconfigure
your barcode scanner hardware to use another separator character if:

- your barcode scanner doesn't insert the GS character, or
- some part of your scanning data pipeline cannot maintain the
  character as-is.

A reasonable choice for an alternative separator character might be the
pipe character, `|`, as this character cannot legally be a part of the
payload in Element Strings.

If we configure the barcode scanner to use an alternative separator character,
we also need to tell Biip what character to expect by passing the
`separator_chars` parameter to the [`parse()`][biip.parse] function:

```python
>>> result = biip.parse("0107032069804988100329|15210525", separator_chars=["|"])
>>> result.gs1_message.as_hri()
'(01)07032069804988(10)0329(15)210525'
```

Once again, all three Element Strings was successfully extracted.

## Deep dive

This quickstart guide covers the surface of Biip and should get you
quickly up and running.

If you need to dive deeper, all parts of Biip have extensive docstrings
with references to the relevant parts of specifications from GS1 and
ISO. As a last resource, you have the code as well as a test suite with
100% code coverage.

Happy barcode scanning!
