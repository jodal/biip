"""Application Identifiers specified by GS1."""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Type

from biip import ParseError


@dataclass
class GS1ApplicationIdentifier:
    """Application Identifier assigned by GS1.

    Source: https://www.gs1.org/standards/barcodes/application-identifiers
    """

    #: The Application Identifier (AI) itself.
    ai: str

    #: Description of the AIs use.
    description: str

    #: Commonly used label/abbreviation for the AI.
    data_title: str

    #: Whether a FNC1 character is required after element strings of this type.
    #: This is the case for all AIs that have a variable length.
    fnc1_required: bool

    #: Human readable format of the AIs element string.
    format: str

    #: Regular expression for parsing the AIs element string.
    pattern: str = field(repr=False)

    @classmethod
    def get(
        cls: Type[GS1ApplicationIdentifier], value: str
    ) -> GS1ApplicationIdentifier:
        """Lookup the given GS1 Application Identifier (AI).

        Args:
            value: The AI code, e.g. "01".

        Returns:
            Metadata about the given AI.

        Raises:
            KeyError: If the given AI is not found.
        """
        for application_identifier in _GS1_APPLICATION_IDENTIFIERS:
            if application_identifier.ai == value:
                return application_identifier
        raise KeyError(value)

    @classmethod
    def extract(
        cls: Type[GS1ApplicationIdentifier], value: str
    ) -> GS1ApplicationIdentifier:
        """Extract the GS1 Application Identifier (AI) from the given value.

        Args:
            value: The string to extract an AI from.

        Returns:
            Metadata about the extracted AI.

        Raises:
            TypeError: If the input isn't str or bytes.
            ParseError: If the parsing fails.
        """
        if isinstance(value, str):
            data = value.encode()
        elif isinstance(value, bytes):
            data = value
        else:
            raise TypeError(f"Expected str or bytes, got {type(value)}.")

        for application_identifier in _GS1_APPLICATION_IDENTIFIERS:
            if data.startswith(application_identifier.ai.encode()):
                return application_identifier

        raise ParseError(
            f"Failed to get GS1 Application Identifier from {value!r}."
        )

    def __len__(self: GS1ApplicationIdentifier) -> int:
        """Get the length of the Application Identifier code."""
        return len(self.ai)


_GS1_APPLICATION_IDENTIFIERS_FILE = (
    pathlib.Path(__file__).parent / "_application_identifiers.json"
)

_GS1_APPLICATION_IDENTIFIERS = [
    GS1ApplicationIdentifier(**kwargs)
    for kwargs in json.loads(_GS1_APPLICATION_IDENTIFIERS_FILE.read_text())
]
