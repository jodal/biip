"""GS1 Application Identifiers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources

from biip import ParseError


@dataclass(frozen=True)
class GS1ApplicationIdentifier:
    r"""GS1 Application Identifier (AI).

    AIs are data field prefixes used in several types of barcodes, including
    GS1-128. The AI defines what semantical meaning and format of the following
    data field.

    AIs standardize how to include e.g. product weight, expiration dates,
    and lot numbers in barcodes.

    References:
        https://www.gs1.org/standards/barcodes/application-identifiers

    Example:
        >>> from biip.gs1 import GS1ApplicationIdentifier
        >>> ai = GS1ApplicationIdentifier.extract("01")
        >>> ai
        GS1ApplicationIdentifier(ai='01', description='Global Trade Item
        Number (GTIN)', data_title='GTIN', fnc1_required=False,
        format='N2+N14')
        >>> ai.pattern
        '^01(\\d{14})$'
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
    def extract(cls, value: str) -> GS1ApplicationIdentifier:
        """Extract the GS1 Application Identifier (AI) from the given value.

        Args:
            value: The string to extract an AI from.

        Returns:
            Metadata about the extracted AI.

        Raises:
            ParseError: If the parsing fails.

        Example:
            >>> from biip.gs1 import GS1ApplicationIdentifier
            >>> GS1ApplicationIdentifier.extract("010703206980498815210526100329")
            GS1ApplicationIdentifier(ai='01', description='Global Trade Item
            Number (GTIN)', data_title='GTIN', fnc1_required=False,
            format='N2+N14')
        """
        for application_identifier in _GS1_APPLICATION_IDENTIFIERS.values():
            if value.startswith(application_identifier.ai):
                return application_identifier

        msg = f"Failed to get GS1 Application Identifier from {value!r}."
        raise ParseError(msg)

    def __len__(self) -> int:
        """Get the length of the Application Identifier code."""
        return len(self.ai)

    def __str__(self) -> str:
        """Get the string representation of the Application Identifier."""
        return f"({self.ai})"


def _load_application_identifiers():
    with resources.open_text(__package__, '_application_identifiers.json') as f:
        data = json.load(f)
    return {
        entry['ai']: GS1ApplicationIdentifier(**entry)
        for entry in data
    }

_GS1_APPLICATION_IDENTIFIERS = _load_application_identifiers()
