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

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum, IntEnum
from typing import Optional, Type, Union

from biip import EncodeError, ParseError
from biip.gs1 import GS1Prefix
from biip.gs1.checksums import numeric_check_digit

try:
    import moneyed
except ImportError:  # pragma: no cover
    moneyed = None


__all__ = ["Gtin", "GtinFormat", "Rcn", "RcnUsage"]


class GtinFormat(IntEnum):
    """Enum of GTIN formats."""

    #: GTIN-8
    GTIN_8 = 8

    #: GTIN-12
    GTIN_12 = 12

    #: GTIN-13
    GTIN_13 = 13

    #: GTIN-14
    GTIN_14 = 14

    def __str__(self: GtinFormat) -> str:
        """Pretty string representation of format."""
        return self.name.replace("_", "-")

    def __repr__(self: GtinFormat) -> str:
        """Canonical string representation of format."""
        return f"GtinFormat.{self.name}"

    @property
    def length(self: GtinFormat) -> int:
        """Length of a GTIN of the given format."""
        return int(self)


class RcnUsage(Enum):
    """Enum of RCN usage restrictions."""

    #: Usage of RCN restricted to geopgraphical area.
    GEOGRAPHICAL = "geo"

    #: Usage of RCN restricted to internally in a company.
    COMPANY = "company"


@dataclass
class Gtin:
    """Data class containing a GTIN."""

    #: Raw unprocessed value.
    #:
    #: May include leading zeros.
    value: str

    #: GTIN format, either GTIN-8, GTIN-12, GTIN-13, or GTIN-14.
    #:
    #: Classification is done after stripping leading zeros.
    format: GtinFormat

    #: The GS1 prefix, indicating what GS1 country organization that assigned
    #: code range.
    prefix: GS1Prefix

    #: The actual payload, including packaging level if any, company prefix,
    #: and item reference. Excludes the check digit.
    payload: str

    #: Check digit used to check if the GTIN as a whole is valid.
    check_digit: int

    #: Packaging level is the first digit in GTIN-14 codes.
    #:
    #: This digit is used for wholesale shipments, e.g. the GTIN-14 product
    #: identifier in GS1-128 barcodes, but not in the GTIN-13 barcodes used for
    #: retail products.
    packaging_level: Optional[int] = None

    @classmethod
    def parse(cls: Type[Gtin], value: str) -> Gtin:
        """Parse the given value into a :class:`Gtin` object.

        Both GTIN-8, GTIN-12, GTIN-13, and GTIN-14 are supported.

        Args:
            value: The value to parse.

        Returns:
            GTIN data structure with the successfully extracted data.
            The checksum is guaranteed to be valid if a GTIN object is returned.

        Raises:
            ParseError: If the parsing fails.
        """
        if len(value) not in (8, 12, 13, 14):
            raise ParseError(
                f"Failed parsing {value!r} as GTIN: "
                f"Expected 8, 12, 13, or 14 digits, got {len(value)}."
            )

        if not value.isnumeric():
            raise ParseError(
                f"Failed parsing {value!r} as GTIN: Expected a numerical value."
            )

        stripped_value = _strip_leading_zeros(value)
        assert len(stripped_value) in (8, 12, 13, 14)

        num_significant_digits = len(stripped_value)
        gtin_format = GtinFormat(num_significant_digits)

        payload = stripped_value[:-1]
        check_digit = int(stripped_value[-1])

        packaging_level: Optional[int] = None
        if gtin_format == GtinFormat.GTIN_14:
            packaging_level = int(stripped_value[0])
            value_without_packaging_level = stripped_value[1:]
            prefix = GS1Prefix.extract(value_without_packaging_level)
        elif gtin_format == GtinFormat.GTIN_8:
            prefix = GS1Prefix.extract(stripped_value.zfill(12))
        else:
            prefix = GS1Prefix.extract(stripped_value)

        calculated_check_digit = numeric_check_digit(payload)
        if check_digit != calculated_check_digit:
            raise ParseError(
                f"Invalid GTIN check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )

        gtin_type: Type[Union[Gtin, Rcn]]
        if "Restricted Circulation Number" in prefix.usage:
            gtin_type = Rcn
        else:
            gtin_type = Gtin

        return gtin_type(
            value=value,
            format=gtin_format,
            prefix=prefix,
            payload=payload,
            check_digit=check_digit,
            packaging_level=packaging_level,
        )

    def as_gtin_8(self: Gtin) -> str:
        """Format as a GTIN-8."""
        return self._as_format(GtinFormat.GTIN_8)

    def as_gtin_12(self: Gtin) -> str:
        """Format as a GTIN-12."""
        return self._as_format(GtinFormat.GTIN_12)

    def as_gtin_13(self: Gtin) -> str:
        """Format as a GTIN-13."""
        return self._as_format(GtinFormat.GTIN_13)

    def as_gtin_14(self: Gtin) -> str:
        """Format as a GTIN-14."""
        return self._as_format(GtinFormat.GTIN_14)

    def _as_format(self: Gtin, gtin_format: GtinFormat) -> str:
        if self.format.length > gtin_format.length:
            raise EncodeError(
                f"Failed encoding {self.value!r} as {gtin_format!s}."
            )
        return f"{self.payload}{self.check_digit}".zfill(gtin_format.length)


@dataclass
class Rcn(Gtin):
    """Restricted Circulation Number (RCN) is a subset of GTIN.

    RCNs with prefix 02 and 20-29 have the same semantics across a geographic
    region, defined by the local GS1 Member Organization.

    RCNs with prefix 40-49 have semantics that are only defined within a
    single company.
    """

    #: Where the RCN can be circulated,
    #: in a geographical area or within a company.
    usage: Optional[RcnUsage] = field(default=None, init=False)

    #: A variable weight value extracted from the barcode,
    #: if indicated by prefix.
    weight: Optional[Decimal] = field(default=None, init=False)

    #: A variable weight price extracted from the barcode,
    #: if indicated by prefix.
    price: Optional[Decimal] = field(default=None, init=False)

    #: A Money value created from the variable weight price.
    #: Only set if py-moneyed is installed and the currency is known.
    money: Optional["moneyed.Money"] = field(default=None, init=False)

    def __post_init__(self: Rcn) -> None:
        """Initialize derivated fields."""
        self._set_usage()

    def _set_usage(self: Rcn) -> None:
        if "within a geographic region" in self.prefix.usage:
            self.usage = RcnUsage.GEOGRAPHICAL
        elif "within a company" in self.prefix.usage:
            self.usage = RcnUsage.COMPANY


def _strip_leading_zeros(value: str) -> str:
    if len(value) in (12, 13, 14) and len(value.lstrip("0")) in (9, 10, 11, 12):
        # Keep up to three leading zeros in GTIN-12
        num_zeros_before_gtin_12 = len(value) - 12
        return value[num_zeros_before_gtin_12:]

    if len(value) >= 8 and len(value.lstrip("0")) <= 8:
        # Keep all leading zeros in GTIN-8
        num_zeros_before_gtin_8 = len(value) - 8
        return value[num_zeros_before_gtin_8:]

    return value.lstrip("0")
