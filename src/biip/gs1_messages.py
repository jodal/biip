"""Support for barcode data with GS1 messages.

The `biip.gs1_messages` module contains Biip's support for parsing data
consisting of GS1 messages and element strings. GS1 messages are text strings
consisting of one or more GS1 element strings. Each GS1 Element String is
identified by a GS1 Application Identifier (AI) prefix followed by the element's
value.

Data of this format is found in the following types of barcodes:

- [GS1-128](https://en.wikipedia.org/wiki/Code_128)
- [GS1 DataBar](https://en.wikipedia.org/wiki/GS1_DataBar_Coupon)
- [GS1 DataMatrix](https://en.wikipedia.org/wiki/Data_Matrix)
- [GS1 QR Code](https://en.wikipedia.org/wiki/QR_code)

If you only want to parse GS1 Messages, you can import the GS1 Message parser
directly instead of using [`biip.parse()`][biip.parse].

    >>> from biip.gs1_messages import GS1Message

If the parsing succeeds, it returns a [`GS1Message`][biip.gs1_messages.GS1Message]
object.

    >>> msg = GS1Message.parse("010703206980498815210526100329")

The [`GS1Message`][biip.gs1_messages.GS1Message] can be represented as an HRI,
short for "human readable interpretation", using
[`msg.as_hri()`][biip.gs1_messages.GS1Message.as_hri]. The HRI is the text
usually printed below or next to the barcode.

    >>> msg.value
    '010703206980498815210526100329'
    >>> msg.as_hri()
    '(01)07032069804988(15)210526(10)0329'

HRI can also be parsed using
[`GS1Message.parse_hri()`][biip.gs1_messages.GS1Message.parse_hri].

    >>> msg = GS1Message.parse_hri("(01)07032069804988(15)210526(10)0329")

A message can contain multiple element strings.

    >>> len(msg.element_strings)
    3

In this example, the first element string is a GTIN.

    >>> pprint(msg.element_strings[0])
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

The message object has [`msg.get()`][biip.gs1_messages.GS1Message.get] and
[`msg.filter()`][biip.gs1_messages.GS1Message.filter] methods to lookup element
strings either by the Application Identifier's "data title" or its AI number.

    >>> pprint(msg.get(data_title='BEST BY'))
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='15',
            description='Best before date (YYMMDD)',
            data_title='BEST BEFORE or BEST BY',
            separator_required=False,
            format='N2+N6'
        ),
        value='210526',
        pattern_groups=[
            '210526'
        ],
        date=datetime.date(2021, 5, 26)
    )
    >>> pprint(msg.get(ai="10"))
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='10',
            description='Batch or lot number',
            data_title='BATCH/LOT',
            separator_required=True,
            format='N2+X..20'
        ),
        value='0329',
        pattern_groups=[
            '0329'
        ]
    )
"""

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
from biip.gs1_element_strings import GS1ElementString


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
