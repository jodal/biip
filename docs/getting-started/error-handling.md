# Error handling

Biip can parse several different data formats. Thus, it'll return a
result object with a mix of results and errors. In the above example, we
can see that the data is successfully parsed as a GTIN (and GS1 Message) while
parsing as an UPC or SSCC failed, and Biip returned error messages explaining
why.

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
