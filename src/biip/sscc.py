"""Serial Shipping Container Code (SSCC).

SSCCs are used to identify logistic units, e.g. a pallet shipped between two
parties.

Example:
    >>> from biip.sscc import Sscc
    >>> sscc = Sscc.parse("376130321109103420")
    >>> sscc
    Sscc(value='376130321109103420', prefix=GS1Prefix(value='761',
    usage='GS1 Schweiz, Suisse, Svizzera'), extension_digit=3,
    payload='37613032110910342', check_digit=0)
    >>> sscc.as_hri()
    '3 761 3032110910342 0'
    >>> sscc.as_hri(company_prefix_length=8)
    '3 761 30321 10910342 0'
"""

from dataclasses import dataclass
from typing import Optional, Type

from biip import ParseError
from biip.gs1 import GS1Prefix
from biip.gs1.checksums import numeric_check_digit


@dataclass
class Sscc:
    """Data class containing an SSCC."""

    #: Raw unprocessed value.
    value: str

    #: The GS1 prefix, indicating what GS1 country organization that assigned
    #: code range.
    prefix: GS1Prefix

    #: Extension digit used to increase the capacity of the serial reference.
    extension_digit: int

    #: The actual payload, including extension digit, company prefix, and item
    #: reference. Excludes the check digit.
    payload: str

    #: Check digit used to check if the SSCC as a whole is valid.
    check_digit: int

    @classmethod
    def parse(cls: Type["Sscc"], value: str) -> "Sscc":
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
            raise ParseError(
                f"Failed to parse {value!r} as SSCC: "
                f"Expected 18 digits, got {len(value)}."
            )

        if not value.isnumeric():
            raise ParseError(
                f"Failed to parse {value!r} as SSCC: Expected a numerical value."
            )

        value_without_extension_digit = value[1:]
        prefix = GS1Prefix.extract(value_without_extension_digit)
        extension_digit = int(value[0])
        payload = value[:-1]
        check_digit = int(value[-1])

        calculated_check_digit = numeric_check_digit(payload)
        if check_digit != calculated_check_digit:
            raise ParseError(
                f"Invalid SSCC check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )

        return cls(
            value=value,
            prefix=prefix,
            extension_digit=extension_digit,
            payload=payload,
            check_digit=check_digit,
        )

    def as_hri(self: "Sscc", *, company_prefix_length: Optional[int] = None) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        Args:
            company_prefix_length: Length of the assigned GS1 Company prefix.
                7-10 characters. If not specified, the GS1 Company Prefix and
                the Serial Reference are rendered as a single group.

        Raises:
            ValueError: If an illegal company prefix length is used.

        Returns:
            A human-readable string where the logic parts are separated by whitespace.
        """
        value = self.payload[1:]  # Strip extension digit
        gs1_prefix = self.prefix.value

        if company_prefix_length is None:
            data = value[len(gs1_prefix) :]
            return f"{self.extension_digit} {gs1_prefix} {data} {self.check_digit}"

        if not (7 <= company_prefix_length <= 10):
            raise ValueError(
                "Expected company prefix length between 7 and 10, "
                f"got {company_prefix_length!r}."
            )

        company_prefix = value[len(gs1_prefix) : company_prefix_length]
        serial_reference = value[company_prefix_length:]
        return (
            f"{self.extension_digit} {gs1_prefix} {company_prefix} "
            f"{serial_reference} {self.check_digit}"
        )
