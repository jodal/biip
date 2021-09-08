"""Restricted Circulation Numbers (RCN)."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable, Dict, Optional

from biip import EncodeError, ParseError
from biip.gs1 import checksums
from biip.gtin import Gtin, RcnRegion, RcnUsage

try:
    import moneyed
except ImportError:  # pragma: no cover
    moneyed = None  # type: ignore


@dataclass
class Rcn(Gtin):
    """Restricted Circulation Number (RCN) is a subset of GTIN.

    Both RCN-8, RCN-12, and RCN-13 are supported. There is no 14 digit version
    of RCN.

    RCN-12 with prefix 2 and RCN-13 with prefix 02 or 20-29 have the same
    semantics across a geographic region, defined by the local GS1 Member
    Organization.

    RCN-8 with prefix 0 or 2, RCN-12 with prefix 4, and RCN-13 with prefix 04 or
    40-49 have semantics that are only defined within a single company.

    Use :meth:`biip.gtin.Gtin.parse` to parse potential RCNs. This subclass
    is returned if the GS1 Prefix signifies that the value is an RCN.

    References:
        GS1 General Specifications, section 2.1.11-2.1.12
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

    def __post_init__(self) -> None:
        """Initialize derivated fields."""
        self._set_usage()

    def _set_usage(self) -> None:
        # Classification as RCN depends on the prefix being known, so we won't
        # get here unless it is known.
        assert self.prefix is not None

        if "within a geographic region" in self.prefix.usage:
            self.usage = RcnUsage.GEOGRAPHICAL
        if "within a company" in self.prefix.usage:
            self.usage = RcnUsage.COMPANY

    def _parse_with_regional_rules(self, region: RcnRegion) -> None:
        if self.usage == RcnUsage.COMPANY:
            # The value is an RCN, but it is intended for use within a company,
            # so we can only interpret it as an opaque GTIN.
            return

        if not isinstance(region, RcnRegion):
            region = RcnRegion(region)
        self.region = region

        # Classification as RCN depends on the prefix being known, so we won't
        # get here unless it is known.
        assert self.prefix is not None
        rcn_prefix = self.prefix.value[:2]

        rules = _RCN_RULES.get(self.region)
        if rules is None:
            raise Exception(  # pragma: no cover
                "RCN region defined without defining rules. This is a bug."
            )

        strategy = rules.get(rcn_prefix)
        if strategy is None:
            # Without a strategy, we cannot extract anything.
            return

        if strategy.get_weight is not None:
            self.weight = strategy.get_weight(self)

        if strategy.get_price is not None:
            self.price = strategy.get_price(self)

        currency_code = self.region.get_currency_code()
        if self.price is not None and moneyed is not None and currency_code is not None:
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
            raise EncodeError(
                f"Cannot zero out the variable measure part of {self.value!r} as the "
                f"RCN rules for the geographical region {self.region!r} are unknown."
            )

        # Classification as RCN depends on the prefix being known, so we won't
        # get here unless it is known.
        assert self.prefix is not None
        rcn_prefix = self.prefix.value[:2]

        rules = _RCN_RULES.get(self.region)
        if rules is None:
            raise Exception(  # pragma: no cover
                "RCN region defined without defining rules. This is a bug."
            )

        strategy = rules.get(rcn_prefix)
        if strategy is None or strategy.without_variable_measure is None:
            # This prefix has no rules for removing variable parts.
            return self

        return strategy.without_variable_measure(self)


def _get_price_from_pppp(rcn: Rcn) -> Optional[Decimal]:
    # Get price from the last four digits of the payload, with the placement of
    # the decimal separator decided by the prefix.
    #
    # These rules are used in the following regions:
    # - Norway:
    #   No specification found, but products tested seems to match Swedish rules.
    # - Sweden:
    #   https://gs1.se/en/support/how-do-i-create-my-variable-weight-numbers/

    assert rcn.payload[:2] in ("20", "21", "22")

    value = rcn.payload[-4:]

    num_decimals = 2 - int(rcn.payload[1])
    num_units = 4 - num_decimals

    units = value[:num_units]
    decimals = value[num_units:]
    return Decimal(f"{units}.{decimals}")


