"""Enums used when parsing GTINs."""

from __future__ import annotations

import warnings
from enum import Enum, IntEnum
from typing import Optional, Union


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

    #: Usage of RCN restricted to geopgraphical area.
    GEOGRAPHICAL = "geo"

    #: Usage of RCN restricted to internally in a company.
    COMPANY = "company"

    def __repr__(self) -> str:
        """Canonical string representation of format."""
        return f"RcnUsage.{self.name}"


class RcnRegion(Enum):
    """Enum of geographical regions with custom RCN rules.

    The value of the enum is the lowercase ISO 3166-1 Alpha-2 code.
    """

    #: Denmark
    DENMARK = "dk"

    #: Estonia
    ESTONIA = "ee"

    #: Finland
    FINLAND = "fi"

    #: Germany
    GERMANY = "de"

    #: Great Britain
    GREAT_BRITAIN = "gb"

    #: Latvia
    LATVIA = "lv"

    #: Lithuania
    LITHUANIA = "lt"

    #: Norway
    NORWAY = "no"

    #: Sweden
    SWEDEN = "se"

    @classmethod
    def from_iso_3166_1_numeric_code(cls, code: Union[int, str]) -> Optional[RcnRegion]:
        """Get the region from an ISO 3166-1 numeric code.

        Args:
            code: The ISO 3166-1 numeric code.

        Returns:
            The RCN region or ``None`` if the code does not match a RCN region
            known to Biip.

        Raises:
            ValueError: If the code is not a valid ISO 3166-1 numeric code.

        Deprecated:
            This method was deprecated in Biip 2.2. It will be removed in Biip 3.0.
        """
        warnings.warn(
            "The method from_iso_3166_1_numeric_code() is deprecated "
            "and will be removed in Biip 3.0.",
            DeprecationWarning,
        )

        code = str(code).zfill(3)

        if len(code) != 3 or not code.isdecimal():
            raise ValueError(
                f"Expected ISO 3166-1 numeric code to be 3 digits, got {code!r}."
            )

        return {
            "208": RcnRegion.DENMARK,
            "233": RcnRegion.ESTONIA,
            "246": RcnRegion.FINLAND,
            "276": RcnRegion.GERMANY,
            "826": RcnRegion.GREAT_BRITAIN,
            "428": RcnRegion.LATVIA,
            "440": RcnRegion.LITHUANIA,
            "578": RcnRegion.NORWAY,
            "752": RcnRegion.SWEDEN,
        }.get(code)

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
