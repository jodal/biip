"""Application Identifiers specified by GS1."""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Optional, Type

from biip import ParseError


@dataclass
class GS1ApplicationIdentifier:
    """Application Identifier assigned by GS1.

    Source: https://www.gs1.org/standards/barcodes/application-identifiers
    """

    ai: str
    description: str
    data_title: str
    fnc1_required: bool
    format: str
    pattern: str

    @classmethod
    def get(
        cls: Type[GS1ApplicationIdentifier], value: str
    ) -> GS1ApplicationIdentifier:
        """Lookup the given GS1 Application Identifier (AI).

        Args:
            value: The AI code, e.g. "01".

        Returns:
            ``GS1ApplicationIdentifier`` with metadata on the AI.

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
            ``GS1ApplicationIdentifier` with metadata on the AI.

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


def get_predefined_length(value: str) -> Optional[int]:
    """Get predefined length of element string, including Application Identifier prefix.

    Args:
        value: Any string starting with a GS1 Application Identifier.

    Returns:
        Predefined length or ``None`` if undefined.
    """
    ai_prefix = value[:2]
    return {
        "00": 20,
        "01": 16,
        "02": 16,
        "03": 16,
        "04": 18,
        "11": 8,
        "12": 8,
        "13": 8,
        "14": 8,
        "15": 8,
        "16": 8,
        "17": 8,
        "18": 8,
        "19": 8,
        "20": 4,
        "31": 10,
        "32": 10,
        "33": 10,
        "34": 10,
        "35": 10,
        "36": 10,
        "41": 16,
    }.get(ai_prefix)


_GS1_APPLICATION_IDENTIFIERS_FILE = (
    pathlib.Path(__file__).parent / "_application_identifiers.json"
)

_GS1_APPLICATION_IDENTIFIERS = [
    GS1ApplicationIdentifier(**kwargs)
    for kwargs in json.loads(_GS1_APPLICATION_IDENTIFIERS_FILE.read_text())
]
