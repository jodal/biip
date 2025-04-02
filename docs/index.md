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

## Installation

Biip has no dependencies other than Python 3.10 or newer.

Biip can be installed from [PyPI](https://pypi.org/project/biip/):

```sh
python3 -m pip install biip
```

### Parsing money amounts

Optionally, with the help of
[`py-moneyed`](https://pypi.org/project/py-moneyed/), Biip can convert amounts
with currency information to `moneyed.Money` objects. To install Biip with
`py-moneyed`, run:

```sh
python3 -m pip install "biip[money]"
```

### Try it out

If you're using [uv](https://docs.astral.sh/uv/), you can try out Biip in a
Python shell without installing anything by running:

```sh
uvx --with biip python
```

Once the Python shell is open, import and use Biip:

```python
>>> import biip
>>> biip.parse("your-barcode-data")
```

## Development status

Biip was developed to cover all the barcode parsing needs throughout the
operations of the online grocery store [oda.com](https://oda.com), including
registering incoming pallets, restocking shelves, picking items, and tracking
orders on the way to the customers.

With the features described below, Biip supports all of the above use cases, and
are considered to be mostly feature complete. That said, we're always open to
add support for more countries in the RCN parser given that documentation of the
format is available.

Please [open an issue](https://github.com/jodal/biip/issues) if you have any
barcode parsing related needs that are not covered by Biip.

## Features

### GS1 messages

GS1 messages can encode information about products, shipments, and other
business entities. They are used in several different barcode symbologies,
including
[GS1-128](https://en.wikipedia.org/wiki/Code_128),
[GS1 DataBar](https://en.wikipedia.org/wiki/GS1_DataBar_Coupon),
[GS1 DataMatrix](https://en.wikipedia.org/wiki/Data_Matrix), and
[GS1 QR Code](https://en.wikipedia.org/wiki/QR_code).

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
- [x] Encode as GS1 Web URIs.

### GS1 Web URIs

GS1 Web URIs are used to encode the same information as GS1 messages, but as the
path and query parameters of an URL. The URL can point to any domain. This means
that barcodes containing GS1 Web URIs can be used both in the supply chain and
for consumers to look up product information. GS1 Web URIs are used in the
[GS1 DataMatrix](https://en.wikipedia.org/wiki/Data_Matrix) and
[GS1 QR Code](https://en.wikipedia.org/wiki/QR_code)
barcode symbologies.

- [x] Everything supported for GS1 messages are also supported for GS1 Web URIs.
- [x] Parse GS1 Web URIs, both canonical and non-canonical URIs.
- [x] Encode GS1 Web URIs, both canonical and with custom domains, path
      prefixes, and with short names instead of AIs for the fields encoded in the path.
- [x] Encode as GS1 messages.

### GLN (Global Location Number)

[GLNs](https://en.wikipedia.org/wiki/Global_Location_Number) are used to
identify locations, such as warehouses and stores.

- [x] Parse.
- [x] Extract and validate check digit.
- [x] Extract GS1 Prefix.
- [x] Extract GS1 Company Prefix.

### GTIN (Global Trade Item Number)

[GTINs](https://en.wikipedia.org/wiki/Global_Trade_Item_Number) are used to
identify trade items, such as products or services.

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

RCNs are a subset of GTINs that may include additional information about the
trade item. The rules for parsing geographical RCNs vary from country to
country. The rules for parsing company RCNs vary from company to company, and
are thus not standardized.

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

[SSCCs](https://en.wikipedia.org/wiki/Serial_shipping_container_code) are used
to uniquely identify a shipping container.

- [x] Extract and validate check digit.
- [x] Extract GS1 Prefix.
- [x] Extract GS1 Company Prefix.
- [x] Extract extension digit.
- [x] Encode for human consumption, with the logical groups separated by whitespace.

### UPC (Universal Product Code)

[UPCs](https://en.wikipedia.org/wiki/Universal_Product_Code) are used to
uniquely identify a product. They are commonly used in American products with
UPC barcodes.

- [x] Parse 12-digit UPC-A.
- [x] Parse 6-digit UPC-E, with implicit number system 0 and no check digit.
- [x] Parse 7-digit UPC-E, with explicit number system and no check digit.
- [x] Parse 8-digit UPC-E, with explicit number system and a check digit.
- [x] Expand UPC-E to UPC-A.
- [x] Suppress UPC-A to UPC-E, for the values where it is supported.

### Symbology Identifiers, e.g. `]EO`

Symbology Identifiers are used by barcode scanners to specify the symbology of a
the scanned barcode, so that barcode data parsers like Biip can automatically
select the correct parser.

- [x] Recognize all specified Symbology Identifier code characters.
- [x] Strip Symbology Identifiers before parsing the remainder.
- [x] Use Symbology Identifiers when automatically selecting what parser to use.
