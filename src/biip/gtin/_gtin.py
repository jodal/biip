"""Global Trade Item Number (GTIN)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Type, Union

from biip import EncodeError, ParseError
from biip.gs1 import GS1CompanyPrefix, GS1Prefix
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

    #: The GS1 Prefix, indicating what GS1 country organization that assigned
    #: code range.
    prefix: Optional[GS1Prefix]

    #: The GS1 Company Prefix, identifying the company that issued the GTIN.
    company_prefix: Optional[GS1CompanyPrefix]

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
        cls,
        value: str,
        *,
        rcn_region: Optional[Union[RcnRegion, str]] = None,
        rcn_verify_variable_measure: bool = True,
    ) -> Gtin:
        """Parse the given value into a :class:`Gtin` object.

        Both GTIN-8, GTIN-12, GTIN-13, and GTIN-14 are supported.

        Args:
            value: The value to parse.
            rcn_region: The geographical region whose rules should be used to
                interpret Restricted Circulation Numbers (RCN).
                Needed to extract e.g. variable weight/price from GTIN.
            rcn_verify_variable_measure: Whether to verify that the variable
                measure in a RCN matches its check digit, if present. Some
                companies use the variable measure check digit for other
                purposes, requiring this check to be disabled.

        Returns:
            GTIN data structure with the successfully extracted data.
            The checksum is guaranteed to be valid if a GTIN object is returned.

        Raises:
            ParseError: If the parsing fails.
        """
        from biip.gtin import Rcn

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

        packaging_level: Optional[int] = None
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

        calculated_check_digit = numeric_check_digit(payload)
        if check_digit != calculated_check_digit:
            msg = (
                f"Invalid GTIN check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )
            raise ParseError(msg)

        gtin_type: Type[Union[Gtin, Rcn]]
        if (
            gtin_format <= GtinFormat.GTIN_13
            and prefix is not None
            and "Restricted Circulation Number" in prefix.usage
        ):
            gtin_type = Rcn
        else:
            gtin_type = Gtin

        gtin = gtin_type(
            value=value,
            format=gtin_format,
            prefix=prefix,
            company_prefix=company_prefix,
            payload=payload,
            check_digit=check_digit,
            packaging_level=packaging_level,
        )

        if isinstance(gtin, Rcn) and rcn_region is not None:
            gtin._parse_with_regional_rules(  # noqa: SLF001
                region=rcn_region,
                verify_variable_measure=rcn_verify_variable_measure,
            )

        return gtin

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
