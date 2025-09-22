# Symbology Identifiers

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
message parsers.

/// note | Learn more
To learn more about Symbology Identifiers, see the
[`biip.symbology`](../reference/symbology.md) reference documentation.
///
