"""Prefixes allocated by GS1.

Example:
    >>> from biip.gs1 import GS1CompanyPrefix, GS1Prefix
    >>> GS1Prefix.extract("7044610873466")
    GS1Prefix(value='704', usage='GS1 Norway')
    >>> GS1CompanyPrefix.extract("7044610873466")
    GS1CompanyPrefix(value='704461')
"""

from __future__ import annotations

import json
import lzma
from dataclasses import dataclass
from importlib import resources
from typing import Dict, Optional, Union

from biip import ParseError

_TrieNode = Union[Dict[str, "_TrieNode"], int]


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
    def extract(cls, value: str) -> Optional[GS1Prefix]:
        """Extract the GS1 Prefix from the given value.

        Args:
            value: The string to extract a GS1 Prefix from.

        Returns:
            Metadata about the extracted prefix, or `None` if the prefix is unknown.

        Raises:
            ParseError: If the parsing fails.
        """
        prefix = ""

        for prefix_range in _GS1_PREFIX_RANGES:
            prefix = value[: prefix_range.length]

            if not prefix.isdecimal():
                continue
            number = int(prefix)

            if prefix_range.min_value <= number <= prefix_range.max_value:
                return cls(value=prefix, usage=prefix_range.usage)

        if not prefix.isdecimal():
            # `prefix` is now the shortest prefix possible, and should be
            # numeric even if the prefix assignment is unknown.
            msg = f"Failed to get GS1 Prefix from {value!r}."
            raise ParseError(msg)

        return None


@dataclass(frozen=True)
class GS1CompanyPrefix:
    """Company prefix assigned by GS1.

    The prefix assigned to a single company.

    Example:
        >>> from biip.gs1 import GS1CompanyPrefix
        >>> GS1CompanyPrefix.extract("7044610873466")
        GS1CompanyPrefix(value='704461')
    """

    #: The company prefix itself.
    value: str

    @classmethod
    def extract(cls, value: str) -> Optional[GS1CompanyPrefix]:
        """Extract the GS1 Company Prefix from the given value.

        Args:
            value: The string to extract a GS1 Company Prefix from.
                The value is typically a GLN, GTIN, or an SSCC.

        Returns:
            Metadata about the extracted prefix, or `None` if the prefix is unknown.

        Raises:
            ParseError: If the parsing fails.
        """
        if not value.isdecimal():
            msg = f"Failed to get GS1 Company Prefix from {value!r}."
            raise ParseError(msg)

        node = _GS1_COMPANY_PREFIX_TRIE
        digits = list(value)

        while digits:
            digit = digits.pop(0)

            assert isinstance(node, dict)
            if digit not in node:
                # Prefix is undefined.
                return None
            node = node[digit]

            if isinstance(node, int):
                if node == 0:
                    # Prefix is defined, but has zero length.
                    return None
                return cls(value=value[:node])

        return None


@dataclass(frozen=True)
class _GS1PrefixRange:
    length: int
    min_value: int
    max_value: int
    usage: str


def _load_prefix_ranges():
    with resources.open_text(__package__, '_prefix_ranges.json') as f:
        data = json.load(f)
    return [_GS1PrefixRange(**kwargs) for kwargs in data]

_GS1_PREFIX_RANGES = _load_prefix_ranges()

def _load_company_prefix_trie():
    with resources.open_binary(__package__, '_company_prefix_trie.json.lzma') as compressed_file:
        decompressed_data = lzma.decompress(compressed_file.read())
        data = json.loads(decompressed_data.decode('utf-8'))
    return data

_GS1_COMPANY_PREFIX_TRIE: _TrieNode = _load_company_prefix_trie()
