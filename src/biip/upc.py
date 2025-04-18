"""Universal Product Code (UPC).

The `biip.upc` module contains Biip's support for parsing UPC formats.

This class can interpret the following UPC formats:

- UPC-A, 12 digits.
- UPC-E, 6 digits, with implicit number system 0 and no check digit.
- UPC-E, 7 digits, with explicit number system and no check digit.
- UPC-E, 8 digits, with explicit number system and a check digit.

If you only want to parse UPCs, you can import the UPC parser directly
instead of using [`biip.parse()`][biip.parse].

    >>> from biip.upc import Upc

If parsing succeeds, it returns a [`Upc`][biip.upc.Upc] object.

    >>> upc_a = Upc.parse("042100005264")
    >>> pprint(upc_a)
    Upc(
        value='042100005264',
        format=UpcFormat.UPC_A,
        number_system_digit=0,
        payload='04210000526',
        check_digit=4
    )

A subset of the UPC-A values can be converted to a shorter UPC-E format by
suppressing zeros using [`as_upc_e()`][biip.upc.Upc.as_upc_e].

    >>> upc_a.as_upc_e()
    '04252614'

All UPC-E values can be expanded to an UPC-A using
[`as_upc_a()`][biip.upc.Upc.as_upc_a].

    >>> upc_e = Upc.parse("04252614")
    >>> pprint(upc_e)
    Upc(
        value='04252614',
        format=UpcFormat.UPC_E,
        number_system_digit=0,
        payload='0425261',
        check_digit=4
    )
    >>> upc_e.as_upc_a()
    '042100005264'

UPC is a subset of the later GTIN standard: An UPC-A value is also a valid
GTIN-12 value.

    >>> upc_e.as_gtin_12()
    '042100005264'

The canonical format for persisting UPCs to e.g. a database is GTIN-14.

    >>> upc_e.as_gtin_14()
    '00042100005264'
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from biip import EncodeError, ParseConfig, ParseError
from biip.checksums import gs1_standard_check_digit


class UpcFormat(Enum):
    """Enum of UPC formats."""

    UPC_A = "upc_a"
    """UPC-A"""

    UPC_E = "upc_e"
    """UPC-E"""

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"UpcFormat.{self.name}"


@dataclass(frozen=True)
class Upc:
    """Data class containing an UPC."""

    value: str
    """Raw unprocessed value."""

    format: UpcFormat
    """UPC format, either UPC-A or UPC-E."""

    number_system_digit: int
    """Number system digit."""

    payload: str
    """The actual payload.

    Including number system digit, manufacturer code, and product code. Excludes
    the check digit.
    """

    check_digit: int | None = None
    """Check digit used to check if the UPC-A as a whole is valid.

    Set for UPC-A, but not set for UPC-E.
    """

    @classmethod
    def parse(
        cls,
        value: str,
        *,
        config: ParseConfig | None = None,  # noqa: ARG003
    ) -> Upc:
        """Parse the given value into a [`Upc`][biip.upc.Upc] object.

        The checksum is guaranteed to be valid if an UPC object is returned.

        Args:
            value: The value to parse.
            config: Configuration options for parsing.

        Returns:
            UPC data structure with the successfully extracted data.

        Raises:
            ParseError: If the parsing fails.
        """
        value = value.strip()

        length = len(value)
        if length not in (6, 7, 8, 12):
            msg = (
                f"Failed to parse {value!r} as UPC: "
                f"Expected 6, 7, 8, or 12 digits, got {length}."
            )
            raise ParseError(msg)

        if not value.isdecimal():
            msg = f"Failed to parse {value!r} as UPC: Expected a numerical value."
            raise ParseError(msg)

        if length == 12:
            return cls._parse_upc_a(value)

        if length in (6, 7, 8):
            return cls._parse_upc_e(value)

        msg = "Unhandled UPC length. This is a bug."  # pragma: no cover
        raise NotImplementedError(msg)  # pragma: no cover

    @classmethod
    def _parse_upc_a(cls, value: str) -> Upc:
        assert len(value) == 12

        payload = value[:-1]
        number_system_digit = int(value[0])
        check_digit = int(value[-1])

        calculated_check_digit = gs1_standard_check_digit(payload)
        if check_digit != calculated_check_digit:
            msg = (
                f"Invalid UPC-A check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )
            raise ParseError(msg)

        return cls(
            value=value,
            format=UpcFormat.UPC_A,
            payload=payload,
            number_system_digit=number_system_digit,
            check_digit=check_digit,
        )

    @classmethod
    def _parse_upc_e(cls, value: str) -> Upc:
        length = len(value)
        assert length in (6, 7, 8)

        if length == 6:
            # Implicit number system 0, no check digit.
            number_system_digit = 0
            payload = f"{number_system_digit}{value}"
            upc_a_payload = _upc_e_to_upc_a_expansion(f"{payload}0")[:-1]
            check_digit = gs1_standard_check_digit(upc_a_payload)
        elif length == 7:
            # Explicit number system, no check digit.
            number_system_digit = int(value[0])
            payload = value
            upc_a_payload = _upc_e_to_upc_a_expansion(f"{payload}0")[:-1]
            check_digit = gs1_standard_check_digit(upc_a_payload)
        elif length == 8:
            # Explicit number system and check digit.
            number_system_digit = int(value[0])
            payload = value[:-1]
            check_digit = int(value[-1])
        else:
            msg = "Unhandled UPC-E length. This is a bug."  # pragma: no cover
            raise Exception(msg)  # noqa: TRY002  # pragma: no cover

        # Control that the number system digit is correct.
        if number_system_digit not in (0, 1):
            msg = (
                f"Invalid UPC-E number system for {value!r}: "
                f"Expected 0 or 1, got {number_system_digit!r}."
            )
            raise ParseError(msg)

        # Control that check digit is correct.
        upc_a_payload = _upc_e_to_upc_a_expansion(f"{payload}{check_digit}")[:-1]
        calculated_check_digit = gs1_standard_check_digit(upc_a_payload)
        if check_digit != calculated_check_digit:
            msg = (
                f"Invalid UPC-E check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )
            raise ParseError(msg)

        return cls(
            value=value,
            format=UpcFormat.UPC_E,
            payload=payload,
            number_system_digit=number_system_digit,
            check_digit=check_digit,
        )

    def as_upc_a(self) -> str:
        """Format as UPC-A.

        Returns:
            A string with the UPC encoded as UPC-A.

        References:
            GS1 General Specifications, section 5.2.2.4.2
        """
        if self.format == UpcFormat.UPC_A:
            return f"{self.payload}{self.check_digit}"

        if self.format == UpcFormat.UPC_E:
            return _upc_e_to_upc_a_expansion(f"{self.payload}{self.check_digit}")

        msg = (  # pragma: no cover
            "Unhandled case while formatting as UPC-A. This is a bug."
        )
        raise NotImplementedError(msg)  # pragma: no cover

    def as_upc_e(self) -> str:
        """Format as UPC-E.

        Returns:
            A string with the UPC encoded as UPC-E, if possible.

        Raises:
            EncodeError: If encoding as UPC-E fails.

        References:
            GS1 General Specifications, section 5.2.2.4.1
        """
        if self.format == UpcFormat.UPC_A:
            return _upc_a_to_upc_e_suppression(f"{self.payload}{self.check_digit}")

        if self.format == UpcFormat.UPC_E:
            return f"{self.payload}{self.check_digit}"

        msg = (  # pragma: no cover
            "Unhandled case while formatting as UPC-E. This is a bug."
        )
        raise NotImplementedError(msg)  # pragma: no cover

    def as_gtin_12(self) -> str:
        """Format as GTIN-12."""
        from biip.gtin import Gtin

        return Gtin.parse(self.as_upc_a()).as_gtin_12()

    def as_gtin_13(self) -> str:
        """Format as GTIN-13."""
        from biip.gtin import Gtin

        return Gtin.parse(self.as_upc_a()).as_gtin_13()

    def as_gtin_14(self) -> str:
        """Format as GTIN-14."""
        from biip.gtin import Gtin

        return Gtin.parse(self.as_upc_a()).as_gtin_14()


def _upc_e_to_upc_a_expansion(value: str) -> str:
    assert len(value) == 8
    assert value.isdecimal()

    last_digit = int(value[6])
    check_digit = int(value[7])

    if last_digit in (0, 1, 2):
        return f"{value[:3]}{last_digit}0000{value[3:6]}{check_digit}"

    if last_digit == 3:
        return f"{value[:4]}00000{value[4:6]}{check_digit}"

    if last_digit == 4:
        return f"{value[:5]}00000{value[5]}{check_digit}"

    if last_digit in (5, 6, 7, 8, 9):
        return f"{value[:6]}0000{last_digit}{check_digit}"

    msg = (  # pragma: no cover
        "Unhandled case while expanding UPC-E to UPC-A. This is a bug."
    )
    raise Exception(msg)  # noqa: TRY002  # pragma: no cover


def _upc_a_to_upc_e_suppression(value: str) -> str:
    assert len(value) == 12
    assert value.isdecimal()

    check_digit = int(value[11])

    if int(value[10]) in (5, 6, 7, 8, 9) and value[6:10] == "0000" and value[5] != "0":
        # UPC-E suppression, condition A
        return f"{value[:6]}{value[10]}{check_digit}"

    if value[5:10] == "00000" and value[4] != "0":
        # UPC-E suppression, condition B
        return f"{value[:5]}{value[10]}4{check_digit}"

    if value[4:8] == "0000" and int(value[3]) in (0, 1, 2):
        # UPC-E suppression, condition C
        return f"{value[:3]}{value[8:11]}{value[3]}{check_digit}"

    if value[4:9] == "00000" and int(value[3]) in range(3, 10):
        # UPC-E suppression, condition D
        return f"{value[:4]}{value[9:11]}3{check_digit}"

    msg = f"UPC-A {value!r} cannot be represented as UPC-E."
    raise EncodeError(msg)
