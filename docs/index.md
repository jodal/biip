# Introduction

## Highlights

Biip is a Python library for making sense of the data in barcodes.

The library can interpret the following formats:

- GTIN-8, GTIN-12, GTIN-13, and GTIN-14 numbers,
  commonly found in EAN-8, EAN-13, and ITF-14 barcodes.

- GS1 AI element strings,
  commonly found in GS1-128 barcodes.

- UPC-A and UPC-E numbers, as found in UPC-A and UPC-E barcodes.

## Example

```python
>>> biip.parse("]E09781492053743")
ParseResult(
    value=']E09781492053743',
    symbology_identifier=SymbologyIdentifier(
        value=']E0',
        symbology=Symbology.EAN_UPC,
        modifiers='0',
        gs1_symbology=GS1Symbology.EAN_13,
    ),
    gtin=Gtin(
        value='9781492053743',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(value='978', usage='Bookland (ISBN)'),
        company_prefix=None,
        payload='978149205374',
        check_digit=3,
        packaging_level=None,
    ),
    gtin_error=None,
    upc=None,
    upc_error=None,
    sscc=None,
    sscc_error=None,
    gs1_message=None,
    gs1_message_error=None,
)
```

## Installation

Biip has no dependencies other than Python 3.9 or newer.

Biip is available from [PyPI](https://pypi.org/project/biip/):

```sh
python3 -m pip install biip
```

Optionally, with the help of `py-moneyed`, Biip can convert amounts with
currency information to `moneyed.Money` objects.
To install Biip with `py-moneyed`, run:

```sh
python3 -m pip install "biip[money]"
```

If you're using [uv](https://docs.astral.sh/uv/), you can try out Biip in a
Python shell by running:

```sh
uvx --with biip python
```


## Features

### GS1 (multiple Element Strings with Application Identifiers)

- [x] Recognize all specified Application Identifiers.
- [x] Recognize allocating GS1 Member Organization from the GS1 Company Prefix.
- [x] Recognize the GS1 Company Prefix.
- [x] Parse fixed-length Element Strings.
- [x] Parse variable-length Element Strings, including support for configuring
      the separation character.
- [x] Parse AI `00` as SSCC.
- [x] Parse AI `01` and `02` as GTIN.
- [x] Parse AI `410`-`417` as GLN.
- [x] Parse dates/times into `datetime.date`/`datetime.datetime` values. The
      year is interpreted to be within -49/+50 years from today. Dates with day "00"
      are interpreted as the last day of the month.
- [x] Parse variable measurement fields into `Decimal` values.
- [x] Parse discount percentage into `Decimal` values.
- [x] Parse amounts into `Decimal` values. Additionally, if py-moneyed
      is installed, parse amounts with currency into `Money` values.
- [x] Encode as Human Readable Interpretation (HRI),
      e.g. with parenthesis around the AI numbers.
- [x] Parse Human Readable Interpretation (HRI) strings.
- [x] Easy lookup of parsed Element Strings by Application Identifier (AI)
      prefix and part of AI's data title.

### GLN (Global Location Number)

- [x] Parse.
- [x] Extract and validate check digit.
- [x] Extract GS1 Prefix.
- [x] Extract GS1 Company Prefix.

### GTIN (Global Trade Item Number)

- [x] Parse GTIN-8, e.g. from EAN-8 barcodes.
- [x] Parse GTIN-12, e.g. from UPC-A and UPC-E barcodes.
- [x] Parse GTIN-13, e.g. from EAN-13 barcodes.
- [x] Parse GTIN-14, e.g. from ITF-14 and GS1-128 barcodes.
- [x] Extract and validate check digit.
- [x] Extract GS1 Prefix.
- [x] Extract GS1 Company Prefix.
- [x] Extract packaging level digit from GTIN-14.
- [x] Encode GTIN-8 as GTIN-12/13/14.
- [x] Encode GTIN-12 as GTIN-13/14.
- [x] Encode GTIN-13 as GTIN-14.

### RCN (Restricted Circulation Numbers), a subset of GTINs

- [x] Classification of RCN usage to either a geographical region or a company.
- [x] Parsing of variable measurements (price/weight) into `Decimal`
      values.
- [x] Parsing of price values into `Money` values if `py-moneyed` is
      installed and the region's RCN parsing rules specifies a currency.
- [x] Denmark: Parsing of weight and price.
- [x] Estland: Parsing of weight.
- [x] Finland: Parsing of weight.
- [x] Germany: Parsing of weight, price, and count, including validation of
      measurement check digit.
- [x] Great Britain: Parsing of price, including validation of measurement check
      digit.
- [x] Latvia: Parsing of weight.
- [x] Lithuania: Parsing of weight.
- [x] Norway: Parsing of weight and price.
- [x] Sweden: Parsing of weight and price.
- [x] Encode RCN with the variable measure part zeroed out,
      to help looking up the correct trade item.

### SSCC (Serial Shipping Container Code)

- [x] Extract and validate check digit.
- [x] Extract GS1 Prefix.
- [x] Extract GS1 Company Prefix.
- [x] Extract extension digit.
- [x] Encode for human consumption, with the logical groups separated by whitespace.

### UPC (Universal Product Code)

- [x] Parse 12-digit UPC-A.
- [x] Parse 6-digit UPC-E, with implicit number system 0 and no check digit.
- [x] Parse 7-digit UPC-E, with explicit number system and no check digit.
- [x] Parse 8-digit UPC-E, with explicit number system and a check digit.
- [x] Expand UPC-E to UPC-A.
- [x] Suppress UPC-A to UPC-E, for the values where it is supported.

### Symbology Identifiers, e.g. `]EO`

- [x] Recognize all specified Symbology Identifier code characters.
- [x] Strip Symbology Identifiers before parsing the remainder.
- [x] Use Symbology Identifiers when automatically selecting what parser to use.
