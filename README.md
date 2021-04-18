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
  commonly found in EAN-8, EAN-13, UPC-A, UPC-E, and ITF-14 barcodes.

- GS1 AI element strings,
  commonly found in GS1-128 barcodes.

For a quickstart guide and a complete API reference,
see the [documentation](https://biip.readthedocs.io/).

## Installation

Biip requires Python 3.6 or newer.

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

# Project resources

- [Documentation](https://biip.readthedocs.io/)
- [Source code](https://github.com/jodal/biip)
- [Releases](https://github.com/jodal/biip/releases)
- [Issue tracker](https://github.com/jodal/biip/issues)
- [Contributors](https://github.com/jodal/biip/graphs/contributors)
- [Users](https://github.com/jodal/biip/wiki/Users)

## Development status

All planned features have been implemented.
Please open an issue if you have and barcode parsing related needs that are not covered.

## Features

- GS1 (multiple Element Strings with Application Identifiers)
  - [x] Recognize all specified Application Identifiers.
  - [x] Recognize allocating GS1 Member Organization from the GS1 Company Prefix.
  - [x] Parse fixed-length Element Strings.
  - [x] Parse variable-length Element Strings.
    - [x] Support configuring the separation character.
  - [x] Parse AI `00` as SSCC.
  - [x] Parse AI `01` and `02` as GTIN.
  - [x] Parse dates into `datetime.date` values.
    - [x] Interpret the year to be within -49/+50 years from today.
    - [x] Interpret dates with day "00" as the last day of the month.
  - [x] Parse variable measurement fields into `Decimal` values.
  - [x] Parse discount percentage into `Decimal` values.
  - [x] Parse amounts into `Decimal` values.
    - [x] Additionally, if py-moneyed is installed,
          parse amounts with currency into `Money` values.
  - [x] Encode as Human Readable Interpretation (HRI),
        e.g. with parenthesis around the AI numbers.
  - [x] Easy lookup of parsed Element Strings by:
    - [x] Application Identifier (AI) prefix
    - [x] Part of AI's data title
- GTIN (Global Trade Item Number)
  - [x] Parse GTIN-8, e.g. from EAN-8 barcodes.
  - [x] Parse GTIN-12, e.g. from UPC-A and UPC-E barcodes.
  - [x] Parse GTIN-13, e.g. from EAN-13 barcodes.
  - [x] Parse GTIN-14, e.g. from ITF-14 and GS1-128 barcodes.
  - [x] Extract and validate check digit.
  - [x] Extract GS1 Prefix.
  - [x] Extract packaging level digit from GTIN-14.
  - [x] Encode GTIN-8 as GTIN-12/13/14.
  - [x] Encode GTIN-12 as GTIN-13/14.
  - [x] Encode GTIN-13 as GTIN-14.
- RCN (Restricted Circulation Numbers), a subset of GTINs
  - [x] Classification of RCN usage to either a geographical region or a company.
  - [x] Parsing of variable measurements (price/weight) into `Decimal`
        values.
  - [x] Parsing of price values into `Money` values if `py-moneyed` is
        installed and the region's RCN parsing rules specifies a currency.
  - [x] Baltics: Parsing of weight.
  - [x] Great Britain: Parsing of price, including validation of price check digit.
  - [x] Norway: Parsing of weight and price.
  - [x] Sweden: Parsing of weight and price.
  - [x] Encode RCN with the variable measure part zeroed out,
        to help looking up the correct trade item.
- SSCC (Serial Shipping Container Code)
  - [x] Validate check digit.
  - [x] Encode for human consumption, with the logical groups separated by whitespace.
- Symbology Identifers, e.g. `]EO`
  - [x] Recognize all specified Symbology Identifier code characters.
  - [x] Strip Symbology Identifers before parsing the remainder.
  - [x] Use Symbology Identifers when automatically selecting what parser to use.

## License

Biip is copyright 2020-2021 Stein Magnus Jodal and contributors.
Biip is licensed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
