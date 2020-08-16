"""GS1 Element Strings."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from typing import List, Optional, Type

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHAR, GS1ApplicationIdentifier
from biip.gtin import Gtin


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
        packaging_level=None), date=None)
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

    #: A date created from the element string, if the AI represents a date.
    date: Optional[datetime.date] = None

    @classmethod
    def extract(
        cls: Type[GS1ElementString],
        value: str,
        *,
        separator_char: str = DEFAULT_SEPARATOR_CHAR,
    ) -> GS1ElementString:
        """Extract the first GS1 Element String from the given value.

        Args:
            value: The string to extract an Element String from. May contain
                more than one Element String.
            separator_char: Character used in place of the FNC1 symbol.
                Defaults to `<GS>` (ASCII value 29).
                If variable-length fields are not terminated with this
                character, the parser might greedily consume later fields.

        Returns:
            A data class with the Element String's parts and data extracted from it.

        Raises:
            ValueError: If the ``separator_char`` isn't exactly 1 character long.
            ParseError: If the parsing fails.
        """
        if len(separator_char) != 1:
            raise ValueError("separator_char must be exactly 1 character long.")

        ai = GS1ApplicationIdentifier.extract(value)
        value = value.split(separator_char, maxsplit=1)[0]

        pattern = ai.pattern[:-1] if ai.pattern.endswith("$") else ai.pattern
        matches = re.match(pattern, value)
        if not matches:
            raise ParseError(
                f"Failed to match GS1 AI {ai.ai} pattern {ai.pattern!r} with {value!r}."
            )
        pattern_groups = list(matches.groups())
        value = "".join(pattern_groups)

        element = cls(ai=ai, value=value, pattern_groups=pattern_groups)
        element._set_Gtin()
        element._set_date()

        return element

    def _set_Gtin(self: GS1ElementString) -> None:
        if self.ai.ai not in ("01", "02"):
            return

        self.gtin = Gtin.parse(self.value)

    def _set_date(self: GS1ElementString) -> None:
        if (
            "(YYMMDD)" not in self.ai.description
        ):  # TODO: A more robust condition
            return

        try:
            self.date = _parse_date(self.value)
        except ValueError:
            raise ParseError(
                f"Failed to parse GS1 AI {self.ai.ai} date from {self.value!r}."
            )

    def __len__(self: GS1ElementString) -> int:
        """Get the length of the element string."""
        return len(self.ai) + len(self.value)

    def as_hri(self: GS1ElementString) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below the barcode.

        Returns:
            A human-readable string where the AI is wrapped in parenthesis.
        """
        return f"({self.ai.ai}){self.value}"


def _parse_date(value: str) -> datetime.date:
    # TODO Handle date being zero, ref chapter 3.4.2.

    result = datetime.datetime.strptime(value, r"%y%m%d").date()

    # The two-digit year refers to a year in the range between 49 years past
    # and 50 years into the future. However, Python uses 1969 as the pivot
    # point when selecting the century, so we must adjust all dates that are
    # interpreted as more than 49 years ago.
    #
    # References: GS1 General Specifications, chapter 7.12.
    min_year = datetime.date.today().year - 49
    if result.year < min_year:
        result = result.replace(year=result.year + 100)

    return result
