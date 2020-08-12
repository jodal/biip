"""GS1 messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from biip.gs1 import GS1Element


@dataclass
class GS1Message:
    """A GS1 message is the result of a single barcode scan.

    It may contain one or more GS1 element strings.
    """

    value: str
    elements: List[GS1Element]
