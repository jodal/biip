# GS1 Digital Link URIs

In an effort to make a single barcode that is useful both in the supply chain
and for consumers wanting to learn more about the product they've purchased, GS1
has developed the GS1 Digital Link URI standard.

GS1 Digital Link URIs are HTTP URIs that can contain any domain name and any
path prefix, and then encodes the element strings as path segments and query
parameters in a standardized way.

Let's assume that an imaginary manufacturer named Example Inc. wants to create a
barcode for a product with GTIN `07032069804988`. The URI should link to their
product information page. The barcode should also encode the batch number `0329`
and the expiration date `2021-05-26` for easy tracking of the items through the
supply chain. Using the GS1 Digital Link URI specification, they create the
following URI:

```
https://www.example.com/products/01/07032069804988?10=0329&15=210526
```

They put this in a GS1 QR code or a GS1 DataMatrix barcode, and print it on the
product.

When a consumer scans the barcode, they are taken to the product page. When the supply chain scans this barcode and use Biip to parse it, they get the following result:

```python
>>> result = biip.parse("https://www.example.com/products/01/07032069804988?10=0329&15=210526")
>>> print(result)
ParseResult(
    value='https://www.example.com/products/01/07032069804988?10=0329&15=210526',
    gtin=Gtin(
        value='07032069804988',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(value='703', usage='GS1 Norway'),
        company_prefix=GS1CompanyPrefix(value='703206'),
        item_reference='980498',
        payload='703206980498',
        check_digit=8
    ),
    gs1_digital_link_uri=GS1DigitalLinkURI(
        value='https://www.example.com/products/01/07032069804988?10=0329&15=210526',
        element_strings=[
            GS1ElementString(
                ai=GS1ApplicationIdentifier(
                    ai='01',
                    description='Global Trade Item Number (GTIN)',
                    data_title='GTIN',
                    separator_required=False,
                    format='N2+N14'
                ),
                value='07032069804988',
                pattern_groups=['07032069804988'],
                gtin=Gtin(
                    value='07032069804988',
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value='703', usage='GS1 Norway'),
                    company_prefix=GS1CompanyPrefix(value='703206'),
                    item_reference='980498',
                    payload='703206980498',
                    check_digit=8
                )
            ),
            GS1ElementString(
                ai=GS1ApplicationIdentifier(
                    ai='10',
                    description='Batch or lot number',
                    data_title='BATCH/LOT',
                    separator_required=True,
                    format='N2+X..20'
                ),
                value='0329',
                pattern_groups=['0329']
            ),
            GS1ElementString(
                ai=GS1ApplicationIdentifier(
                    ai='15',
                    description='Best before date (YYMMDD)',
                    data_title='BEST BEFORE or BEST BY',
                    separator_required=False,
                    format='N2+N6'
                ),
                value='210526',
                pattern_groups=['210526'],
                date=datetime.date(2021, 5, 26)
            )
        ]
    )
)
```

As you can see, Biip has extracted the GTIN, batch number and expiration date,
just like we're used to with traditional GS1 message barcodes.

You can also use Biip to convert the result to a canonical GS1 Digital Link URI:

```python
>>> result.gs1_digital_link_uri.as_canonical_uri()
'https://id.gs1.org/01/07032069804988/10/0329?15=210526'
```

Or to convert it to a GS1 message and print the equivalent HRI representation:

```python
>>> message = result.gs1_digital_link_uri.as_gs1_message()
>>> message.as_hri()
'(01)07032069804988(10)0329(15)210526'
```

If you have an existing GS1 message barcode and want to convert it to a GS1
Digital Link URI, Biip can also be helpful:

```python
>>> dl_uri = message.as_gs1_digital_link_uri()
>>> dl_uri.as_uri(
...    domain="another.example.net",
...    prefix="database",
... )
'https://another.example.net/database/01/07032069804988/10/0329?15=210526'
```

/// note | Learn more
To learn more about GS1 messages, see the
[`biip.gs1_digital_link_uris`](../reference/gs1_digital_link_uris.md)
reference documentation.
///
