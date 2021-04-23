"""Universal Product Code (UPC)."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from biip import ParseError
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

        if not value.isnumeric():
            raise ParseError(
                f"Failed to parse {value!r} as UPC: Expected a numerical value."
            )

        length = len(value)
        if length == 12:
            return cls._parse_upc_a(value)
        elif length == 6:
            return cls._parse_upc_e(value)
        else:
            raise ParseError(
                f"Failed to parse {value!r} as UPC: "
                f"Expected 6 or 12 digits, got {length}."
            )

    @classmethod
    def _parse_upc_a(cls: Type["Upc"], value: str) -> "Upc":
        assert len(value) == 12

        payload = value[:-1]
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
            check_digit=check_digit,
        )

    @classmethod
    def _parse_upc_e(cls: Type["Upc"], value: str) -> "Upc":
        assert len(value) == 6

        # TODO: Check UPC-E parity pattern.

        return cls(
            value=value,
            format=UpcFormat.UPC_E,
            payload=value,
            check_digit=None,
        )
