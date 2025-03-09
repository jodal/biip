"""Support for Symbology Identifiers.

Symbology Identifiers is a standardized way to identify what type of barcode
symbology was used to encode the following data.

The Symbology Identifiers are a few extra characters that may be prefixed to
the scanned data by the barcode scanning hardware. The software interpreting
the barcode may use the Symbology Identifier to differentiate how to handle
the barcode, but must at the very least be able to strip and ignore the extra
characters.

Examples:
    >>> from biip.symbology import SymbologyIdentifier
    >>> SymbologyIdentifier.extract("]E05901234123457")
    SymbologyIdentifier(value=']E0', symbology=Symbology.EAN_UPC,
    modifiers='0', gs1_symbology=GS1Symbology.EAN_13)
    >>> SymbologyIdentifier.extract("]I198765432109213")
    SymbologyIdentifier(value=']I1', symbology=Symbology.ITF,
    modifiers='1', gs1_symbology=GS1Symbology.ITF_14)

References:
    ISO/IEC 15424:2008.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from biip import ParseError
from biip.gs1 import GS1Symbology

__all__ = [
    "Symbology",
    "SymbologyIdentifier",
]


class Symbology(Enum):
    """Enum of barcode symbologies that are supported by Symbology Identifers.

    References:
        ISO/IEC 15424:2008, table 1.
    """

    CODE_39 = "A"
    """Code 39"""

    TELEPEN = "B"
    """Telepen"""

    CODE_128 = "C"
    """Code 128"""

    CODE_ONE = "D"
    """Code One"""

    EAN_UPC = "E"
    """EAN/UPC"""

    CODABAR = "F"
    """Codabar"""

    CODE_93 = "G"
    """Code 93"""

    CODE_11 = "H"
    """Code 11"""

    ITF = "I"
    """ITF (Interleaved 2 of 5)"""

    CODE_16K = "K"
    """Code 16K"""

    PDF417 = "L"
    """PDF417 and MicroPDF417"""

    MSI = "M"
    """MSI"""

    ANKER = "N"
    """Anker"""

    CODABLOCK = "O"
    """Codablock"""

    PLESSEY_CODE = "P"
    """Plessey Code"""

    QR_CODE = "Q"
    """QR Code and QR Code 2005"""

    STRAIGHT_2_OF_5_WITH_2_BAR_START_STOP_CODE = "R"
    """Straigt 2 of 5 (with two bar start/stop codes)"""

    STRAIGHT_2_OF_5_WITH_3_BAR_START_STOP_CODE = "S"
    """Straigt 2 of 5 (with three bar start/stop codes)"""

    CODE_49 = "T"
    """Code 49"""

    MAXICODE = "U"
    """MaxiCode"""

    OTHER_BARCODE = "X"
    """Other barcode"""

    SYSTEM_EXPANSION = "Y"
    """System expansion"""

    NON_BARCODE = "Z"
    """Non-barcode"""

    CHANNEL_CODE = "c"
    """Channel Code"""

    DATA_MATRIX = "d"
    """Data Matrix"""

    RSS_EAN_UCC_COMPOSITE = "e"
    """RSS and EAN.UCC Composite"""

    OCR = "o"
    """OCR (Optical Character Recognition)"""

    POSICODE = "p"
    """PosiCode"""

    SUPERCODE = "s"
    """SuperCode"""

    AZTEC_CODE = "z"
    """Aztec Code"""

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"Symbology.{self.name}"


@dataclass
class SymbologyIdentifier:
    """Data class containing a Symbology Identifier."""

    value: str
    """Raw unprocessed value."""

    symbology: Symbology
    """The recognized symbology."""

    modifiers: str
    """Symbology modifiers.

    Refer to `gs1_symbology` or ISO/IEC 15424 for interpretation.
    """

    gs1_symbology: Optional[GS1Symbology] = None
    """If the Symbology Identifier is used in the GS1 system,
    this field is set to indicate how to interpret the following data.
    """

    @classmethod
    def extract(cls, value: str) -> SymbologyIdentifier:
        """Extract the Symbology Identifier from the given value.

        Args:
            value: The string to extract a Symbology Identifier from.

        Returns:
            Metadata about the extracted Symbology Identifier.

        Raises:
            ParseError: If the parsing fails.
        """
        if not value.startswith("]"):
            msg = (
                f"Failed to get Symbology Identifier from {value!r}. "
                "No initial ']' flag character found."
            )
            raise ParseError(msg)

        try:
            symbology = Symbology(value[1])
        except ValueError as exc:
            msg = (
                f"Failed to get Symbology Identifier from {value!r}. "
                f"{value[1]!r} is not a recognized code character."
            )
            raise ParseError(msg) from exc

        if symbology == Symbology.SYSTEM_EXPANSION:
            modifiers_length = int(value[2]) + 1
        else:
            modifiers_length = 1

        modifiers = value[2 : 2 + modifiers_length]

        value = f"]{symbology.value}{modifiers}"

        gs1_symbology: Optional[GS1Symbology]
        try:
            gs1_symbology = GS1Symbology(f"{symbology.value}{modifiers}")
        except ValueError:
            gs1_symbology = None

        return cls(
            value=value,
            symbology=symbology,
            modifiers=modifiers,
            gs1_symbology=gs1_symbology,
        )

    def __len__(self) -> int:
        """Get the length of the Symbology Identfier."""
        return len(self.value)

    def __str__(self) -> str:
        """Get the string representation of the Symbology Identifier."""
        return self.value
