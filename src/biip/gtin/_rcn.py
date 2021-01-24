"""Restricted Circulation Numbers (RCN)."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from biip import EncodeError, ParseError
from biip.gs1 import checksums
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
    is returned if the GS1 Prefix signifies that the value is an RCN.
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

    def __post_init__(self: "Rcn") -> None:
        """Initialize derivated fields."""
        self._set_usage()

    def _set_usage(self: "Rcn") -> None:
        if "within a geographic region" in self.prefix.usage:
            self.usage = RcnUsage.GEOGRAPHICAL
        if "within a company" in self.prefix.usage:
            self.usage = RcnUsage.COMPANY

    def _parse_with_regional_rules(self: "Rcn", region: RcnRegion) -> None:
        if self.usage == RcnUsage.COMPANY:
            return

        if not isinstance(region, RcnRegion):
            region = RcnRegion(region)

        self.region = region

        if self.region in (RcnRegion.BALTICS,):
            self._parse_using_swedish_weight_rules()

        if self.region in (RcnRegion.GREAT_BRITAIN,):
            self._parse_using_british_price_rules()

        if self.region in (RcnRegion.NORWAY, RcnRegion.SWEDEN):
            self._parse_using_swedish_price_rules()
            self._parse_using_swedish_weight_rules()

        if self.price is not None and moneyed is not None:
            self.money = moneyed.Money(
                amount=self.price, currency=self.region.get_currency_code()
            )

    def _parse_using_british_price_rules(self: "Rcn") -> None:
        # References:
        #   https://www.gs1uk.org/how-to-barcode-variable-measure-items

        if self.payload[:2] not in ("20",):
            return

        check_digit = int(self.payload[-5])
        value = self.payload[-4:]

        calculated_check_digit = checksums.price_check_digit(value)
        if check_digit != calculated_check_digit:
            raise ParseError(
                f"Invalid price check digit for price data {value!r} "
                f"in RCN {self.value!r}: "
                f"Expected {calculated_check_digit!r}, got {check_digit!r}."
            )

        pounds_sterling = Decimal(value)
        self.price = pounds_sterling / 100

    def _parse_using_swedish_price_rules(self: "Rcn") -> None:
        # These rules are used in the following regions:
        # - Norway:
        #   No specification found, but products tested seems to match Swedish rules.
        # - Sweden:
        #   https://www.gs1.se/en/our-standards/Identify/variable-weight-number1/

        if self.payload[:2] not in ("20", "21", "22"):
            return

        value = self.payload[-4:]

        num_decimals = 2 - int(self.payload[1])
        num_units = 4 - num_decimals

        units = value[:num_units]
        decimals = value[num_units:]

        self.price = Decimal(f"{units}.{decimals}")

    def _parse_using_swedish_weight_rules(self: "Rcn") -> None:
        # These rules are used in the following regions:
        # - Baltics:
        #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf
        # - Norway:
        #   No specification found, but products tested seems to match Swedish rules.
        # - Sweden:
        #   https://www.gs1.se/en/our-standards/Identify/variable-weight-number1/

        if self.payload[:2] not in ("23", "24", "25"):
            return

        value = self.payload[-4:]

        num_decimals = 6 - int(self.payload[1])
        num_units = 4 - num_decimals

        units = value[:num_units]
        decimals = value[num_units:]

        self.weight = Decimal(f"{units}.{decimals}")

    def without_variable_measure(self: "Rcn") -> Gtin:
        """Create a new RCN where the variable measure is zeroed out.

        This provides us with a number which still includes the item
        reference, but does not vary with weight/price, and can thus be used
        to lookup the relevant trade item in a database or similar.

        This has no effect on RCNs intended for use within a company, as
        the semantics of those numbers vary from company to company.

        Returns:
            A new RCN instance with zeros in the variable measure places.

        Raises:
            EncodeError: If the rules for variable measures in the region are unknown.
        """
        if self.usage == RcnUsage.COMPANY:
            return self

        if self.region in (
            RcnRegion.BALTICS,
            RcnRegion.NORWAY,
            RcnRegion.SWEDEN,
        ):
            measure = "0000"
            payload = f"{self.value[:-5]}{measure}"
            check_digit = checksums.numeric_check_digit(payload)
            value = f"{payload}{check_digit}"
            return Gtin.parse(value, rcn_region=self.region)
        elif self.region in (RcnRegion.GREAT_BRITAIN,):
            measure = "0000"
            price_check_digit = checksums.price_check_digit(measure)
            payload = f"{self.value[:-6]}{price_check_digit}{measure}"
            check_digit = checksums.numeric_check_digit(payload)
            value = f"{payload}{check_digit}"
            return Gtin.parse(value, rcn_region=self.region)
        else:
            raise EncodeError(
                f"Cannot zero out the variable measure part of {self.value!r} as the "
                f"RCN rules for the geographical region {self.region!r} are unknown."
            )
