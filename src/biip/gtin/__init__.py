"""Support for Global Trade Item Number (GTIN).

The :mod:`biip.gtin` module contains biip's support for parsing GTIN formats.

A GTIN is a number that uniquely identifies a trade item.

This class can interpet the following GTIN formats:

- GTIN-8, found in EAN-8 barcodes.
- GTIN-12, found in UPC-A and UPC-E barcodes.
- GTIN-13, found in EAN-13 barcodes.
- GTIN-14, found in ITF-14 barcodes, as well as a data field in GS1 barcodes.

A GTIN can be converted to any other GTIN format, as long as the target
format is longer.

Example:
    >>> from biip.gtin import Gtin
    >>> gtin = Gtin.parse("5901234123457")
    >>> gtin
    Gtin(value='5901234123457', format=GtinFormat.GTIN_13,
    prefix=GS1Prefix(value='590', usage='GS1 Poland'),
    payload='590123412345', check_digit=7, packaging_level=None)
    >>> gtin.as_gtin_14()
    '05901234123457'
"""

from biip.gtin._enums import GtinFormat, RcnRegion, RcnUsage
from biip.gtin._gtin import Gtin
from biip.gtin._rcn import Rcn

__all__ = ["Gtin", "GtinFormat", "Rcn", "RcnUsage", "RcnRegion"]
