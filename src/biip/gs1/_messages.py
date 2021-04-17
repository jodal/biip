"""GS1 messages."""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Type, Union

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHARS, GS1ApplicationIdentifier, GS1ElementString
from biip.gtin import RcnRegion


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
        cls: Type["GS1Message"],
        value: str,
        *,
        rcn_region: Optional[RcnRegion] = None,
        separator_chars: Iterable[str] = DEFAULT_SEPARATOR_CHARS,
    ) -> "GS1Message":
        """Parse a string from a barcode scan as a GS1 message with AIs.

        Args:
            value: The string to parse.
            rcn_region: The geographical region whose rules should be used to
                interpret Restricted Circulation Numbers (RCN).
                Needed to extract e.g. variable weight/price from GTIN.
            separator_chars: Characters used in place of the FNC1 symbol.
                Defaults to `<GS>` (ASCII value 29).
                If variable-length fields in the middle of the message are
                not terminated with a separator character, the parser might
                greedily consume the rest of the message.

        Returns:
            A message object with one or more element strings.

        Raises:
            ParseError: If a fixed-length field ends with a separator character.
        """
        value = value.strip()
        element_strings = []
        rest = value[:]

        while rest:
            element_string = GS1ElementString.extract(
                rest, rcn_region=rcn_region, separator_chars=separator_chars
            )
            element_strings.append(element_string)

            rest = rest[len(element_string) :]

            if rest.startswith(tuple(separator_chars)):
                if element_string.ai.fnc1_required:
                    rest = rest[1:]
                else:
                    separator_char = rest[0]
                    raise ParseError(
                        f"Element String {element_string.as_hri()!r} has fixed length "
                        "and should not end with a separator character. "
                        f"Separator character {separator_char!r} found in {value!r}."
                    )

        return cls(value=value, element_strings=element_strings)

    def as_hri(self: "GS1Message") -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        Returns:
            A human-readable string where the AIs are wrapped in parenthesis.
        """
        return "".join(es.as_hri() for es in self.element_strings)

    def filter(
        self: "GS1Message",
        *,
        ai: Optional[Union[str, GS1ApplicationIdentifier]] = None,
        data_title: Optional[str] = None,
    ) -> List[GS1ElementString]:
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

        result = []

        for element_string in self.element_strings:
            if ai is not None and element_string.ai.ai.startswith(ai):
                result.append(element_string)
            elif data_title is not None and data_title in element_string.ai.data_title:
                result.append(element_string)

        return result

    def get(
        self: "GS1Message",
        *,
        ai: Optional[Union[str, GS1ApplicationIdentifier]] = None,
        data_title: Optional[str] = None,
    ) -> Optional[GS1ElementString]:
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
