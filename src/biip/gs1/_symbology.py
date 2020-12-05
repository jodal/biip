"""Symbology Identifiers relevant to the GS1 system."""

from enum import Enum
from typing import Set, Type


class GS1Symbology(Enum):
    """Enum of Symbology Identifiers used in the GS1 system.

    References:
        GS1 General Specifications, Figure 5.1.2-2.
        ISO/IEC 15424:2008.
    """

    #: EAN-13, UPC-A, or UPC-E.
    EAN_13 = "E0"

    #: Two-digit add-on symbol for EAN-13.
    EAN_TWO_DIGIT_ADD_ON = "E1"

    #: Five-digit add-on symbol for EAN-13.
    EAN_FIVE_DIGIT_ADD_ON = "E2"

    #: EAN-13, UPC-A, or UPC-E with add-on symbol.
    EAN_13_WITH_ADD_ON = "E3"

    #: EAN-8
    EAN_8 = "E4"

    #: ITF-14
    ITF_14 = "I1"

    #: GS1-128
    GS1_128 = "C1"

    #: GS1 DataBar
    GS1_DATABAR = "e0"

    #: GS1 Composite. Data packet follows an encoded symbol separator character.
    GS1_COMPOSITE_WITH_SEPARATOR_CHAR = "e1"

    #: GS1 Composite. Data packet follows an escape mechanism character.
    GS1_COMPOSITE_WITH_ESCAPE_CHAR = "e2"

    #: GS1 DataMatrix
    GS1_DATAMATRIX = "d2"

    #: GS1 QR Code
    GS1_QR_CODE = "Q3"

    #: GS1 DotCode
    GS1_DOTCODE = "J1"

    @classmethod
    def with_ai_element_strings(
        cls: Type["GS1Symbology"],
    ) -> Set["GS1Symbology"]:
        """Symbologies that may contain AI Element Strings."""
        return {
            cls.GS1_128,
            cls.GS1_DATABAR,
            cls.GS1_DATAMATRIX,
            cls.GS1_QR_CODE,
            cls.GS1_DOTCODE,
        }

    @classmethod
    def with_gtin(cls: Type["GS1Symbology"]) -> Set["GS1Symbology"]:
        """Symbologies that may contain GTINs."""
        return {cls.EAN_13, cls.EAN_13_WITH_ADD_ON, cls.EAN_8, cls.ITF_14}

    def __repr__(self: "GS1Symbology") -> str:
        """Canonical string representation of format."""
        return f"GS1Symbology.{self.name}"
