"""GS1 Element Strings."""

from __future__ import annotations

import calendar
import datetime as dt
import re
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from biip import ParseError
from biip.gln import Gln
from biip.gs1_application_identifiers import GS1ApplicationIdentifier
from biip.gtin import Gtin
from biip.sscc import Sscc

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from biip.rcn import RcnRegion

try:
    import moneyed  # noqa: TC002

    have_moneyed = True
except ImportError:  # pragma: no cover
    have_moneyed = False


@dataclass
class GS1ElementString:
    """GS1 Element String.

    An Element String consists of a GS1 Application Identifier (AI) and its data field.

    A single barcode can contain multiple Element Strings. Together these are
    called a "message."

    Examples:
        >>> from biip.gs1_messages import GS1ElementString
        >>> element_string = GS1ElementString.extract("0107032069804988")
        >>> pprint(element_string)
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='01',
                description='Global Trade Item Number (GTIN)',
                data_title='GTIN',
                separator_required=False,
                format='N2+N14'
            ),
            value='07032069804988',
            pattern_groups=[
                '07032069804988'
            ],
            gtin=Gtin(
                value='07032069804988',
                format=GtinFormat.GTIN_13,
                prefix=GS1Prefix(
                    value='703',
                    usage='GS1 Norway'
                ),
                company_prefix=GS1CompanyPrefix(
                    value='703206'
                ),
                payload='703206980498',
                check_digit=8
            )
        )
        >>> element_string.as_hri()
        '(01)07032069804988'
    """

    ai: GS1ApplicationIdentifier
    """The element's Application Identifier (AI)."""

    value: str
    """Raw data field of the Element String. Does not include the AI."""

    pattern_groups: list[str]
    """List of pattern groups extracted from the Element String."""

    gln: Gln | None = None
    """A GLN created from the element string, if the AI represents a GLN."""

    gln_error: str | None = None
    """The GLN parse error, if parsing as a GLN was attempted and failed."""

    gtin: Gtin | None = None
    """A GTIN created from the element string, if the AI represents a GTIN."""

    gtin_error: str | None = None
    """The GTIN parse error, if parsing as a GTIN was attempted and failed."""

    sscc: Sscc | None = None
    """An SSCC created from the element string, if the AI represents a SSCC."""

    sscc_error: str | None = None
    """The SSCC parse error, if parsing as an SSCC was attempted and failed."""

    date: dt.date | None = None
    """A date created from the element string, if the AI represents a date."""

    datetime: dt.datetime | None = None
    """A datetime created from the element string, if the AI represents a datetime."""

    decimal: Decimal | None = None
    """A decimal value created from the element string, if the AI represents a
    number."""

    money: moneyed.Money | None = None
    """A Money value created from the element string, if the AI represents a
    currency and an amount.

    Only set if `py-moneyed` is installed.
    """

    @classmethod
    def extract(
        cls,
        value: str,
        *,
        rcn_region: RcnRegion | None = None,
        rcn_verify_variable_measure: bool = True,
        separator_chars: Iterable[str] = ("\x1d",),
    ) -> GS1ElementString:
        """Extract the first GS1 Element String from the given value.

        If the element string contains a primitive data type, like a date,
        decimal number, or currency, it will be parsed and stored in the
        [`date`][biip.gs1_messages.GS1ElementString.date],
        [`decimal`][biip.gs1_messages.GS1ElementString.decimal], or
        [`money`][biip.gs1_messages.GS1ElementString.money] field respectively.
        If parsing of a primitive data type fails, a
        [`ParseError`][biip.ParseError] will be raised.

        If the element string contains another supported format, like a GLN,
        GTIN, or SSCC, it will parsed and validated, and the result stored in
        the fields
        [`gln`][biip.gs1_messages.GS1ElementString.gln],
        [`gtin`][biip.gs1_messages.GS1ElementString.gtin], or
        [`sscc`][biip.gs1_messages.GS1ElementString.sscc] respectively. If parsing or
        validation of an inner format fails, the
        [`gln_error`][biip.gs1_messages.GS1ElementString.gln_error],
        [`gtin_error`][biip.gs1_messages.GS1ElementString.gtin_error], or
        [`sscc_error`][biip.gs1_messages.GS1ElementString.sscc_error] field will be set.
        No [`ParseError`][biip.ParseError] will be raised.

        Args:
            value: The string to extract an Element String from. May contain
                more than one Element String.
            rcn_region: The geographical region whose rules should be used to
                interpret Restricted Circulation Numbers (RCN).
                Needed to extract e.g. variable weight/price from GTIN.
            rcn_verify_variable_measure: Whether to verify that the variable
                measure in a RCN matches its check digit, if present. Some
                companies use the variable measure check digit for other
                purposes, requiring this check to be disabled.
            separator_chars: Characters used in place of the FNC1 symbol.
                Defaults to `<GS>` (ASCII value 29).
                If variable-length fields are not terminated with a separator
                character, the parser might greedily consume later fields.

        Returns:
            A data class with the Element String's parts and data extracted from it.

        Raises:
            ValueError: If the `separator_char` isn't exactly 1 character long.
            ParseError: If the parsing fails.
        """
        if any(len(char) != 1 for char in separator_chars):
            msg = (
                "All separator characters must be exactly 1 character long, "
                f"got {list(separator_chars)!r}."
            )
            raise ValueError(msg)

        ai = GS1ApplicationIdentifier.extract(value)

        for separator_char in separator_chars:
            value = value.split(separator_char, maxsplit=1)[0]

        pattern = ai.pattern.removesuffix("$")
        matches = re.match(pattern, value)
        if not matches:
            msg = f"Failed to match {value!r} with GS1 AI {ai} pattern '{ai.pattern}'."
            raise ParseError(msg)
        pattern_groups = [group for group in matches.groups() if group is not None]
        value = "".join(pattern_groups)

        element = cls(ai=ai, value=value, pattern_groups=pattern_groups)
        element._set_gln()
        element._set_gtin(
            rcn_region=rcn_region,
            rcn_verify_variable_measure=rcn_verify_variable_measure,
        )
        element._set_sscc()
        element._set_date_and_datetime()
        element._set_decimal()

        return element

    def _set_gln(self) -> None:
        if self.ai.ai[:2] != "41":
            return

        try:
            self.gln = Gln.parse(self.value)
            self.gln_error = None
        except ParseError as exc:
            self.gln = None
            self.gln_error = str(exc)

    def _set_gtin(
        self,
        *,
        rcn_region: RcnRegion | None,
        rcn_verify_variable_measure: bool,
    ) -> None:
        if self.ai.ai not in ("01", "02"):
            return

        try:
            self.gtin = Gtin.parse(
                self.value,
                rcn_region=rcn_region,
                rcn_verify_variable_measure=rcn_verify_variable_measure,
            )
            self.gtin_error = None
        except ParseError as exc:
            self.gtin = None
            self.gtin_error = str(exc)

    def _set_sscc(self) -> None:
        if self.ai.ai != "00":
            return

        try:
            self.sscc = Sscc.parse(self.value)
            self.sscc_error = None
        except ParseError as exc:
            self.sscc = None
            self.sscc_error = str(exc)

    def _set_date_and_datetime(self) -> None:
        if self.ai.ai not in (
            "11",
            "12",
            "13",
            "15",
            "16",
            "17",
            "4324",
            "4325",
            "4326",
            "7003",
            "7006",
            "7007",
            "7011",
            "8008",
        ):
            return

        try:
            self.date, self.datetime = _parse_date_and_datetime(self.value)
        except ValueError as exc:
            msg = f"Failed to parse GS1 AI {self.ai} date/time from {self.value!r}."
            raise ParseError(msg) from exc

    def _set_decimal(self) -> None:
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

        if amount_payable_with_currency and have_moneyed:
            import moneyed

            currency = moneyed.get_currency(iso=self.pattern_groups[0])
            self.money = moneyed.Money(amount=self.decimal, currency=currency)

    def __len__(self) -> int:
        """Get the length of the element string."""
        return len(self.ai) + len(self.value)

    def __rich_repr__(self) -> Iterator[tuple[str, Any] | tuple[str, Any, Any]]:
        # Skip printing fields with default values
        yield "ai", self.ai
        yield "value", self.value
        yield "pattern_groups", self.pattern_groups
        yield "gln", self.gln, None
        yield "gln_error", self.gln_error, None
        yield "gtin", self.gtin, None
        yield "gtin_error", self.gtin_error, None
        yield "sscc", self.sscc, None
        yield "sscc_error", self.sscc_error, None
        yield "date", self.date, None
        yield "datetime", self.datetime, None
        yield "decimal", self.decimal, None
        yield "money", self.money, None

    def as_hri(self) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below the barcode.

        Returns:
            A human-readable string where the AI is wrapped in parenthesis.
        """
        return f"{self.ai}{self.value}"


def _parse_date_and_datetime(value: str) -> tuple[dt.date, dt.datetime | None]:
    pairs = [value[i : i + 2] for i in range(0, len(value), 2)]

    year = int(pairs[0])
    year += _get_century(year)
    month = int(pairs[1])
    day = int(pairs[2])
    if day == 0:
        day = _get_last_day_of_month(year, month)
    date = dt.date(year, month, day)
    if not pairs[3:]:
        return date, None

    hour = int(pairs[3])
    minute = int(pairs[4] if pairs[4:] else 0)
    seconds = int(pairs[5] if pairs[5:] else 0)
    if hour == 99 and minute == 99:
        return date, None

    return date, dt.datetime(year, month, day, hour, minute, seconds)  # noqa: DTZ001


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
    current_year = dt.datetime.now(tz=dt.timezone.utc).year
    current_century = current_year - current_year % 100
    two_digit_current_year = current_year - current_century

    # Previous century
    if 51 <= two_digit_year - two_digit_current_year <= 99:
        return current_century - 100

    # Next century
    if -99 <= two_digit_year - two_digit_current_year <= -50:
        # Skipping coverage as this code won't run until year 2051
        return current_century + 100  # pragma: no cover

    # Current century
    return current_century


def _get_last_day_of_month(year: int, month: int) -> int:
    """Get the last day of the given month."""
    return calendar.monthrange(year, month)[1]
