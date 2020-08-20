"""Enums used when parsing GTINs."""

from __future__ import annotations

from enum import Enum, IntEnum


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

    def __str__(self: GtinFormat) -> str:
        """Pretty string representation of format."""
        return self.name.replace("_", "-")

    def __repr__(self: GtinFormat) -> str:
        """Canonical string representation of format."""
        return f"GtinFormat.{self.name}"

    @property
    def length(self: GtinFormat) -> int:
        """Length of a GTIN of the given format."""
        return int(self)


class RcnUsage(Enum):
    """Enum of RCN usage restrictions."""

    #: Usage of RCN restricted to geopgraphical area.
    GEOGRAPHICAL = "geo"

    #: Usage of RCN restricted to internally in a company.
    COMPANY = "company"
