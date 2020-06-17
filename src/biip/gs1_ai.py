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
    def extract(
        cls: Type[GS1ApplicationIdentifier], value: str
    ) -> GS1ApplicationIdentifier:
        """Extract the GS1 Application Identifier (AI) from the given value.

        Args:
            value: The string to extract an AI from.

        Returns:
            ``GS1ApplicationIdentifier` with metadata on the AI.

        Raises:
            ParseError: If the parsing fails.
        """
        for application_identifier in _GS1_APPLICATION_IDENTIFIERS:
            if value.startswith(application_identifier.ai):
                return application_identifier

        raise ParseError(
            f"Failed to get GS1 Application Identifier from {value!r}."
        )


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
    pathlib.Path(__file__).parent / "gs1_ai.json"
)

_GS1_APPLICATION_IDENTIFIERS = [
    GS1ApplicationIdentifier(**kwargs)
    for kwargs in json.loads(_GS1_APPLICATION_IDENTIFIERS_FILE.read_text())
]
