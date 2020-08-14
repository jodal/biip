"""GS1 element strings."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from typing import List, Optional, Type

from biip import ParseError
from biip.gs1 import GS1ApplicationIdentifier


@dataclass
class GS1ElementString:
    """A GS1 Element String consists of a GS1 Application Identifier and its value."""

    #: The element's Application Identifier (AI).
    ai: GS1ApplicationIdentifier

    #: Raw data field of the Element String. Does not include the AI.
    value: str

    #: List of pattern groups extracted from the Element String.
    groups: List[str]

    #: A date created from the element string, if the AI represents a date.
    date: Optional[datetime.date] = None

    @classmethod
    def extract(cls: Type[GS1ElementString], value: str) -> GS1ElementString:
        """Extract the GS1 element string from the given value."""
        ai = GS1ApplicationIdentifier.extract(value)

        pattern = ai.pattern[:-1] if ai.pattern.endswith("$") else ai.pattern
        matches = re.match(pattern, value)
        if not matches:
            raise ParseError(
                f"Failed to match GS1 AI {ai.ai} pattern {ai.pattern!r} with {value!r}."
            )
        groups = list(matches.groups())
        value = "".join(groups)

        element = cls(ai=ai, value=value, groups=groups)
        element._set_date()

        return element

    def _set_date(self: GS1ElementString) -> None:
        if "(YYMMDD)" in self.ai.description:  # TODO: A more robust condition
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

        The HRI is often printed directly below barcodes.

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
    # References: See GS1 General Specifications, chapter 7.12.
    min_year = datetime.date.today().year - 49
    if result.year < min_year:
        result = result.replace(year=result.year + 100)

    return result
