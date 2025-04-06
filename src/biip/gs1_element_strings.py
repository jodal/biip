"""GS1 element strings.

An element string consists of a GS1 Application Identifier (AI) and its data field.

Element strings are usually found in a GS1 message or a GS1 Web URI. A single
barcode can contain multiple element strings.

Examples:
    >>> from biip.gs1_element_strings import GS1ElementString
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

from __future__ import annotations

import calendar
import datetime as dt
import re
from collections.abc import Iterator
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from biip import ParseError
from biip._parser import ParseConfig
from biip.gln import Gln
from biip.gs1_application_identifiers import GS1ApplicationIdentifier
from biip.gtin import Gtin
from biip.sscc import Sscc

if TYPE_CHECKING:
    from collections.abc import Iterator


try:
    import moneyed  # noqa: TC002

    have_moneyed = True
except ImportError:  # pragma: no cover
    have_moneyed = False


@dataclass(frozen=True)
class GS1ElementString:
    """A GS1 element string consists of an Application Identifier (AI) and a value."""

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
        config: ParseConfig | None = None,
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
            config: Configuration options for parsing.

        Returns:
            A data class with the Element String's parts and data extracted from it.

        Raises:
            ValueError: If the `separator_char` isn't exactly 1 character long.
            ParseError: If the parsing fails.
        """
        if config is None:
            config = ParseConfig()

        if any(len(char) != 1 for char in config.separator_chars):
            msg = (
                "All separator characters must be exactly 1 character long, "
                f"got {list(config.separator_chars)!r}."
            )
            raise ValueError(msg)

        ai = GS1ApplicationIdentifier.extract(value)

        for separator_char in config.separator_chars:
            value = value.split(separator_char, maxsplit=1)[0]

        pattern = ai.pattern.removesuffix("$")
        matches = re.match(pattern, value)
        if not matches:
            msg = f"Failed to match {value!r} with GS1 AI {ai} pattern '{ai.pattern}'."
            raise ParseError(msg)
        pattern_groups = [group for group in matches.groups() if group is not None]
        value = "".join(pattern_groups)

        element = cls(ai=ai, value=value, pattern_groups=pattern_groups)
        element = element._with_gln(config=config)
        element = element._with_gtin(config=config)  # noqa: SLF001
        element = element._with_sscc(config=config)  # noqa: SLF001
        element = element._with_date_and_datetime(config=config)  # noqa: SLF001
        element = element._with_decimal()  # noqa: SLF001

        return element  # noqa: RET504

    def _with_gln(self, *, config: ParseConfig) -> GS1ElementString:
        if self.ai.ai[:2] != "41":
            return self

        try:
            gln = Gln.parse(self.value, config=config)
            gln_error = None
        except ParseError as exc:
            gln = None
            gln_error = str(exc)

        return replace(self, gln=gln, gln_error=gln_error)

    def _with_gtin(self, *, config: ParseConfig) -> GS1ElementString:
        if self.ai.ai not in ("01", "02", "03"):
            return self

        try:
            gtin = Gtin.parse(self.value, config=config)
            gtin_error = None
        except ParseError as exc:
            gtin = None
            gtin_error = str(exc)

        return replace(self, gtin=gtin, gtin_error=gtin_error)

    def _with_sscc(self, *, config: ParseConfig) -> GS1ElementString:
        if self.ai.ai != "00":
            return self

        try:
            sscc = Sscc.parse(self.value, config=config)
            sscc_error = None
        except ParseError as exc:
            sscc = None
            sscc_error = str(exc)

        return replace(self, sscc=sscc, sscc_error=sscc_error)

    def _with_date_and_datetime(self, *, config: ParseConfig) -> GS1ElementString:
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
            return self

        try:
            date, datetime = _parse_date_and_datetime(self.value)
        except ValueError as exc:
            if not config.gs1_element_strings_verify_date:
                return self
            msg = f"Failed to parse GS1 AI {self.ai} date/time from {self.value!r}."
            raise ParseError(msg) from exc

        return replace(self, date=date, datetime=datetime)

    def _with_decimal(self) -> GS1ElementString:
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

            decimal = Decimal(f"{units}.{decimals}")
        else:
            decimal = None

        if amount_payable_with_currency and have_moneyed:
            import moneyed

            currency = moneyed.get_currency(iso=self.pattern_groups[0])
            money = moneyed.Money(amount=decimal, currency=currency)
        else:
            money = None

        return replace(self, decimal=decimal, money=money)

    def __len__(self) -> int:
        """Get the length of the element string."""
        return len(self.ai) + len(self.value)

    def __rich_repr__(self) -> Iterator[tuple[str, Any] | tuple[str, Any, Any]]:  # noqa: D105
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


class GS1ElementStrings(list[GS1ElementString]):
    """List of GS1 element strings."""

    def filter(
        self,
        *,
        ai: str | GS1ApplicationIdentifier | None = None,
        data_title: str | None = None,
    ) -> GS1ElementStrings:
        """Filter element strings by AI or data title.

        Args:
            ai: AI instance or string to match against the start of the
                element string's AI.
            data_title: String to find anywhere in the element string's AI
                data title.

        Returns:
            All matching element strings in the list.
        """
        if isinstance(ai, GS1ApplicationIdentifier):
            ai = ai.ai

        result = GS1ElementStrings()

        for element_string in self:
            ai_match = ai is not None and element_string.ai.ai.startswith(ai)
            data_title_match = (
                data_title is not None and data_title in element_string.ai.data_title
            )
            if ai_match or data_title_match:
                result.append(element_string)

        return result

    def get(
        self,
        *,
        ai: str | GS1ApplicationIdentifier | None = None,
        data_title: str | None = None,
    ) -> GS1ElementString | None:
        """Get element string by AI or data title.

        Args:
            ai: AI instance or string to match against the start of the
                element string's AI.
            data_title: String to find anywhere in the element string's AI
                data title.

        Returns:
            The first matching element string in the list.
        """
        matches = self.filter(ai=ai, data_title=data_title)
        return matches[0] if matches else None
