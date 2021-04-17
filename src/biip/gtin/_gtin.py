"""Global Trade Item Number (GTIN)."""

from dataclasses import dataclass
from typing import Optional, Type, Union

from biip import EncodeError, ParseError
from biip.gs1 import GS1Prefix
from biip.gs1.checksums import numeric_check_digit
from biip.gtin import GtinFormat, RcnRegion


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
    def parse(
        cls: Type["Gtin"], value: str, *, rcn_region: Optional[RcnRegion] = None
    ) -> "Gtin":
        """Parse the given value into a :class:`Gtin` object.

        Both GTIN-8, GTIN-12, GTIN-13, and GTIN-14 are supported.

        Args:
            value: The value to parse.
            rcn_region: The geographical region whose rules should be used to
                interpret Restricted Circulation Numbers (RCN).
                Needed to extract e.g. variable weight/price from GTIN.

        Returns:
            GTIN data structure with the successfully extracted data.
            The checksum is guaranteed to be valid if a GTIN object is returned.

        Raises:
            ParseError: If the parsing fails.
        """
        from biip.gtin import Rcn

        value = value.strip()

        if len(value) not in (8, 12, 13, 14):
            raise ParseError(
                f"Failed to parse {value!r} as GTIN: "
                f"Expected 8, 12, 13, or 14 digits, got {len(value)}."
            )

        if not value.isnumeric():
            raise ParseError(
                f"Failed to parse {value!r} as GTIN: Expected a numerical value."
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
        elif gtin_format == GtinFormat.GTIN_12:
            # Add a zero to convert U.P.C. Company Prefix to GS1 Company Prefix
            prefix = GS1Prefix.extract(stripped_value.zfill(13))
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

        gtin = gtin_type(
            value=value,
            format=gtin_format,
            prefix=prefix,
            payload=payload,
            check_digit=check_digit,
            packaging_level=packaging_level,
        )

        if isinstance(gtin, Rcn) and rcn_region is not None:
            gtin._parse_with_regional_rules(rcn_region)

        return gtin

    def as_gtin_8(self: "Gtin") -> str:
        """Format as a GTIN-8."""
        return self._as_format(GtinFormat.GTIN_8)

    def as_gtin_12(self: "Gtin") -> str:
        """Format as a GTIN-12."""
        return self._as_format(GtinFormat.GTIN_12)

    def as_gtin_13(self: "Gtin") -> str:
        """Format as a GTIN-13."""
        return self._as_format(GtinFormat.GTIN_13)

    def as_gtin_14(self: "Gtin") -> str:
        """Format as a GTIN-14."""
        return self._as_format(GtinFormat.GTIN_14)

    def _as_format(self: "Gtin", gtin_format: GtinFormat) -> str:
        if self.format.length > gtin_format.length:
            raise EncodeError(f"Failed encoding {self.value!r} as {gtin_format!s}.")
        return f"{self.payload}{self.check_digit}".zfill(gtin_format.length)


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
