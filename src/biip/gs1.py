"""Support for parsing of GS1-128 data."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from typing import List, Optional, Type

from biip import ParseError
from biip.gs1_ai import GS1ApplicationIdentifier


__all__ = ["GS1ApplicationIdentifier", "GS1Element", "GS1Message", "parse"]


@dataclass
class GS1Element:
    """A GS1 element string consists of a GS1 Application Identifier and its value."""

    ai: GS1ApplicationIdentifier
    value: str
    groups: List[str]

    # Extra fields that are populated for some AI
    date: Optional[datetime.date] = None

    @classmethod
    def extract(cls: Type[GS1Element], value: str) -> GS1Element:
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

    def _set_date(self: GS1Element) -> None:
        if "(YYMMDD)" in self.ai.description:  # TODO: A more robust condition
            try:
                self.date = datetime.datetime.strptime(
                    self.value, r"%y%m%d"
                ).date()
            except ValueError:
                raise ParseError(
                    f"Failed to parse GS1 AI {self.ai.ai} date from {self.value!r}."
                )

    def __len__(self: GS1Element) -> int:
        """Get the length of the element string."""
        return len(self.ai) + len(self.value)


@dataclass
class GS1Message:
    """A GS1 message is the result of a single barcode scan.

    It may contain one or more GS1 element strings.
    """

    value: str
    elements: List[GS1Element]


def parse(value: str) -> GS1Message:
    """Parse a GS1-128 barcode data string.

    Args:
        value: The string to parse.

    Returns:
        ``GS1Message`` with one or more ``GS1Element``.
    """
    elements = []
    rest = value[:]

    while rest:
        element = GS1Element.extract(rest)
        elements.append(element)
        rest = rest[len(element) :]

    return GS1Message(value=value, elements=elements)
