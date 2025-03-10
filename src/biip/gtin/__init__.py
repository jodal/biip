"""Support for Global Trade Item Number (GTIN).

The `biip.gtin` module contains Biip's support for parsing GTIN formats.

A GTIN is a number that uniquely identifies a trade item.

This class can interpet the following GTIN formats:

- GTIN-8, found in EAN-8 barcodes.
- GTIN-12, found in UPC-A and UPC-E barcodes.
- GTIN-13, found in EAN-13 barcodes.
- GTIN-14, found in ITF-14 barcodes, as well as a data field in GS1 barcodes.

If you only want to parse GTINs, you can import the GTIN parser directly
instead of using `biip.parse()`.

    >>> from biip.gtin import Gtin

If parsing succeeds, it returns a `Gtin` object.

    >>> gtin = Gtin.parse("7032069804988")
    >>> pprint(gtin)
    Gtin(
        value='7032069804988',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(
            value='703',
            usage='GS1 Norway'
        ),
        company_prefix=GS1CompanyPrefix(
            value='703206'
        ),
        payload='703206980498',
        check_digit=8,
        packaging_level=None
    )

A GTIN can be converted to any other GTIN format, as long as the target
format is longer.

    >>> gtin.as_gtin_14()
    '07032069804988'

As all GTINs can be converted to GTIN-14, it is the recommended format to use
when storing or comparing GTINs. For example, when looking up a product
associated with a GTIN, the GTIN should first be expanded to a GTIN-14 before
using it to query the product catalog.
"""

from biip.gtin._enums import GtinFormat, RcnRegion, RcnUsage
from biip.gtin._gtin import Gtin
from biip.gtin._rcn import Rcn

__all__ = ["Gtin", "GtinFormat", "Rcn", "RcnRegion", "RcnUsage"]
