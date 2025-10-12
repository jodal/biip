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
>>> print(biip.parse("]E05710858000781"))
ParseResult(
    value=']E05710858000781',
    symbology_identifier=SymbologyIdentifier(
        value=']E0',
        iso_symbology=ISOSymbology.EAN_UPC,
        modifiers='0',
        gs1_symbology=GS1Symbology.EAN_13
    ),
    gtin=Gtin(
        value='5710858000781',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(value='571', usage='GS1 Denmark'),
        company_prefix=GS1CompanyPrefix(value='5710858'),
        item_reference='00078',
        payload='571085800078',
        check_digit=1
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

With the [existing features](features.md), Biip supports all of the above use
cases, and are considered to be mostly feature complete. That said, we're always
open to add support for more countries in the RCN parser given that
documentation of the format is available.

Please [open an issue](https://github.com/jodal/biip/issues) if you have any
barcode parsing related needs that are not covered by Biip.
