"""Support for Symbology Identifiers.

Symbology Identifiers is a standardized way to identify what type of barcode
symbology was used to encode the following data.

The Symbology Identifiers are a few extra characters that may be prefixed to
the scanned data by the barcode scanning hardware. The software interpreting
the barcode may use the Symbology Identifier to differentiate how to handle
the barcode, but must at the very least be able to strip and ignore the extra
characters.

Example:
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

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from biip import ParseError
from biip.gs1 import GS1Symbology

__all__ = [
    "SymbologyIdentifier",
    "Symbology",
]


class Symbology(Enum):
    """Enum of barcode symbologies that are supported by Symbology Identifers.

    References:
        ISO/IEC 15424:2008, Table 1.
    """

    #: Code 39
    CODE_39 = "A"

    #: Telepen
    TELEPEN = "B"

    #: Code 128
    CODE_128 = "C"

    #: Code One
    CODE_ONE = "D"

    #: EAN/UPC
    EAN_UPC = "E"

    #: Codabar
    CODABAR = "F"

    #: Code 93
    CODE_93 = "G"

    #: Code 11
    CODE_11 = "H"

    #: ITF (Interleaved 2 of 5)
    ITF = "I"

    #: Code 16K
    CODE_16K = "K"

    #: PDF417 and MicroPDF417
    PDF417 = "L"

    #: MSI
    MSI = "M"

    #: Anker
    ANKER = "N"

    #: Codablock
    CODABLOCK = "O"

    #: Plessey Code
    PLESSEY_CODE = "P"

    #: QR Code and QR Code 2005
    QR_CODE = "Q"

    #: Straigt 2 of 5 (with two bar start/stop codes)
    STRAIGHT_2_OF_5_WITH_2_BAR_START_STOP_CODE = "R"

    #: Straigt 2 of 5 (with three bar start/stop codes)
    STRAIGHT_2_OF_5_WITH_3_BAR_START_STOP_CODE = "S"

    #: Code 49
    CODE_49 = "T"

    #: MaxiCode
    MAXICODE = "U"

    #: Other barcode
    OTHER_BARCODE = "X"

    #: System expansion
    SYSTEM_EXPANSION = "Y"

    #: Non-barcode
    NON_BARCODE = "Z"

    #: Channel Code
    CHANNEL_CODE = "c"

    #: Data Matrix
    DATA_MATRIX = "d"

    #: RSS and EAN.UCC Composite
    RSS_EAN_UCC_COMPOSITE = "e"

    #: OCR (Optical Character Recognition)
    OCR = "o"

    #: PosiCode
    POSICODE = "p"

    #: SuperCode
    SUPERCODE = "s"

    #: Aztec Code
    AZTEC_CODE = "z"

    def __repr__(self: "Symbology") -> str:
        """Canonical string representation of format."""
        return f"Symbology.{self.name}"


@dataclass
class SymbologyIdentifier:
    """Data class containing a Symbology Identifier."""

    #: Raw unprocessed value.
    value: str

    #: The recognized symbology.
    symbology: Symbology

    #: Symbology modifiers.
    #: Refer to :attr:`gs1_symbology` or ISO/IEC 15424 for interpretation.
    modifiers: str

    #: If the Symbology Identifier is used in the GS1 system,
    #: this field is set to indicate how to interpret the following data.
    gs1_symbology: Optional[GS1Symbology] = None

    @classmethod
    def extract(cls: Type["SymbologyIdentifier"], value: str) -> "SymbologyIdentifier":
        """Extract the Symbology Identifier from the given value.

        Args:
            value: The string to extract a Symbology Identifier from.

        Returns:
            Metadata about the extracted Symbology Identifier.

        Raises:
            ParseError: If the parsing fails.o
        """
        if not value.startswith("]"):
            raise ParseError(
                f"Failed to get Symbology Identifier from {value!r}. "
                "No initial ']' flag character found."
            )

        try:
            symbology = Symbology(value[1])
        except ValueError:
            raise ParseError(
                f"Failed to get Symbology Identifier from {value!r}. "
                f"{value[1]!r} is not a recognized code character."
            )

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

    def __len__(self: "SymbologyIdentifier") -> int:
        """Get the length of the Symbology Identfier."""
        return len(self.value)

    def __str__(self: "SymbologyIdentifier") -> str:
        """Get the string representation of the Symbology Identifier."""
        return self.value
