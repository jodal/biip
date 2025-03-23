"""Restricted Circulation Number (RCN) is a subset of GTIN.

Both RCN-8, RCN-12, and RCN-13 are supported. There is no 14 digit version
of RCN.

RCN-12 with prefix 2 and RCN-13 with prefix 02 or 20-29 have the same
semantics across a geographic region, defined by the local GS1 Member
Organization.

RCN-8 with prefix 0 or 2, RCN-12 with prefix 4, and RCN-13 with prefix 04 or
40-49 have semantics that are only defined within a single company.

Use [`Gtin.parse()`][biip.gtin.Gtin.parse] to parse potential RCNs. This
subclass is returned if the GS1 Prefix signifies that the value is an RCN.

References:
    GS1 General Specifications, section 2.1.11-2.1.12
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any

from biip import EncodeError, ParseError
from biip.checksums import gs1_price_weight_check_digit, gs1_standard_check_digit
from biip.gtin import Gtin

if TYPE_CHECKING:
    from collections.abc import Iterator

try:
    import moneyed  # noqa: TC002

    have_moneyed = True
except ImportError:  # pragma: no cover
    have_moneyed = False

__all__ = ["Rcn", "RcnRegion", "RcnUsage"]


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

    def get_currency_code(self) -> str | None:
        """Get the ISO-4217 currency code for the region."""
        return {
            RcnRegion.DENMARK: "DKK",
            RcnRegion.GERMANY: "EUR",
            RcnRegion.GREAT_BRITAIN: "GBP",
            RcnRegion.NORWAY: "NOK",
            RcnRegion.SWEDEN: "SEK",
        }.get(self)


@dataclass
class Rcn(Gtin):
    """Data class containing an RCN.

    This is a subclass of [`Gtin`][biip.gtin.Gtin]. To create an `Rcn` instance,
    use [`Gtin.parse()`][biip.gtin.Gtin.parse] with an RCN string as the value
    to parse.
    """

    usage: RcnUsage | None = field(default=None)
    """Where the RCN can be circulated, in a geographical region or within a company."""

    region: RcnRegion | None = field(default=None)
    """The geographical region.

    The region's rules are used to interpret the contents of the RCN.
    """

    weight: Decimal | None = field(default=None)
    """A variable weight value extracted from the GTIN."""

    count: int | None = field(default=None)
    """A variable count extracted from the GTIN."""

    price: Decimal | None = field(default=None)
    """A variable weight price extracted from the GTIN."""

    money: moneyed.Money | None = field(default=None)
    """A Money value created from the variable weight price.

    Only set if [`py-moneyed`](https://pypi.org/project/py-moneyed/) is
    installed and the currency is known.
    """

    def __post_init__(self) -> None:
        """Initialize derivated fields."""
        self._set_usage()

    def __rich_repr__(self) -> Iterator[tuple[str, Any] | tuple[str, Any, Any]]:  # noqa: D105
        # Skip printing fields with default values
        yield from super().__rich_repr__()
        yield "usage", self.usage, None
        yield "region", self.region, None
        yield "weight", self.weight, None
        yield "count", self.count, None
        yield "price", self.price, None
        yield "money", self.money, None

    def _set_usage(self) -> None:
        # Classification as RCN depends on the prefix being known, so we won't
        # get here unless it is known.
        assert self.prefix is not None

        if "within a geographic region" in self.prefix.usage:
            self.usage = RcnUsage.GEOGRAPHICAL
        if "within a company" in self.prefix.usage:
            self.usage = RcnUsage.COMPANY

    def _parse_with_regional_rules(
        self,
        *,
        region: RcnRegion | str,
        verify_variable_measure: bool,
    ) -> None:
        if self.usage == RcnUsage.COMPANY:
            # The value is an RCN, but it is intended for use within a company,
            # so we can only interpret it as an opaque GTIN.
            return

        if not isinstance(region, RcnRegion):
            region = RcnRegion(region)
        self.region = region

        strategy = _Strategy.get_for_rcn(self)
        if strategy is None:
            # Without a strategy, we cannot extract anything.
            return

        if verify_variable_measure:
            strategy.verify_check_digit(self)

        if strategy.measure_type == _MeasureType.WEIGHT:
            self.weight = strategy.get_variable_measure(self)

        if strategy.measure_type == _MeasureType.COUNT:
            self.count = int(strategy.get_variable_measure(self))

        if strategy.measure_type == _MeasureType.PRICE:
            self.price = strategy.get_variable_measure(self)

        currency_code = self.region.get_currency_code()
        if self.price is not None and have_moneyed and currency_code is not None:
            import moneyed

            self.money = moneyed.Money(amount=self.price, currency=currency_code)

    def without_variable_measure(self) -> Gtin:
        """Create a new RCN where the variable measure is zeroed out.

        This provides us with a number which still includes the item
        reference, but does not vary with weight/price, and can thus be used
        to lookup the relevant trade item in a database or similar.

        This has no effect on RCNs intended for use within a company, as
        the semantics of those numbers vary from company to company.

        Returns:
            A RCN instance with zeros in the variable measure places.

        Raises:
            EncodeError: If the rules for variable measures in the region are unknown.
        """
        if self.usage == RcnUsage.COMPANY:
            # The value is an RCN, but it is intended for use within a company,
            # so we can only interpret it as an opaque GTIN.
            return self

        if self.region is None:
            msg = (
                f"Cannot zero out the variable measure part of {self.value!r} as the "
                f"RCN rules for the geographical region {self.region!r} are unknown."
            )
            raise EncodeError(msg)

        strategy = _Strategy.get_for_rcn(self)
        if strategy is None:
            # This prefix has no rules for removing variable parts.
            return self

        return strategy.without_variable_measure(self)


class _MeasureType(str, Enum):
    COUNT = "count"
    PRICE = "price"
    WEIGHT = "weight"


@dataclass
class _Strategy:
    measure_type: _MeasureType
    pattern: str
    num_decimals: int

    prefix_slice: slice = field(init=False)
    value_slice: slice = field(init=False)
    check_digit_slice: slice | None = field(init=False)

    @classmethod
    def get_for_rcn(cls, rcn: Rcn) -> _Strategy | None:
        # The RCN's geographical region must be known to lookup the correct
        # strategy for interpreting the RCN's variable measure.
        assert rcn.region is not None

        region_rules = _RCN_RULES.get(rcn.region)
        if region_rules is None:  # pragma: no cover
            msg = "RCN region defined without defining rules. This is a bug."
            raise Exception(msg)  # noqa: TRY002

        # Classification as RCN depends on the prefix being known, so we won't
        # get here unless it is known.
        assert rcn.prefix is not None

        rcn_prefix = rcn.prefix.value[:2]
        return region_rules.get(rcn_prefix)

    def __post_init__(self) -> None:
        assert len(self.pattern) == 12, "Pattern must be exactly 12 chars long."

        prefix_slice = self._get_pattern_slice("P")
        value_slice = self._get_pattern_slice("V")

        assert prefix_slice is not None, "Pattern must contain a prefix marker (P)."
        assert value_slice is not None, "Pattern must contain a value marker (V)."

        self.prefix_slice = prefix_slice
        self.value_slice = value_slice
        self.check_digit_slice = self._get_pattern_slice("C")

    def _get_pattern_slice(self, char: str) -> slice | None:
        if char not in self.pattern:
            return None
        return slice(self.pattern.index(char), self.pattern.rindex(char) + 1)

    def verify_check_digit(self, rcn: Rcn) -> None:
        if self.check_digit_slice is None:
            return

        rcn_13 = rcn.as_gtin_13()
        value = rcn_13[self.value_slice]
        check_digit = int(rcn_13[self.check_digit_slice])
        calculated_check_digit = gs1_price_weight_check_digit(value)

        if check_digit != calculated_check_digit:
            msg = (
                f"Invalid check digit for variable measure value {value!r} "
                f"in RCN {rcn.value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )
            raise ParseError(msg)

    def get_variable_measure(self, rcn: Rcn) -> Decimal:
        rcn_13 = rcn.as_gtin_13()
        value = Decimal(rcn_13[self.value_slice])
        return value / Decimal(10) ** self.num_decimals

    def without_variable_measure(self, rcn: Rcn) -> Gtin:
        # Zero out the variable measure part of the payload, and recalculate both
        # the GTIN check digit and the variable measure's check digit digit, if any.

        rcn_13 = rcn.as_gtin_13()
        zeroed_value = "0" * len(rcn_13[self.value_slice])

        digits = list(self.pattern)
        digits[self.prefix_slice] = list(rcn_13[self.prefix_slice])
        digits[self.value_slice] = list(zeroed_value)
        if self.check_digit_slice is not None:
            digits[self.check_digit_slice] = [
                str(gs1_price_weight_check_digit(zeroed_value))
            ]

        gtin_payload = "".join(digits)
        gtin_check_digit = gs1_standard_check_digit(gtin_payload)
        gtin = f"{gtin_payload}{gtin_check_digit}"
        return Gtin.parse(gtin, rcn_region=rcn.region)


_RCN_RULES: dict[RcnRegion, dict[str, _Strategy]] = {
    RcnRegion.DENMARK: {
        # References:
        #   https://www.gs1.dk/om-gs1/overblik-over-gs1-standarder/gtin-13-pris
        #   https://www.gs1.dk/om-gs1/overblik-over-gs1-standarder/gtin-13-vaegt
        "21": _Strategy(_MeasureType.PRICE, "PPPPPPVVVVVV", num_decimals=2),
        "22": _Strategy(_MeasureType.PRICE, "PPPPPPVVVVVV", num_decimals=2),
        "23": _Strategy(_MeasureType.PRICE, "PPPPPPVVVVVV", num_decimals=2),
        "24": _Strategy(_MeasureType.PRICE, "PPPPPPVVVVVV", num_decimals=2),
        "26": _Strategy(_MeasureType.WEIGHT, "PPPPPPVVVVVV", num_decimals=3),
        "27": _Strategy(_MeasureType.WEIGHT, "PPPPPPPVVVVV", num_decimals=3),
        "28": _Strategy(_MeasureType.WEIGHT, "PPPPPPVVVVVV", num_decimals=3),
    },
    RcnRegion.ESTONIA: {
        # References:
        #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf
        "23": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=3),
        "24": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=2),
        "25": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=1),
    },
    RcnRegion.FINLAND: {
        # References:
        #   https://gs1.fi/en/instructions/gs1-company-prefix/how-identify-product-gtin
        "23": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=3),
        "24": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=2),
        "25": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=1),
    },
    RcnRegion.GERMANY: {
        # References:
        #   https://www.gs1-germany.de/fileadmin/gs1/fachpublikationen/globale-artikelnummer-gtin-in-der-anwendung.pdf
        #   https://san.gs1-germany.de/SAN-4-Konzept
        "22": _Strategy(_MeasureType.PRICE, "PPPPPPCVVVVV", num_decimals=2),
        "23": _Strategy(_MeasureType.PRICE, "PPPPPPCVVVVV", num_decimals=2),
        "25": _Strategy(_MeasureType.COUNT, "PPPPPPCVVVVV", num_decimals=0),
        "26": _Strategy(_MeasureType.COUNT, "PPPPPPCVVVVV", num_decimals=0),
        "28": _Strategy(_MeasureType.WEIGHT, "PPPPPPCVVVVV", num_decimals=3),
        "29": _Strategy(_MeasureType.WEIGHT, "PPPPPPCVVVVV", num_decimals=3),
    },
    RcnRegion.GREAT_BRITAIN: {
        # References:
        #   https://www.gs1uk.org/how-to-barcode-variable-measure-items
        "20": _Strategy(_MeasureType.PRICE, "PPPPPPPCVVVV", num_decimals=2),
    },
    RcnRegion.LATVIA: {
        # References:
        #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf
        "23": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=3),
        "24": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=2),
        "25": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=1),
    },
    RcnRegion.LITHUANIA: {
        # References:
        #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf
        "23": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=3),
        "24": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=2),
        "25": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=1),
    },
    RcnRegion.NORWAY: {
        # References:
        #   No specification found, but products tested seems to match Swedish rules.
        "20": _Strategy(_MeasureType.PRICE, "PPPPPPPPVVVV", num_decimals=2),
        "21": _Strategy(_MeasureType.PRICE, "PPPPPPPPVVVV", num_decimals=1),
        "22": _Strategy(_MeasureType.PRICE, "PPPPPPPPVVVV", num_decimals=0),
        "23": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=3),
        "24": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=2),
        "25": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=1),
    },
    RcnRegion.SWEDEN: {
        # References:
        #   https://gs1.se/en/support/how-do-i-create-my-variable-weight-numbers/
        "20": _Strategy(_MeasureType.PRICE, "PPPPPPPPVVVV", num_decimals=2),
        "21": _Strategy(_MeasureType.PRICE, "PPPPPPPPVVVV", num_decimals=1),
        "22": _Strategy(_MeasureType.PRICE, "PPPPPPPPVVVV", num_decimals=0),
        "23": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=3),
        "24": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=2),
        "25": _Strategy(_MeasureType.WEIGHT, "PPPPPPPPVVVV", num_decimals=1),
    },
}
