<h1 align="center">
   &#x1F4E6;<br>
   Biip
</h1>

<p align="center">
  <em>Biip interprets the data in barcodes.</em>
</p>

<p align="center">
  <a href="https://github.com/jodal/biip/actions?workflow=Tests">
    <img src="https://github.com/jodal/biip/workflows/Tests/badge.svg" alt="Tests">
  </a>
  <a href="https://codecov.io/gh/jodal/biip">
    <img src="https://codecov.io/gh/jodal/biip/branch/master/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/biip/">
    <img src="https://img.shields.io/pypi/v/biip.svg" alt="PyPI">
  </a>
</p>

---

Biip is a Python library for making sense of the data in barcodes.

The library can interpret the following formats:

- GTIN-8, GTIN-12, GTIN-13, and GTIN-14 numbers,
  commonly found in EAN-8, EAN-13, UPC-A, UPC-E, and ITF-14 barcodes.

- GS1 AI element strings,
  commonly found in GS1-128 barcodes.

## Features

- GS1
  - [x] Parse fixed-length Element Strings
  - [x] Parse variable-length Element Strings
    - [x] Support configuring the separation character
  - Data field enrichment
    - [ ] Parse `(00)` as SSCC
    - [x] Parse `(01)` and `(02)` as GTIN
    - [x] Parse dates into `datetime` objects
      - [x] Interpret the year to be within -49/+50 years from today
      - [x] Interpret dates with "00" as the day as the last day of the month
    - [ ] Parse variable measurement fields (price/weight) into `Decimal` values
  - [x] Encode as Human Readable Interpretation (HRI), e.g. with parenthesis
        around the AI numbers
- GTIN (Global Trade Item Number)
  - [x] Parse GTIN-8, e.g. from EAN-8 barcodes
  - [x] Parse GTIN-12, e.g. from UPC-A and UPC-E barcodes
  - [x] Parse GTIN-13, e.g. from EAN-13 barcodes
  - [x] Parse GTIN-14, e.g. from ITF-14 barcodes, as well as a data field in GS1 barcodes
  - [x] Extract and validate check digit
  - [x] Extract GS1 Prefix
  - [x] Extract packaging level digit from GTIN-14
  - [ ] Parse variable measurements (price/weight) into `Decimal` values
    - The exact semantics vary from market to market, but GS1 have some global
      recommendations. Have to research if there is enough similarity to have
      one rule set or if we need to configure what market rule set to use.
    - Available rule sets include:
      - [ ] Global recommendations: GS1 General Specifications, chapter 2.1.12.2
      - [ ] UK: https://www.gs1uk.org/sites/default/files/How_to_calculate_variable_measure_items_0.pdf
      - [ ] Sweden: https://www.gs1.se/en/our-standards/Identify/variable-weight-number1/
      - [ ] Baltics: https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf
  - Encode
    - [x] GTIN-8 as GTIN-12/13/14
    - [x] GTIN-12 as GTIN-13/14
    - [x] GTIN-13 as GTIN-14
    - [ ] GTIN with variable weight part zeroed out, to help looking up the correct trade item
- SSCC
  - [ ] Validate check digit
  - [ ] Extract GS1 Company Prefix, if possible due to varying field length
  - [ ] Extract serial reference, if possible due to varying field length
- Symbol IDs, e.g. `]EO`
  - [ ] Use Symbol IDs when automatically selecting what parser to use
  - [ ] Strip Symbol IDs before parsing the remainder

## Installation

Biip is available from [PyPI](https://pypi.org/project/biip/):

```
python3 -m pip install biip
```

Biip requires Python 3.7 or newer.

## Usage

This project is still in its infancy.
However, some [documentation](https://biip.readthedocs.io/) already exists.

## License

Biip is copyright 2020 Stein Magnus Jodal and contributors.
Biip is licensed under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
