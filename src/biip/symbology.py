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
    >>> si = SymbologyIdentifier.extract("]E05901234123457")
    >>> pprint(si)
    SymbologyIdentifier(
        value=']E0',
        iso_symbology=ISOSymbology.EAN_UPC,
        modifiers='0',
        gs1_symbology=GS1Symbology.EAN_13
    )
    >>> si = SymbologyIdentifier.extract("]I198765432109213")
    >>> pprint(si)
    SymbologyIdentifier(
        value=']I1',
        iso_symbology=ISOSymbology.ITF,
        modifiers='1',
        gs1_symbology=GS1Symbology.ITF_14
    )

References:
    ISO/IEC 15424:2008.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from biip import ParseError

__all__ = [
    "GS1Symbology",
    "ISOSymbology",
    "SymbologyIdentifier",
]


class ISOSymbology(Enum):
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
        return f"ISOSymbology.{self.name}"


class GS1Symbology(Enum):
    """Enum of Symbology Identifiers used in the GS1 system.

    References:
        - GS1 General Specifications, figure 5.1.2-2.
        - ISO/IEC 15424:2008.
    """

    EAN_13 = "E0"
    """EAN-13, UPC-A, or UPC-E."""

    EAN_TWO_DIGIT_ADD_ON = "E1"
    """Two-digit add-on symbol for EAN-13."""

    EAN_FIVE_DIGIT_ADD_ON = "E2"
    """Five-digit add-on symbol for EAN-13."""

    EAN_13_WITH_ADD_ON = "E3"
    """EAN-13, UPC-A, or UPC-E with add-on symbol."""

    EAN_8 = "E4"
    """EAN-8"""

    ITF_14 = "I1"
    """ITF-14"""

    GS1_128 = "C1"
    """GS1-128"""

    GS1_DATABAR = "e0"
    """GS1 DataBar"""

    GS1_COMPOSITE_WITH_SEPARATOR_CHAR = "e1"
    """GS1 Composite. Data packet follows an encoded symbol separator character."""

    GS1_COMPOSITE_WITH_ESCAPE_CHAR = "e2"
    """GS1 Composite. Data packet follows an escape mechanism character."""

    GS1_DATAMATRIX = "d2"
    """GS1 DataMatrix"""

    GS1_QR_CODE = "Q3"
    """GS1 QR Code"""

    GS1_DOTCODE = "J1"
    """GS1 DotCode"""

    @classmethod
    def with_ai_element_strings(cls) -> set[GS1Symbology]:
        """Symbologies that may contain AI Element Strings."""
        return {
            cls.GS1_128,
            cls.GS1_DATABAR,
            cls.GS1_DATAMATRIX,
            cls.GS1_QR_CODE,
            cls.GS1_DOTCODE,
        }

    @classmethod
    def with_gtin(cls) -> set[GS1Symbology]:
        """Symbologies that may contain GTINs."""
        return {cls.EAN_13, cls.EAN_13_WITH_ADD_ON, cls.EAN_8, cls.ITF_14}

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"GS1Symbology.{self.name}"


@dataclass
class SymbologyIdentifier:
    """Data class containing a Symbology Identifier."""

    value: str
    """Raw unprocessed value."""

    iso_symbology: ISOSymbology
    """The recognized ISO symbology."""

    modifiers: str
    """Symbology modifiers.

    Refer to [`gs1_symbology`][biip.symbology.SymbologyIdentifier.gs1_symbology]
    or ISO/IEC 15424 for interpretation.
    """

    gs1_symbology: GS1Symbology | None = None
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
            iso_symbology = ISOSymbology(value[1])
        except ValueError as exc:
            msg = (
                f"Failed to get Symbology Identifier from {value!r}. "
                f"{value[1]!r} is not a recognized code character."
            )
            raise ParseError(msg) from exc

        if iso_symbology == ISOSymbology.SYSTEM_EXPANSION:
            modifiers_length = int(value[2]) + 1
        else:
            modifiers_length = 1

        modifiers = value[2 : 2 + modifiers_length]

        value = f"]{iso_symbology.value}{modifiers}"

        gs1_symbology: GS1Symbology | None
        try:
            gs1_symbology = GS1Symbology(f"{iso_symbology.value}{modifiers}")
        except ValueError:
            gs1_symbology = None

        return cls(
            value=value,
            iso_symbology=iso_symbology,
            modifiers=modifiers,
            gs1_symbology=gs1_symbology,
        )

    def __len__(self) -> int:
        """Get the length of the Symbology Identfier."""
        return len(self.value)

    def __str__(self) -> str:
        """Get the string representation of the Symbology Identifier."""
        return self.value
