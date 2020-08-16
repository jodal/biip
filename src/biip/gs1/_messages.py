"""GS1 messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Type

from biip.gs1 import GS1ElementString


@dataclass
class GS1Message:
    """A GS1 message is the result of a single barcode scan.

    It may contain one or more GS1 Element Strings.

    Example:
        See :mod:`biip.gs1` for a usage example.
    """

    #: Raw unprocessed value.
    value: str

    #: List of Element Strings found in the message.
    element_strings: List[GS1ElementString]

    @classmethod
    def parse(
        cls: Type[GS1Message], value: str, *, fnc1_char: Optional[str] = None
    ) -> GS1Message:
        """Parse a string from a barcode scan as a GS1 message with AIs.

        Args:
            value: The string to parse.
            fnc1_char: Character used in place of the FNC1 symbol. If not provided,
                parsing of variable-length fields in the middle of the message
                might greedily consume later fields.

        Returns:
            A message object with one or more element strings.

        """
        element_strings = []
        rest = value[:]

        while rest:
            element_string = GS1ElementString.extract(rest, fnc1_char=fnc1_char)
            element_strings.append(element_string)

            rest = rest[len(element_string) :]
            if fnc1_char is not None and rest.startswith(fnc1_char):
                rest = rest[1:]

        return cls(value=value, element_strings=element_strings)

    def as_hri(self: GS1Message) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        Returns:
            A human-readable string where the AIs are wrapped in parenthesis.
        """
        return "".join(es.as_hri() for es in self.element_strings)