def _get_price_from_vpppp_with_houndredths(rcn: Rcn) -> Optional[Decimal]:
    # Get price from the last five digits of the payload, where the first one is
    # a verification digit, and the price is given in hundredths of the currency.
    #
    # References:
    #   https://www.gs1uk.org/how-to-barcode-variable-measure-items

    check_digit = int(rcn.payload[-5])
    value = rcn.payload[-4:]

    calculated_check_digit = checksums.price_check_digit(value)
    if check_digit != calculated_check_digit:
        raise ParseError(
            f"Invalid price check digit for price data {value!r} "
            f"in RCN {rcn.value!r}: "
            f"Expected {calculated_check_digit!r}, got {check_digit!r}."
        )

    cents = Decimal(value)
    return cents / 100


def _get_weight_from_pppp(rcn: Rcn) -> Optional[Decimal]:
    # Get weight from the last four digits of the payload, with the placement of
    # the decimal separator decided by the prefix.
    #
    # References:
    # - Estonia, Latvia, and Lithuania:
    #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf
    # - Finland:
    #   https://gs1.fi/en/instructions/gs1-company-prefix/how-identify-product-gtin
    # - Norway:
    #   No specification found, but products tested seems to match these rules.
    # - Sweden:
    #   https://gs1.se/en/support/how-do-i-create-my-variable-weight-numbers/

    assert rcn.payload[:2] in ("23", "24", "25")

    value = rcn.payload[-4:]

    num_decimals = 6 - int(rcn.payload[1])
    num_units = 4 - num_decimals

    units = value[:num_units]
    decimals = value[num_units:]
    return Decimal(f"{units}.{decimals}")


def _zero_pppp(rcn: Rcn) -> Gtin:
    # Zero out the last four digits of the payload (pppp), and recalculate the
    # check digit.

    measure = "0000"
    payload = f"{rcn.value[:-5]}{measure}"
    check_digit = checksums.numeric_check_digit(payload)
    value = f"{payload}{check_digit}"
    return Gtin.parse(value, rcn_region=rcn.region)


def _zero_vpppp(rcn: Rcn) -> Gtin:
    # Zero out the last four digits of the payload (pppp), and recalculate both
    # the check digit and the price verifier digit (v).

    measure = "0000"
    price_check_digit = checksums.price_check_digit(measure)
    payload = f"{rcn.value[:-6]}{price_check_digit}{measure}"
    check_digit = checksums.numeric_check_digit(payload)
    value = f"{payload}{check_digit}"
    return Gtin.parse(value, rcn_region=rcn.region)


@dataclass
class _RcnStrategy:
    get_price: Optional[Callable[[Rcn], Optional[Decimal]]] = None
    get_weight: Optional[Callable[[Rcn], Optional[Decimal]]] = None
    without_variable_measure: Optional[Callable[[Rcn], Gtin]] = None


_price_from_pppp = _RcnStrategy(
    get_price=_get_price_from_pppp,
    without_variable_measure=_zero_pppp,
)

_weight_from_pppp = _RcnStrategy(
    get_weight=_get_weight_from_pppp,
    without_variable_measure=_zero_pppp,
)

_RCN_RULES: Dict[RcnRegion, Dict[str, _RcnStrategy]] = {
    RcnRegion.ESTONIA: {
        "23": _weight_from_pppp,
        "24": _weight_from_pppp,
        "25": _weight_from_pppp,
    },
    RcnRegion.FINLAND: {
        "23": _weight_from_pppp,
        "24": _weight_from_pppp,
        "25": _weight_from_pppp,
    },
    RcnRegion.GREAT_BRITAIN: {
        "20": _RcnStrategy(
            get_price=_get_price_from_vpppp_with_houndredths,
            without_variable_measure=_zero_vpppp,
        ),
    },
    RcnRegion.LATVIA: {
        "23": _weight_from_pppp,
        "24": _weight_from_pppp,
        "25": _weight_from_pppp,
    },
    RcnRegion.LITHUANIA: {
        "23": _weight_from_pppp,
        "24": _weight_from_pppp,
        "25": _weight_from_pppp,
    },
    RcnRegion.NORWAY: {
        "20": _price_from_pppp,
        "21": _price_from_pppp,
        "22": _price_from_pppp,
        "23": _weight_from_pppp,
        "24": _weight_from_pppp,
        "25": _weight_from_pppp,
    },
    RcnRegion.SWEDEN: {
        "20": _price_from_pppp,
        "21": _price_from_pppp,
        "22": _price_from_pppp,
        "23": _weight_from_pppp,
        "24": _weight_from_pppp,
        "25": _weight_from_pppp,
    },
}
