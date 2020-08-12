"""GS1 element strings."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from typing import List, Optional, Type

from biip import ParseError
from biip.gs1 import GS1ApplicationIdentifier


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
