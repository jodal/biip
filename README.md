# &#x1F4E6; Biip

_Biip interprets the data in barcodes._

[![Tests](https://img.shields.io/github/workflow/status/jodal/biip/Tests)](https://github.com/jodal/biip/actions?workflow=Tests)
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

## Installation

Biip requires Python 3.7 or newer.

Biip is available from [PyPI](https://pypi.org/project/biip/):

```
python3 -m pip install biip
```

Optionally, with the help of `py-moneyed`, Biip can convert amounts with
currency information to `moneyed.Money` objects.
To install Biip with `py-moneyed`, run:

```
python3 -m pip install "biip[money]"
```

## Project resources

- [Documentation](https://biip.readthedocs.io/)
- [Source code](https://github.com/jodal/biip)
- [Releases](https://github.com/jodal/biip/releases)
- [Issue tracker](https://github.com/jodal/biip/issues)
- [Contributors](https://github.com/jodal/biip/graphs/contributors)
- [Users](https://github.com/jodal/biip/wiki/Users)

## Development status

All planned features have been implemented.
Please open an issue if you have any barcode parsing related needs that are not covered.

## Features

- GS1 (multiple Element Strings with Application Identifiers)
  - Recognize all specified Application Identifiers.
  - Recognize allocating GS1 Member Organization from the GS1 Company Prefix.
  - Parse fixed-length Element Strings.
  - Parse variable-length Element Strings.
    - Support configuring the separation character.
  - Parse AI `00` as SSCC.
  - Parse AI `01` and `02` as GTIN.
  - Parse AI `410`-`417` as GLN.
  - Parse dates into `datetime.date` values.
    - Interpret the year to be within -49/+50 years from today.
    - Interpret dates with day "00" as the last day of the month.
  - Parse variable measurement fields into `Decimal` values.
  - Parse discount percentage into `Decimal` values.
  - Parse amounts into `Decimal` values.
    - Additionally, if py-moneyed is installed,
      parse amounts with currency into `Money` values.
  - Encode as Human Readable Interpretation (HRI),
    e.g. with parenthesis around the AI numbers.
  - Parse Human Readable Interpretation (HRI) strings.
  - Easy lookup of parsed Element Strings by:
    - Application Identifier (AI) prefix
    - Part of AI's data title
- GLN (Global Location Number)
  - Parse.
  - Extract and validate check digit.
  - Extract GS1 Prefix.
- GTIN (Global Trade Item Number)
  - Parse GTIN-8, e.g. from EAN-8 barcodes.
  - Parse GTIN-12, e.g. from UPC-A and UPC-E barcodes.
  - Parse GTIN-13, e.g. from EAN-13 barcodes.
  - Parse GTIN-14, e.g. from ITF-14 and GS1-128 barcodes.
  - Extract and validate check digit.
  - Extract GS1 Prefix.
  - Extract packaging level digit from GTIN-14.
  - Encode GTIN-8 as GTIN-12/13/14.
  - Encode GTIN-12 as GTIN-13/14.
  - Encode GTIN-13 as GTIN-14.
- RCN (Restricted Circulation Numbers), a subset of GTINs
  - Classification of RCN usage to either a geographical region or a company.
  - Parsing of variable measurements (price/weight) into `Decimal`
    values.
  - Parsing of price values into `Money` values if `py-moneyed` is
    installed and the region's RCN parsing rules specifies a currency.
  - Denmark: Parsing of weight and price.
  - Estland: Parsing of weight.
  - Finland: Parsing of weight.
  - Germany: Parsing of weight, price, and count, including validation of
    measurement check digit.
  - Great Britain: Parsing of price, including validation of measurement check
    digit.
  - Latvia: Parsing of weight.
  - Lithuania: Parsing of weight.
  - Norway: Parsing of weight and price.
  - Sweden: Parsing of weight and price.
  - Encode RCN with the variable measure part zeroed out,
    to help looking up the correct trade item.
- SSCC (Serial Shipping Container Code)
  - Validate check digit.
  - Encode for human consumption, with the logical groups separated by whitespace.
- UPC (Universal Product Code)
  - Parse 12-digit UPC-A.
  - Parse 6-digit UPC-E, with implicit number system 0 and no check digit.
  - Parse 7-digit UPC-E, with explicit number system and no check digit.
  - Parse 8-digit UPC-E, with explicit number system and a check digit.
  - Expand UPC-E to UPC-A.
  - Suppress UPC-A to UPC-E, for the values where it is supported.
- Symbology Identifiers, e.g. `]EO`
  - Recognize all specified Symbology Identifier code characters.
  - Strip Symbology Identifiers before parsing the remainder.
  - Use Symbology Identifiers when automatically selecting what parser to use.

## License

Biip is copyright 2020-2022 Stein Magnus Jodal and contributors.
Biip is licensed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
