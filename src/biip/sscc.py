"""Serial Shipping Container Code (SSCC).

SSCCs are used to identify logistic units, e.g. a pallet shipped between two
parties.

If you only want to parse SSCCs, you can import the SSCC parser directly
instead of using :func:`biip.parse`.

    >>> from biip.sscc import Sscc

If parsing succeeds, it returns a :class:`Sscc` object.

    >>> sscc = Sscc.parse("157035381410375177")
    >>> sscc
    Sscc(value='157035381410375177', prefix=GS1Prefix(value='570', usage='GS1
    Denmark'), company_prefix=GS1CompanyPrefix(value='5703538'),
    extension_digit=1, payload='15703538141037517', check_digit=7)

Biip can format the SSCC in HRI format for printing on a label.

    >>> sscc.as_hri()
    '1 5703538 141037517 7'

If the detected GS1 Company Prefix length is wrong, it can be overridden:

    >>> sscc.as_hri(company_prefix_length=9)
    '1 570353814 1037517 7'
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from biip import ParseError
from biip.gs1 import GS1CompanyPrefix, GS1Prefix
from biip.gs1.checksums import numeric_check_digit


@dataclass
class Sscc:
    """Data class containing an SSCC."""

    #: Raw unprocessed value.
    value: str

    #: The GS1 Prefix, indicating what GS1 country organization that assigned
    #: code range.
    prefix: Optional[GS1Prefix]

    #: The GS1 Company Prefix, identifying the company that issued the SSCC.
    company_prefix: Optional[GS1CompanyPrefix]

    #: Extension digit used to increase the capacity of the serial reference.
    extension_digit: int

    #: The actual payload, including extension digit, company prefix, and item
    #: reference. Excludes the check digit.
    payload: str

    #: Check digit used to check if the SSCC as a whole is valid.
    check_digit: int

    @classmethod
    def parse(cls, value: str) -> Sscc:
        """Parse the given value into a :class:`Sscc` object.

        Args:
            value: The value to parse.

        Returns:
            SSCC data structure with the successfully extracted data.
            The checksum is guaranteed to be valid if an SSCC object is returned.

        Raises:
            ParseError: If the parsing fails.
        """
        value = value.strip()

        if len(value) != 18:
            msg = (
                f"Failed to parse {value!r} as SSCC: "
                f"Expected 18 digits, got {len(value)}."
            )
            raise ParseError(msg)

        if not value.isdecimal():
            msg = f"Failed to parse {value!r} as SSCC: Expected a numerical value."
            raise ParseError(msg)

        value_without_extension_digit = value[1:]
        prefix = GS1Prefix.extract(value_without_extension_digit)
        company_prefix = GS1CompanyPrefix.extract(value_without_extension_digit)
        extension_digit = int(value[0])
        payload = value[:-1]
        check_digit = int(value[-1])

        calculated_check_digit = numeric_check_digit(payload)
        if check_digit != calculated_check_digit:
            msg = (
                f"Invalid SSCC check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )
            raise ParseError(msg)

        return cls(
            value=value,
            prefix=prefix,
            company_prefix=company_prefix,
            extension_digit=extension_digit,
            payload=payload,
            check_digit=check_digit,
        )

    def as_hri(self, *, company_prefix_length: Optional[int] = None) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        The GS1 Company Prefix length will be detected and used to render the
        Company Prefix and the Serial Reference as two separate groups. If the
        GS1 Company Prefix length cannot be found, the Company Prefix and the
        Serial Reference are rendered as a single group.

        Args:
            company_prefix_length: Override the detected GS1 Company Prefix
                length. 7-10 characters. If not specified, the GS1 Company
                Prefix is automatically detected.

        Raises:
            ValueError: If an illegal company prefix length is given.

        Returns:
            A human-readable string where the logic parts are separated by whitespace.
        """
        value = self.payload[1:]  # Strip extension digit

        if company_prefix_length is not None:
            # Using override of GS1 Company Prefix length
            if not (7 <= company_prefix_length <= 10):
                msg = (
                    "Expected company prefix length between 7 and 10, "
                    f"got {company_prefix_length!r}."
                )
                raise ValueError(msg)
        elif self.company_prefix is not None:
            # Using auto-detected GS1 Company Prefix length
            company_prefix_length = len(self.company_prefix.value)

        if company_prefix_length is None:
            return f"{self.extension_digit} {value} {self.check_digit}"

        company_prefix = value[:company_prefix_length]
        serial = value[company_prefix_length:]
        return f"{self.extension_digit} {company_prefix} {serial} {self.check_digit}"
