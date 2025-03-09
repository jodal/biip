"""Enums used when parsing GTINs."""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import Optional


class GtinFormat(IntEnum):
    """Enum of GTIN formats."""

    GTIN_8 = 8
    """GTIN-8"""

    GTIN_12 = 12
    """GTIN-12"""

    GTIN_13 = 13
    """GTIN-13"""

    GTIN_14 = 14
    """GTIN-14"""

    def __str__(self) -> str:
        """Pretty string representation of format."""
        return self.name.replace("_", "-")

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"GtinFormat.{self.name}"

    @property
    def length(self) -> int:
        """Length of a GTIN of the given format."""
        return int(self)


class RcnUsage(Enum):
    """Enum of RCN usage restrictions."""

    GEOGRAPHICAL = "geo"
    """Usage of RCN restricted to geopgraphical area."""

    COMPANY = "company"
    """Usage of RCN restricted to internally in a company."""

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"RcnUsage.{self.name}"


class RcnRegion(Enum):
    """Enum of geographical regions with custom RCN rules.

    The value of the enum is the lowercase ISO 3166-1 Alpha-2 code.
    """

    DENMARK = "dk"
    """Denmark"""

    ESTONIA = "ee"
    """Estonia"""

    FINLAND = "fi"
    """Finland"""

    GERMANY = "de"
    """Germany"""

    GREAT_BRITAIN = "gb"
    """Great Britain"""

    LATVIA = "lv"
    """Latvia"""

    LITHUANIA = "lt"
    """Lithuania"""

    NORWAY = "no"
    """Norway"""

    SWEDEN = "se"
    """Sweden"""

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"RcnRegion.{self.name}"

    def get_currency_code(self) -> Optional[str]:
        """Get the ISO-4217 currency code for the region."""
        return {
            RcnRegion.DENMARK: "DKK",
            RcnRegion.GERMANY: "EUR",
            RcnRegion.GREAT_BRITAIN: "GBP",
            RcnRegion.NORWAY: "NOK",
            RcnRegion.SWEDEN: "SEK",
        }.get(self)
