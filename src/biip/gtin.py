"""Support for Global Trade Item Number (GTIN).

The `biip.gtin` module contains Biip's support for parsing GTIN formats.

A GTIN is a number that uniquely identifies a trade item.

This class can interpet the following GTIN formats:

- GTIN-8, found in EAN-8 barcodes.
- GTIN-12, found in UPC-A and UPC-E barcodes.
- GTIN-13, found in EAN-13 barcodes.
- GTIN-14, found in ITF-14 barcodes, as well as a data field in GS1 barcodes.

If you only want to parse GTINs, you can import the GTIN parser directly
instead of using [`biip.parse()`][biip.parse].

    >>> from biip.gtin import Gtin

If parsing succeeds, it returns a [`Gtin`][biip.gtin.Gtin] object.

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
        check_digit=8
    )

A GTIN can be converted to any other GTIN format, as long as the target
format is longer.

    >>> gtin.as_gtin_14()
    '07032069804988'

As all GTINs can be converted to GTIN-14 using
[`as_gtin_14()`][biip.gtin.Gtin.as_gtin_14], it is the recommended format to use
when storing or comparing GTINs. For example, when looking up a product
associated with a GTIN, the GTIN should first be expanded to a GTIN-14 before
using it to query the product catalog.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING, Any

from biip import EncodeError, ParseError
from biip._parser import ParseConfig
from biip.checksums import gs1_standard_check_digit
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix

if TYPE_CHECKING:
    from collections.abc import Iterator


__all__ = ["Gtin", "GtinFormat"]


class GtinFormat(IntEnum):
    """Enum of GTIN formats."""

    GTIN_8 = 8
    """GTIN-8"""

    GTIN_12 = 12
    """GTIN-12"""

    GTIN_13 = 13
    """GTIN-13"""

    GTIN_14 = 14
    """GTIN-14"""

    def __str__(self) -> str:
        """Pretty string representation of format."""
        return self.name.replace("_", "-")

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"GtinFormat.{self.name}"

    @property
    def length(self) -> int:
        """Length of a GTIN of the given format."""
        return int(self)


@dataclass(frozen=True)
class Gtin:
    """Data class containing a GTIN."""

    value: str
    """Raw unprocessed value.

    May include leading zeros.
    """

    format: GtinFormat
    """[GTIN format][biip.gtin.GtinFormat], either GTIN-8, GTIN-12, GTIN-13, or
    GTIN-14.

    Classification is done after stripping leading zeros.
    """

    prefix: GS1Prefix | None
    """The [GS1 Prefix][biip.gs1_prefixes.GS1Prefix].

    Indicating what GS1 country organization that assigned
    code range.
    """

    company_prefix: GS1CompanyPrefix | None
    """The [GS1 Company Prefix][biip.gs1_prefixes.GS1CompanyPrefix].

    Identifying the company that issued the GTIN.
    """

    payload: str
    """The actual payload.

    Including packaging level if any, company prefix, and item reference.
    Excludes the check digit.
    """

    check_digit: int
    """Check digit used to check if the GTIN as a whole is valid."""

    packaging_level: int | None = None
    """Packaging level is the first digit in GTIN-14 codes.

    This digit is used for wholesale shipments, e.g. the GTIN-14 product
    identifier in GS1-128 barcodes, but not in the GTIN-13 barcodes used for
    retail products.
    """

    @classmethod
    def parse(
        cls,
        value: str,
        *,
        config: ParseConfig | None = None,
    ) -> Gtin:
        """Parse the given value into a [`Gtin`][biip.gtin.Gtin] object.

        Both GTIN-8, GTIN-12, GTIN-13, and GTIN-14 are supported.

        The checksum is guaranteed to be valid if a GTIN object is returned.

        Args:
            value: The value to parse.
            config: Configuration options for parsing.

        Returns:
            GTIN data structure with the successfully extracted data.

        Raises:
            ParseError: If the parsing fails.
        """
        if config is None:
            config = ParseConfig()

        from biip.rcn import Rcn

        value = value.strip()

        if len(value) not in (8, 12, 13, 14):
            msg = (
                f"Failed to parse {value!r} as GTIN: "
                f"Expected 8, 12, 13, or 14 digits, got {len(value)}."
            )
            raise ParseError(msg)

        if not value.isdecimal():
            msg = f"Failed to parse {value!r} as GTIN: Expected a numerical value."
            raise ParseError(msg)

        stripped_value = _strip_leading_zeros(value)
        assert len(stripped_value) in (8, 12, 13, 14)

        num_significant_digits = len(stripped_value)
        gtin_format = GtinFormat(num_significant_digits)

        payload = stripped_value[:-1]
        check_digit = int(stripped_value[-1])

        packaging_level: int | None = None
        prefix_value = stripped_value
        if gtin_format == GtinFormat.GTIN_14:
            packaging_level = int(stripped_value[0])
            prefix_value = stripped_value[1:]
        elif gtin_format == GtinFormat.GTIN_12:
            # Add a zero to convert U.P.C. Company Prefix to GS1 Company Prefix
            prefix_value = stripped_value.zfill(13)
        elif gtin_format == GtinFormat.GTIN_8:
            prefix_value = stripped_value.zfill(12)

        prefix = GS1Prefix.extract(prefix_value)
        company_prefix = GS1CompanyPrefix.extract(prefix_value)

        calculated_check_digit = gs1_standard_check_digit(payload)
        if check_digit != calculated_check_digit:
            msg = (
                f"Invalid GTIN check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )
            raise ParseError(msg)

        gtin_type: type[Gtin | Rcn]
        if (
            gtin_format <= GtinFormat.GTIN_13
            and prefix is not None
            and "Restricted Circulation Number" in prefix.usage
        ):
            gtin_type = Rcn
        else:
            gtin_type = Gtin

        result = gtin_type(
            value=value,
            format=gtin_format,
            prefix=prefix,
            company_prefix=company_prefix,
            payload=payload,
            check_digit=check_digit,
            packaging_level=packaging_level,
        )

        if isinstance(result, Rcn):
            result = result._with_usage()  # noqa: SLF001
            result = result._parsed_with_regional_rules(  # noqa: SLF001
                config=config
            )

        return result

    def __rich_repr__(self) -> Iterator[tuple[str, Any] | tuple[str, Any, Any]]:  # noqa: D105
        # Skip printing fields with default values
        yield "value", self.value
        yield "format", self.format
        yield "prefix", self.prefix
        yield "company_prefix", self.company_prefix
        yield "payload", self.payload
        yield "check_digit", self.check_digit
        yield "packaging_level", self.packaging_level, None

    def as_gtin_8(self) -> str:
        """Format as a GTIN-8."""
        return self._as_format(GtinFormat.GTIN_8)

    def as_gtin_12(self) -> str:
        """Format as a GTIN-12."""
        return self._as_format(GtinFormat.GTIN_12)

    def as_gtin_13(self) -> str:
        """Format as a GTIN-13."""
        return self._as_format(GtinFormat.GTIN_13)

    def as_gtin_14(self) -> str:
        """Format as a GTIN-14."""
        return self._as_format(GtinFormat.GTIN_14)

    def _as_format(self, gtin_format: GtinFormat) -> str:
        if self.format.length > gtin_format.length:
            msg = f"Failed encoding {self.value!r} as {gtin_format!s}."
            raise EncodeError(msg)
        return f"{self.payload}{self.check_digit}".zfill(gtin_format.length)

    def without_variable_measure(self) -> Gtin:
        """Create a new GTIN where the variable measure is zeroed out.

        This method is a no-op for proper GTINs. For RCNs, see the method on the
        `Rcn` subclass.

        Returns:
            A GTIN instance with zeros in the variable measure places.

        Raises:
            EncodeError: If the rules for variable measures in the region are unknown.
        """
        return self


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
