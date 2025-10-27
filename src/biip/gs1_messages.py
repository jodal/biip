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
            item_reference='980498',
            payload='703206980498',
            check_digit=8
        )
    )

The `element_strings` attribute has
[`element_strings.get()`][biip.gs1_element_strings.GS1ElementStrings.get] and
[`element_strings.filter()`][biip.gs1_element_strings.GS1ElementStrings.filter]
methods to lookup element strings either by the Application Identifier's "data
title" or its AI number.

    >>> pprint(msg.element_strings.get(data_title='BEST BY'))
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
    >>> pprint(msg.element_strings.get(ai="10"))
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
from typing import TYPE_CHECKING

from biip import ParseError
from biip._parser import ParseConfig
from biip.gs1_application_identifiers import _GS1_APPLICATION_IDENTIFIERS
from biip.gs1_element_strings import GS1ElementString, GS1ElementStrings

if TYPE_CHECKING:
    from biip.gs1_digital_link_uris import GS1DigitalLinkURI


@dataclass(frozen=True)
class GS1Message:
    """A GS1 message is the result of a single barcode scan.

    It may contain one or more GS1 element strings.

    Examples:
        See `biip.gs1_messages` for a usage example.
    """

    value: str
    """Raw unprocessed value."""

    element_strings: GS1ElementStrings
    """List of element strings found in the message.

    See [`GS1ElementStrings`][biip.gs1_element_strings.GS1ElementStrings] for
    methods to extract interesting element strings from the list.
    """

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
        element_strings = GS1ElementStrings()
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
    def from_element_strings(cls, element_strings: GS1ElementStrings) -> GS1Message:
        """Create a GS1 message from a list of element strings.

        Args:
            element_strings: A list of GS1 element strings.

        Returns:
            GS1Message: The created GS1 message.
        """
        parts = chain(
            *[
                [
                    es.ai.ai,
                    es.value,
                    ("\x1d" if es.ai.separator_required else ""),
                ]
                for es in element_strings
            ]
        )
        normalized_string = "".join(parts).removesuffix("\x1d")
        return cls(value=normalized_string, element_strings=element_strings)

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

        element_strings = GS1ElementStrings()
        for ai_number, ai_data in matches:
            if ai_number not in _GS1_APPLICATION_IDENTIFIERS:
                msg = f"Unknown GS1 Application Identifier {ai_number!r} in {value!r}."
                raise ParseError(msg)
            element_strings.append(
                GS1ElementString.extract(f"{ai_number}{ai_data}", config=config)
            )

        return GS1Message.from_element_strings(element_strings)

    def as_hri(self) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        Returns:
            A human-readable string where the AIs are wrapped in parenthesis.
        """
        return "".join(es.as_hri() for es in self.element_strings)

    def as_gs1_digital_link_uri(self) -> GS1DigitalLinkURI:
        """Convert to a GS1 Digital Link URI."""
        from biip.gs1_digital_link_uris import GS1DigitalLinkURI  # noqa: PLC0415

        return GS1DigitalLinkURI.from_element_strings(self.element_strings)
