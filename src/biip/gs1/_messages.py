"""GS1 messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Type

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHAR, GS1ElementString


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
        cls: Type[GS1Message],
        value: str,
        *,
        separator_char: str = DEFAULT_SEPARATOR_CHAR,
    ) -> GS1Message:
        """Parse a string from a barcode scan as a GS1 message with AIs.

        Args:
            value: The string to parse.
            separator_char: Character used in place of the FNC1 symbol.
                Defaults to `<GS>` (ASCII value 29).
                If variable-length fields in the middle of the message are
                not terminated with this character, the parser might greedily
                consume the rest of the message.

        Returns:
            A message object with one or more element strings.

        Raises:
            ParseError: If a fixed-length field ends with a separator character.
        """
        element_strings = []
        rest = value[:]

        while rest:
            element_string = GS1ElementString.extract(
                rest, separator_char=separator_char
            )
            element_strings.append(element_string)

            rest = rest[len(element_string) :]

            if rest.startswith(separator_char):
                if element_string.ai.fnc1_required:
                    rest = rest[1:]
                else:
                    raise ParseError(
                        f"Element String {element_string.as_hri()!r} has fixed length "
                        "and should not end with a separator character. "
                        f"Separator character {separator_char!r} found in {value!r}."
                    )

        return cls(value=value, element_strings=element_strings)

    def as_hri(self: GS1Message) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        Returns:
            A human-readable string where the AIs are wrapped in parenthesis.
        """
        return "".join(es.as_hri() for es in self.element_strings)
