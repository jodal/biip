"""Restricted Circulation Numbers (RCN)."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from biip.gtin import Gtin, RcnRegion, RcnUsage

try:
    import moneyed
except ImportError:  # pragma: no cover
    moneyed = None


@dataclass
class Rcn(Gtin):
    """Restricted Circulation Number (RCN) is a subset of GTIN.

    RCNs with prefix 02 and 20-29 have the same semantics across a geographic
    region, defined by the local GS1 Member Organization.

    RCNs with prefix 40-49 have semantics that are only defined within a
    single company.

    Use :meth:`biip.gtin.Gtin.parse` to parse potential RCNs. This subclass
    is returned if the GS1 Prefix signifies that the value is a RCN.
    """

    #: Where the RCN can be circulated,
    #: in a geographical region or within a company.
    usage: Optional[RcnUsage] = field(default=None, init=False)

    #: The geographical region whose rules are used to interpret the contents
    #: of  the RCN.
    region: Optional[RcnRegion] = field(default=None, init=False)

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
        if "within a company" in self.prefix.usage:
            self.usage = RcnUsage.COMPANY

    def _parse_with_regional_rules(self: Rcn, region: RcnRegion) -> None:
        if self.usage == RcnUsage.COMPANY:
            return

        self.region = region
