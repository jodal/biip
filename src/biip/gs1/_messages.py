"""GS1 messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from biip.gs1 import GS1ElementString


@dataclass
class GS1Message:
    """A GS1 message is the result of a single barcode scan.

    It may contain one or more GS1 Element Strings.
    """

    #: Raw unprocessed value.
    value: str

    #: List of Element Strings found in the message.
    element_strings: List[GS1ElementString]

    def as_hri(self: GS1Message) -> str:
        """Render as a human readable interpretation (HRI).

        The HRI is often printed directly below barcodes.

        Returns:
            A human-readable string where the AIs are wrapped in parenthesis.
        """
        return "".join(es.as_hri() for es in self.element_strings)
