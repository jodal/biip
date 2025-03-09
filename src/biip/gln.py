"""Global Location Number (GLN).

GLNs are used to identify physical locations, digital locations, legal entities,
and organizational functions.

If you only want to parse GLNs, you can import the GLN parser directly.

    >>> from biip.gln import Gln

If parsing succeeds, it returns a `Gln` object.

    >>> gln = Gln.parse("1234567890128")
    >>> gln
    Gln(value='1234567890128', prefix=GS1Prefix(value='123',
    usage='GS1 US'), company_prefix=GS1CompanyPrefix(value='1234567890'),
    payload='123456789012', check_digit=8)

As GLNs do not appear independently in barcodes, the GLN parser is not a part of
the top-level parser `biip.parse()`. However, if you are parsing a barcode with
GS1 element strings including a GLN, the GLN will be parsed and validated using
the `Gln` class.

    >>> import biip
    >>> biip.parse("4101234567890128").gs1_message.get(data_title="SHIP TO").gln
    Gln(value='1234567890128', prefix=GS1Prefix(value='123', usage='GS1 US'),
    company_prefix=GS1CompanyPrefix(value='1234567890'), payload='123456789012',
    check_digit=8)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from biip import ParseError
from biip.gs1 import GS1CompanyPrefix, GS1Prefix
from biip.gs1.checksums import numeric_check_digit


@dataclass
class Gln:
    """Dataclass containing a GLN."""

    value: str
    """Raw unprocessed value."""

    prefix: Optional[GS1Prefix]
    """The GS1 Prefix

    Indicating what GS1 country organization that assigned code range.
    """

    company_prefix: Optional[GS1CompanyPrefix]
    """The GS1 Company Prefix.

    Identifying the company that issued the GLN.
    """

    payload: str
    """The actual payload.

    Including extension digit, company prefix, and item reference. Excludes the
    check digit.
    """

    check_digit: int
    """Check digit used to check if the SSCC as a whole is valid."""

    @classmethod
    def parse(cls, value: str) -> Gln:
        """Parse the given value into a `Gln` object.

        Args:
            value: The value to parse.

        Returns:
            GLN data structure with the successfully extracted data.
            The checksum is guaranteed to be valid if a GLN object is returned.

        Raises:
            ParseError: If the parsing fails.
        """
        value = value.strip()

        if len(value) != 13:
            msg = (
                f"Failed to parse {value!r} as GLN: "
                f"Expected 13 digits, got {len(value)}."
            )
            raise ParseError(msg)

        if not value.isdecimal():
            msg = f"Failed to parse {value!r} as GLN: Expected a numerical value."
            raise ParseError(msg)

        prefix = GS1Prefix.extract(value)
        company_prefix = GS1CompanyPrefix.extract(value)
        payload = value[:-1]
        check_digit = int(value[-1])

        calculated_check_digit = numeric_check_digit(payload)
        if check_digit != calculated_check_digit:
            msg = (
                f"Invalid GLN check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )
            raise ParseError(msg)

        return cls(
            value=value,
            prefix=prefix,
            company_prefix=company_prefix,
            payload=payload,
            check_digit=check_digit,
        )

    def as_gln(self) -> str:
        """Format as a GLN."""
        return self.value
