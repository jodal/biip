"""Enums used when parsing GTINs."""

from enum import Enum, IntEnum
from typing import Optional


class GtinFormat(IntEnum):
    """Enum of GTIN formats."""

    #: GTIN-8
    GTIN_8 = 8

    #: GTIN-12
    GTIN_12 = 12

    #: GTIN-13
    GTIN_13 = 13

    #: GTIN-14
    GTIN_14 = 14

    def __str__(self: "GtinFormat") -> str:
        """Pretty string representation of format."""
        return self.name.replace("_", "-")

    def __repr__(self: "GtinFormat") -> str:
        """Canonical string representation of format."""
        return f"GtinFormat.{self.name}"

    @property
    def length(self: "GtinFormat") -> int:
        """Length of a GTIN of the given format."""
        return int(self)


class RcnUsage(Enum):
    """Enum of RCN usage restrictions."""

    #: Usage of RCN restricted to geopgraphical area.
    GEOGRAPHICAL = "geo"

    #: Usage of RCN restricted to internally in a company.
    COMPANY = "company"

    def __repr__(self: "RcnUsage") -> str:
        """Canonical string representation of format."""
        return f"RcnUsage.{self.name}"


class RcnRegion(Enum):
    """Enum of geographical regions with custom RCN rules."""

    #: Baltics (Estonia, Latvia, Lithuania)
    BALTICS = "baltics"

    #: Great Britain
    GREAT_BRITAIN = "gb"

    #: Norway
    NORWAY = "no"

    #: Sweden
    SWEDEN = "se"

    def __repr__(self: "RcnRegion") -> str:
        """Canonical string representation of format."""
        return f"RcnRegion.{self.name}"

    def get_currency_code(self: "RcnRegion") -> Optional[str]:
        """Get the ISO-4217 currency code for the region."""
        return {
            RcnRegion.GREAT_BRITAIN: "GBP",
            RcnRegion.NORWAY: "NOK",
            RcnRegion.SWEDEN: "SEK",
        }.get(self)
