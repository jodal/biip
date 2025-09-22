# Global Trade Item Number (GTIN)

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

## Use GTIN-14 in databases

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
