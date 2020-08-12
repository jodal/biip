"""Support for Global Trade Item Number (GTIN)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from biip import EncodeError, ParseError
from biip.gs1 import GS1Prefix
from biip.gs1.checksums import numeric_check_digit


class GTINFormat(IntEnum):
    """Global Trade Item Number (GTIN) formats."""

    GTIN_8 = 8
    GTIN_12 = 12
    GTIN_13 = 13
    GTIN_14 = 14

    def __str__(self: GTINFormat) -> str:
        """Pretty string representation of format."""
        return self.name.replace("_", "-")


@dataclass
class GTIN:
    """Global Trade Item Number (GTIN)."""

    #: Raw unprocessed value.
    #:
    #: May include leading zeros.
    value: str

    #: GTIN format, either GTIN-8, GTIN-12, GTIN-13, or GTIN-14.
    #:
    #: Classification is done after stripping leading zeros.
    format: GTINFormat

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

    def as_gtin_8(self: GTIN) -> str:
        """Format as a GTIN-8."""
        return self._as_format(GTINFormat.GTIN_8)

    def as_gtin_12(self: GTIN) -> str:
        """Format as a GTIN-12."""
        return self._as_format(GTINFormat.GTIN_12)

    def as_gtin_13(self: GTIN) -> str:
        """Format as a GTIN-13."""
        return self._as_format(GTINFormat.GTIN_13)

    def as_gtin_14(self: GTIN) -> str:
        """Format as a GTIN-14."""
        return self._as_format(GTINFormat.GTIN_14)

    def _as_format(self: GTIN, format_: GTINFormat) -> str:
        if int(self.format) > int(format_):
            raise EncodeError(f"Failed encoding {self.value!r} as {format_!s}.")
        return f"{self.payload}{self.check_digit}".zfill(int(format_))


def parse(value: str) -> GTIN:
    """Attempt to parse the value as a GTIN.

    Both GTIN-8, GTIN-12, GTIN-13, and GTIN-14 are supported.

    Args:
        value: The value to parse.

    Returns:
        GTIN data structure with the successfully extracted data.

    Raises:
        ParseError: If the parsing fails.
    """
    if len(value) not in (8, 12, 13, 14):
        raise ParseError(
            f"Failed parsing {value!r} as GTIN: "
            f"Expected 8, 12, 13, or 14 characters, got {len(value)}."
        )

    if not value.isnumeric():
        raise ParseError(
            f"Failed parsing {value!r} as GTIN: Expected a numerical value."
        )

    stripped_value = _strip_leading_zeros(value)
    gtin_format = GTINFormat(len(stripped_value))
    payload = stripped_value[:-1]
    check_digit = int(stripped_value[-1])

    packaging_level: Optional[int]
    if gtin_format == GTINFormat.GTIN_14:
        packaging_level = int(stripped_value[0])
        value_without_packaging_level = stripped_value[1:]
        prefix = GS1Prefix.extract(value_without_packaging_level)
    else:
        packaging_level = None
        prefix = GS1Prefix.extract(stripped_value)

    calculated_check_digit = numeric_check_digit(payload)
    if check_digit != calculated_check_digit:
        raise ParseError(
            f"Invalid GTIN check digit for {value!r}: "
            f"Expected {calculated_check_digit!r}, got {check_digit!r}."
        )

    return GTIN(
        value=value,
        format=gtin_format,
        prefix=prefix,
        payload=payload,
        check_digit=check_digit,
        packaging_level=packaging_level,
    )


def _strip_leading_zeros(value: str) -> str:
    if len(value) in (12, 13, 14) and len(value.lstrip("0")) in (9, 10, 11, 12):
        # Keep up to three leading zeros in GTIN-12
        num_zeros_before_gtin_12 = len(value) - 12
        return value[num_zeros_before_gtin_12:]

    return value.lstrip("0")
