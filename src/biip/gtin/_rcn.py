"""Restricted Circulation Numbers (RCN)."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional

from biip.gtin import Gtin

try:
    import moneyed
except ImportError:  # pragma: no cover
    moneyed = None


class RcnUsage(Enum):
    """Enum of RCN usage restrictions."""

    #: Usage of RCN restricted to geopgraphical area.
    GEOGRAPHICAL = "geo"

    #: Usage of RCN restricted to internally in a company.
    COMPANY = "company"


@dataclass
class Rcn(Gtin):
    """Restricted Circulation Number (RCN) is a subset of GTIN.

    RCNs with prefix 02 and 20-29 have the same semantics across a geographic
    region, defined by the local GS1 Member Organization.

    RCNs with prefix 40-49 have semantics that are only defined within a
    single company.
    """

    #: Where the RCN can be circulated,
    #: in a geographical area or within a company.
    usage: Optional[RcnUsage] = field(default=None, init=False)

    #: A variable weight value extracted from the barcode,
    #: if indicated by prefix.
    weight: Optional[Decimal] = field(default=None, init=False)

    #: A variable weight price extracted from the barcode,
    #: if indicated by prefix.
    price: Optional[Decimal] = field(default=None, init=False)

    #: A Money value created from the variable weight price.
    #: Only set if py-moneyed is installed and the currency is known.
    money: Optional["moneyed.Money"] = field(default=None, init=False)

    def __post_init__(self: Rcn) -> None:
        """Initialize derivated fields."""
        self._set_usage()

    def _set_usage(self: Rcn) -> None:
        if "within a geographic region" in self.prefix.usage:
            self.usage = RcnUsage.GEOGRAPHICAL
        elif "within a company" in self.prefix.usage:
            self.usage = RcnUsage.COMPANY
