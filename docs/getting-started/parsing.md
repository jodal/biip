# Parsing barcode data

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
                    separator_required=True,
                    format='N3+X..27'
                ),
                value='069804988',
                pattern_groups=['069', '804988']
            )
        ]
    )
)
```

/// note | Learn more
To learn more about Biip's high-level API, see the
[`biip`](../reference/biip.md) reference documentation.
///
