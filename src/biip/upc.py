"""Universal Product Code (UPC)."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from biip import EncodeError, ParseError
from biip.gs1.checksums import numeric_check_digit


class UpcFormat(Enum):
    """Enum of UPC formats."""

    UPC_A = "upc_a"
    UPC_E = "upc_e"


@dataclass
class Upc:
    """Data class containing an UPC."""

    #: Raw unprocessed value.
    value: str

    #: UPC format, either UPC-A or UPC-E.
    format: UpcFormat

    #: The actual payload, including number system digit, manufacturer code,
    #: and product code. Excludes the check digit.
    payload: str

    #: Number system digit.
    number_system_digit: int

    #: Check digit used to check if the UPC-A as a whole is valid.
    #:
    #: Set for UPC-A, but not set for UPC-E.
    check_digit: Optional[int] = None

    @classmethod
    def parse(cls: Type["Upc"], value: str) -> "Upc":
        """Parse the given value into a :class:`Upc` object.

        Args:
            value: The value to parse.

        Returns:
            UPC data structure with the successfully extracted data.
            The checksum is guaranteed to be valid if an UPC object is returned.

        Raises:
            ParseError: If the parsing fails.
        """
        value = value.strip()

        length = len(value)
        if length not in (6, 7, 8, 12):
            raise ParseError(
                f"Failed to parse {value!r} as UPC: "
                f"Expected 6, 7, 8, or 12 digits, got {length}."
            )

        if not value.isnumeric():
            raise ParseError(
                f"Failed to parse {value!r} as UPC: Expected a numerical value."
            )

        if length == 12:
            return cls._parse_upc_a(value)
        elif length in (6, 7, 8):
            return cls._parse_upc_e(value)

        raise Exception("Unhandled UPC length. This is a bug.")  # pragma: no cover

    @classmethod
    def _parse_upc_a(cls: Type["Upc"], value: str) -> "Upc":
        assert len(value) == 12

        payload = value[:-1]
        number_system_digit = int(value[0])
        check_digit = int(value[-1])

        calculated_check_digit = numeric_check_digit(payload)
        if check_digit != calculated_check_digit:
            raise ParseError(
                f"Invalid UPC-A check digit for {value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )

        return cls(
            value=value,
            format=UpcFormat.UPC_A,
            payload=payload,
            number_system_digit=number_system_digit,
            check_digit=check_digit,
        )

    @classmethod
    def _parse_upc_e(cls: Type["Upc"], value: str) -> "Upc":
        length = len(value)
        assert length in (6, 7, 8)

        if length == 6:
            # Implicit number system 0, no check digit.
            number_system_digit = 0
            payload = f"{number_system_digit}{value}"
            check_digit = numeric_check_digit(payload)
        elif length == 7:
            # Explicit number system, no check digit.
            number_system_digit = int(value[0])
            payload = value
            check_digit = numeric_check_digit(payload)
        elif length == 8:
            # Explicit number system and check digit.
            number_system_digit = int(value[0])
            payload = value[:-1]
            check_digit = int(value[-1])

            # TODO: Expand UPC-E to UPC-A before calculating check digit
            # calculated_check_digit = numeric_check_digit(payload)
            # if check_digit != calculated_check_digit:
            #     raise ParseError(
            #         f"Invalid UPC-E check digit for {value!r}: "
            #         f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            #     )
        else:
            raise Exception(  # pragma: no cover
                "Unhandled UPC-E length. This is a bug."
            )

        return cls(
            value=value,
            format=UpcFormat.UPC_E,
            payload=payload,
            number_system_digit=number_system_digit,
            check_digit=check_digit,
        )

    def as_upc_a(self: "Upc") -> str:
        """Format as UPC-A.

        Returns:
            A string with the UPC encoded as UPC-A.

        References:
            https://www.barcodefaq.com/barcode-properties/symbologies/upc-e/
        """
        if self.format == UpcFormat.UPC_A:
            return f"{self.payload}{self.check_digit}"

        if self.format == UpcFormat.UPC_E:
            return _upc_e_to_upc_a_expansion(f"{self.payload}{self.check_digit}")

        raise Exception(  # pragma: no cover
            "Unhandled case while formatting as UPC-E. This is a bug."
        )

    def as_upc_e(self: "Upc") -> str:
        """Format as UPC-E.

        Returns:
            A string with the UPC encoded as UPC-E, if possible.

        Raises:
            EncodeError: If encoding as UPC-E fails.

        References:
            https://www.barcodefaq.com/barcode-properties/symbologies/upc-e/
        """
        if self.format == UpcFormat.UPC_A:
            return _upc_a_to_upc_e_suppression(f"{self.payload}{self.check_digit}")

        if self.format == UpcFormat.UPC_E:
            return f"{self.payload}{self.check_digit}"

        raise Exception(  # pragma: no cover
            "Unhandled case while formatting as UPC-E. This is a bug."
        )


def _upc_e_to_upc_a_expansion(value: str) -> str:
    assert len(value) == 8
    assert value.isnumeric()

    last_digit = int(value[6])
    check_digit = int(value[7])

    if last_digit in (0, 1, 2):
        return f"{value[:3]}{last_digit}0000" f"{value[3:6]}{check_digit}"

    if last_digit == 3:
        return f"{value[:4]}00000{value[4:6]}{check_digit}"

    if last_digit == 4:
        return f"{value[:5]}00000{value[5]}{check_digit}"

    if last_digit in (5, 6, 7, 8, 9):
        return f"{value[:6]}0000{last_digit}{check_digit}"

    raise Exception(  # pragma: no cover
        "Unhandled case while expanding UPC-E to UPC-A. This is a bug."
    )


def _upc_a_to_upc_e_suppression(value: str) -> str:
    assert len(value) == 12
    assert value.isnumeric()

    check_digit = int(value[11])

    if int(value[10]) in (5, 6, 7, 8, 9) and value[6:10] == "0000" and value[5] != "0":
        # UPC-E suppression, condition A
        return f"{value[:6]}{value[10]}{check_digit}"

    if value[5:10] == "00000" and value[4] != "0":
        # UPC-E suppression, condition B
        return f"{value[:5]}{value[10]}4{check_digit}"

    if value[4:8] == "0000" and int(value[3]) in (0, 1, 2):
        # UPC-E suppression, condition C
        return f"{value[:3]}{value[8:11]}" f"{value[3]}{check_digit}"

    if value[4:9] == "00000" and int(value[3]) in range(3, 10):
        # UPC-E suppression, condition D
        return f"{value[:4]}{value[9:11]}3{check_digit}"

    raise EncodeError(f"UPC-A {value!r} cannot be represented as UPC-E.")
