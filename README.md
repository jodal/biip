# &#x1F4E6; Biip

_Biip interprets the data in barcodes._

[![CI](https://img.shields.io/github/actions/workflow/status/jodal/biip/ci.yml?branch=main)](https://github.com/jodal/biip/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/readthedocs/biip)](https://biip.readthedocs.io/en/latest/)
[![Coverage](https://img.shields.io/codecov/c/gh/jodal/biip)](https://codecov.io/gh/jodal/biip)
[![PyPI](https://img.shields.io/pypi/v/biip)](https://pypi.org/project/biip/)

---

Biip is a Python library for making sense of the data in barcodes.

The library can interpret the following formats:

- GTIN-8, GTIN-12, GTIN-13, and GTIN-14 numbers,
  commonly found in EAN-8, EAN-13, and ITF-14 barcodes.

- GS1 AI element strings,
  commonly found in GS1-128 barcodes.

- UPC-A and UPC-E numbers, as found in UPC-A and UPC-E barcodes.

For a quickstart guide and a complete API reference,
see the [documentation](https://biip.readthedocs.io/).

## Example

```python
>>> from rich import print
>>> import biip
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

## Project resources

- [Documentation](https://biip.readthedocs.io/)
- [Source code](https://github.com/jodal/biip)
- [Releases](https://github.com/jodal/biip/releases)
- [Issue tracker](https://github.com/jodal/biip/issues)
- [Contributors](https://github.com/jodal/biip/graphs/contributors)
- [Users](https://github.com/jodal/biip/wiki/Users)

## License

Copyright 2020-2025 Stein Magnus Jodal and contributors.
Licensed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
