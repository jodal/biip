"""Barcode prefixes allocated by GS1."""

import json
import pathlib
from dataclasses import dataclass
from typing import Type

from biip import ParseError


@dataclass(frozen=True)
class GS1Prefix:
    """Prefix assigned by GS1.

    Used to split the allocation space of various number schemes, e.g. GTIN,
    among GS1 organizations worldwide.

    The GS1 Prefix does not identify the origin of a product, only where the
    number was assigned to a GS1 member organization.

    References:
        https://www.gs1.org/standards/id-keys/company-prefix

    Example:
        >>> from biip.gs1 import GS1Prefix
        >>> GS1Prefix.extract("978-1-492-05374-3")
        GS1Prefix(value='978', usage='Bookland (ISBN)')
    """

    #: The prefix itself.
    value: str

    #: Description of who is using the prefix.
    usage: str

    @classmethod
    def extract(cls: Type["GS1Prefix"], value: str) -> "GS1Prefix":
        """Extract the GS1 Prefix from the given value.

        Args:
            value: The string to extract a GS1 Prefix from.

        Returns:
            Metadata about the extracted prefix.

        Raises:
            ParseError: If the parsing fails.
        """
        for prefix_range in _GS1_PREFIX_RANGES:
            prefix = value[: prefix_range.length]

            if not prefix.isnumeric():
                continue
            number = int(prefix)

            if prefix_range.min_value <= number <= prefix_range.max_value:
                return cls(value=prefix, usage=prefix_range.usage)

        raise ParseError(f"Failed to get GS1 Prefix from {value!r}.")


@dataclass(frozen=True)
class _GS1PrefixRange:
    length: int
    min_value: int
    max_value: int
    usage: str


_GS1_PREFIX_RANGES_FILE = pathlib.Path(__file__).parent / "_prefix_ranges.json"

_GS1_PREFIX_RANGES = [
    _GS1PrefixRange(**kwargs)
    for kwargs in json.loads(_GS1_PREFIX_RANGES_FILE.read_text())
]
