"""Global Location Number (GLN).

GLNs are used to identify physical locations, digital locations, legal entities,
and organizational functions.

If you only want to parse GLNs, you can import the GLN parser directly.

    >>> from biip.gln import Gln

If parsing succeeds, it returns a `Gln` object.

    >>> gln = Gln.parse("1234567890128")
    >>> pprint(gln)
    Gln(
        value='1234567890128',
        prefix=GS1Prefix(
            value='123',
            usage='GS1 US'
        ),
        company_prefix=GS1CompanyPrefix(
            value='1234567890'
        ),
        payload='123456789012',
        check_digit=8
    )

As GLNs do not appear independently in barcodes, the GLN parser is not a part of
the top-level parser [`biip.parse()`][biip.parse]. However, if you are parsing a
barcode with GS1 element strings including a GLN, the GLN will be parsed and
validated using the [`Gln`][biip.gln.Gln] class.

    >>> import biip
    >>> gln = (
    ...     biip.parse("4101234567890128")
    ...     .gs1_message
    ...     .element_strings.get(data_title="SHIP TO")
    ...     .gln
    ... )
    >>> pprint(gln)
    Gln(
        value='1234567890128',
        prefix=GS1Prefix(
            value='123',
            usage='GS1 US'
        ),
        company_prefix=GS1CompanyPrefix(
            value='1234567890'
        ),
        payload='123456789012',
        check_digit=8
    )
"""

from __future__ import annotations

from dataclasses import dataclass

from biip import ParseConfig, ParseError
from biip.checksums import gs1_standard_check_digit
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix


@dataclass(frozen=True)
class Gln:
    """Dataclass containing a GLN."""

    value: str
    """Raw unprocessed value."""

    prefix: GS1Prefix | None
    """The [GS1 Prefix][biip.gs1_prefixes.GS1Prefix].

    Indicating what GS1 country organization that assigned code range.
    """

    company_prefix: GS1CompanyPrefix | None
    """The [GS1 Company Prefix][biip.gs1_prefixes.GS1CompanyPrefix].

    Identifying the company that issued the GLN.
    """

    payload: str
    """The actual payload.

    Including extension digit, company prefix, and item reference. Excludes the
    check digit.
    """

    check_digit: int
    """Check digit used to check if the GLN as a whole is valid."""

    @classmethod
    def parse(
        cls,
        value: str,
        *,
        config: ParseConfig | None = None,  # noqa: ARG003
    ) -> Gln:
        """Parse the given value into a [`Gln`][biip.gln.Gln] object.

        The checksum is guaranteed to be valid if a GLN object is returned.

        Args:
            value: The value to parse.
            config: Configuration options for parsing.

        Returns:
            GLN data structure with the successfully extracted data.

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

        calculated_check_digit = gs1_standard_check_digit(payload)
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
