"""GS1 Element Strings."""

import calendar
import datetime
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List, Optional, Type

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHARS, GS1ApplicationIdentifier
from biip.gtin import Gtin, RcnRegion
from biip.sscc import Sscc

try:
    import moneyed
except ImportError:  # pragma: no cover
    moneyed = None


@dataclass
class GS1ElementString:
    """GS1 Element String.

    An Element String consists of a GS1 Application Identifier (AI) and its data field.

    A single barcode can contain multiple Element Strings. Together these are
    called a "message."

    Example:
        >>> from biip.gs1 import GS1ElementString
        >>> element_string = GS1ElementString.extract("0107032069804988")
        >>> element_string
        GS1ElementString(ai=GS1ApplicationIdentifier(ai='01',
        description='Global Trade Item Number (GTIN)', data_title='GTIN',
        fnc1_required=False, format='N2+N14'), value='07032069804988',
        pattern_groups=['07032069804988'], gtin=Gtin(value='07032069804988',
        format=GtinFormat.GTIN_13, prefix=GS1Prefix(value='703', usage='GS1
        Norway'), payload='703206980498', check_digit=8,
        packaging_level=None), sscc=None, date=None, decimal=None, money=None)
        >>> element_string.as_hri()
        '(01)07032069804988'
    """

    #: The element's Application Identifier (AI).
    ai: GS1ApplicationIdentifier

    #: Raw data field of the Element String. Does not include the AI.
    value: str

    #: List of pattern groups extracted from the Element String.
    pattern_groups: List[str]

    #: A GTIN created from the element string, if the AI represents a GTIN.
    gtin: Optional[Gtin] = None

    #: An SSCC created from the element string, if the AI represents a SSCC.
    sscc: Optional[Sscc] = None

    #: A date created from the element string, if the AI represents a date.
    date: Optional[datetime.date] = None

    #: A decimal value created from the element string, if the AI represents a number.
    decimal: Optional[Decimal] = None

    #: A Money value created from the element string, if the AI represents a
    #: currency and an amount. Only set if py-moneyed is installed.
    money: Optional["moneyed.Money"] = None

    @classmethod
    def extract(
        cls: Type["GS1ElementString"],
        value: str,
        *,
        rcn_region: Optional[RcnRegion] = None,
        separator_chars: Iterable[str] = DEFAULT_SEPARATOR_CHARS,
    ) -> "GS1ElementString":
        """Extract the first GS1 Element String from the given value.

        Args:
            value: The string to extract an Element String from. May contain
                more than one Element String.
            rcn_region: The geographical region whose rules should be used to
                interpret Restricted Circulation Numbers (RCN).
                Needed to extract e.g. variable weight/price from GTIN.
            separator_chars: Characters used in place of the FNC1 symbol.
                Defaults to `<GS>` (ASCII value 29).
                If variable-length fields are not terminated with a separator
                character, the parser might greedily consume later fields.

        Returns:
            A data class with the Element String's parts and data extracted from it.

        Raises:
            ValueError: If the ``separator_char`` isn't exactly 1 character long.
            ParseError: If the parsing fails.
        """
        if any(len(char) != 1 for char in separator_chars):
            raise ValueError(
                "All separator characters must be exactly 1 character long, "
                f"got {list(separator_chars)!r}."
            )

        ai = GS1ApplicationIdentifier.extract(value)

        for separator_char in separator_chars:
            value = value.split(separator_char, maxsplit=1)[0]

        pattern = ai.pattern[:-1] if ai.pattern.endswith("$") else ai.pattern
        matches = re.match(pattern, value)
        if not matches:
            raise ParseError(
                f"Failed to match {value!r} with GS1 AI {ai} pattern '{ai.pattern}'."
            )
        pattern_groups = list(matches.groups())
        value = "".join(pattern_groups)

        element = cls(ai=ai, value=value, pattern_groups=pattern_groups)
        element._set_gtin(rcn_region=rcn_region)
        element._set_sscc()
        element._set_date()
        element._set_decimal()

        return element

    def _set_gtin(
        self: "GS1ElementString", *, rcn_region: Optional[RcnRegion] = None
    ) -> None:
        if self.ai.ai not in ("01", "02"):
            return

        self.gtin = Gtin.parse(self.value, rcn_region=rcn_region)

    def _set_sscc(self: "GS1ElementString") -> None:
        if self.ai.ai != "00":
            return

        self.sscc = Sscc.parse(self.value)

    def _set_date(self: "GS1ElementString") -> None:
        if self.ai.ai not in ("11", "12", "13", "15", "16", "17"):
            return

        try:
            self.date = _parse_date(self.value)
        except ValueError:
            raise ParseError(
                f"Failed to parse GS1 AI {self.ai} date from {self.value!r}."
            )

    def _set_decimal(self: "GS1ElementString") -> None:
        variable_measure = self.ai.ai[:2] in (
            "31",
            "32",
            "33",
            "34",
            "35",
            "36",
        )
        amount_payable = self.ai.ai[:3] in ("390", "392")
        amount_payable_with_currency = self.ai.ai[:3] in ("391", "393")
        percentage = self.ai.ai[:3] in ("394",)

        if (
            variable_measure
            or amount_payable
            or amount_payable_with_currency
            or percentage
        ):
            # See GS1 General Specifications, chapter 3.6 for details.

            # Only group for variable_measure, amount_payable, and percentage.
            # Second and last group for amount_payable_with_currency.
            value = self.pattern_groups[-1]

            num_decimals = int(self.ai.ai[3])
            num_units = len(value) - num_decimals

            units = value[:num_units]
            decimals = value[num_units:]

            self.decimal = Decimal(f"{units}.{decimals}")

        if amount_payable_with_currency and moneyed is not None:
            currency = moneyed.get_currency(iso=self.pattern_groups[0])
            self.money = moneyed.Money(amount=self.decimal, currency=currency)

    def __len__(self: "GS1ElementString") -> int:
        """Get the length of the element string."""
        return len(self.ai) + len(self.value)

    def as_hri(self: "GS1ElementString") -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below the barcode.

        Returns:
            A human-readable string where the AI is wrapped in parenthesis.
        """
        return f"{self.ai}{self.value}"


def _parse_date(value: str) -> datetime.date:
    year, month, day = int(value[0:2]), int(value[2:4]), int(value[4:6])
    year += _get_century(year)
    if day == 0:
        day = _get_last_day_of_month(year, month)
    return datetime.date(year, month, day)


def _get_century(two_digit_year: int) -> int:
    """Get century from two-digit year.

    The two-digit year refers to a year in the range between 49 years past
    and 50 years into the future.

    Args:
        two_digit_year: A two-digit year, e.g. without century specified.

    Returns:
        The century the year is in.

    References:
        GS1 General Specifications, section 7.12
    """
    current_year = datetime.date.today().year
    current_century = current_year - current_year % 100
    two_digit_current_year = current_year - current_century

    if 51 <= two_digit_year - two_digit_current_year <= 99:
        return current_century - 100  # Previous century
    elif -99 <= two_digit_year - two_digit_current_year <= -50:
        # Next century
        # Skipping coverage as this code won't run until year 2051
        return current_century + 100  # pragma: no cover
    else:
        return current_century  # Current century


def _get_last_day_of_month(year: int, month: int) -> int:
    """Get the last day of the given month."""
    return calendar.monthrange(year, month)[1]
