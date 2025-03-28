"""GS1 messages."""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import chain

from biip import ParseError
from biip._parser import ParseConfig
from biip.gs1_application_identifiers import (
    _GS1_APPLICATION_IDENTIFIERS,
    GS1ApplicationIdentifier,
)
from biip.gs1_messages import GS1ElementString


@dataclass
class GS1Message:
    """A GS1 message is the result of a single barcode scan.

    It may contain one or more GS1 Element Strings.

    Examples:
        See `biip.gs1_messages` for a usage example.
    """

    value: str
    """Raw unprocessed value."""

    element_strings: list[GS1ElementString]
    """List of Element Strings found in the message."""

    @classmethod
    def parse(
        cls,
        value: str,
        *,
        config: ParseConfig | None = None,
    ) -> GS1Message:
        """Parse a string from a barcode scan as a GS1 message with AIs.

        Args:
            value: The string to parse.
            config: Configuration options for parsing.

        Returns:
            A message object with one or more element strings.

        Raises:
            ValueError: If the `separator_char` isn't exactly 1 character long.
            ParseError: If the parsing fails.
        """
        if config is None:
            config = ParseConfig()

        value = value.strip()
        element_strings: list[GS1ElementString] = []
        rest = value[:]

        while rest:
            element_string = GS1ElementString.extract(rest, config=config)
            element_strings.append(element_string)

            rest = rest[len(element_string) :]

            # Separator characters are accepted inbetween any element string,
            # even if the AI doesn't require it. See GS1 General Specifications,
            # section 7.8.6 for details.
            while rest.startswith(tuple(config.separator_chars)):
                rest = rest[1:]

        return cls(value=value, element_strings=element_strings)

    @classmethod
    def parse_hri(
        cls,
        value: str,
        *,
        config: ParseConfig | None = None,
    ) -> GS1Message:
        """Parse the GS1 string given in HRI (human readable interpretation) format.

        Args:
            value: The HRI string to parse.
            config: Configuration options for parsing.

        Returns:
            A message object with one or more element strings.

        Raises:
            ParseError: If parsing of the data fails.
        """
        if config is None:
            config = ParseConfig()

        value = value.strip()
        if not value.startswith("("):
            msg = f"Expected HRI string {value!r} to start with a parenthesis."
            raise ParseError(msg)

        pattern = r"\((\d+)\)(\w+)"
        matches: list[tuple[str, str]] = re.findall(pattern, value)
        if not matches:
            msg = (
                f"Could not find any GS1 Application Identifiers in {value!r}. "
                "Expected format: '(AI)DATA(AI)DATA'."
            )
            raise ParseError(msg)

        pairs: list[tuple[GS1ApplicationIdentifier, str]] = []
        for ai_number, ai_data in matches:
            if ai_number not in _GS1_APPLICATION_IDENTIFIERS:
                msg = f"Unknown GS1 Application Identifier {ai_number!r} in {value!r}."
                raise ParseError(msg)
            pairs.append((_GS1_APPLICATION_IDENTIFIERS[ai_number], ai_data))

        parts = chain(
            *[
                [
                    gs1_ai.ai,
                    ai_data,
                    ("\x1d" if gs1_ai.separator_required else ""),
                ]
                for gs1_ai, ai_data in pairs
            ]
        )
        normalized_string = "".join(parts)
        return GS1Message.parse(normalized_string, config=config)

    def as_hri(self) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        Returns:
            A human-readable string where the AIs are wrapped in parenthesis.
        """
        return "".join(es.as_hri() for es in self.element_strings)

    def filter(
        self,
        *,
        ai: str | GS1ApplicationIdentifier | None = None,
        data_title: str | None = None,
    ) -> list[GS1ElementString]:
        """Filter Element Strings by AI or data title.

        Args:
            ai: AI instance or string to match against the start of the
                Element String's AI.
            data_title: String to find anywhere in the Element String's AI
                data title.

        Returns:
            All matching Element Strings in the message.
        """
        if isinstance(ai, GS1ApplicationIdentifier):
            ai = ai.ai

        result: list[GS1ElementString] = []

        for element_string in self.element_strings:
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
        """Get Element String by AI or data title.

        Args:
            ai: AI instance or string to match against the start of the
                Element String's AI.
            data_title: String to find anywhere in the Element String's AI
                data title.

        Returns:
            The first matching Element String in the message.
        """
        matches = self.filter(ai=ai, data_title=data_title)
        return matches[0] if matches else None
