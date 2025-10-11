"""Support for prefixes allocated by GS1.

GS1 prefixes are used to split the allocation space of various number schemes,
e.g. GTIN, GLN, and SSCC.

The allocation space is split twice:

- First, among the national GS1 organizations, represented by
  [`GS1Prefix`][biip.gs1_prefixes.GS1Prefix].
- Secondly, among the companies that apply to their national GS1 organization
  for a number allocation, represented by
  [`GS1CompanyPrefix`][biip.gs1_prefixes.GS1CompanyPrefix].

All prefix data is bundled with Biip. No network access is required.

Examples:
    >>> from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix
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
from typing import Union

from biip import ParseError

__all__ = [
    "GS1CompanyPrefix",
    "GS1Prefix",
]

_PrefixTrieNode = Union[dict[str, "_PrefixTrieNode"], tuple[int, str]]  # noqa: UP007
_CompanyPrefixTrieNode = Union[dict[str, "_CompanyPrefixTrieNode"], int]  # noqa: UP007


@dataclass(frozen=True)
class GS1Prefix:
    """Prefix assigned by GS1.

    Used to split the allocation space of various number schemes, e.g. GTIN,
    GLN, and SSCC, among GS1 organizations worldwide.

    The GS1 Prefix does not identify the origin of a product, only where the
    number was assigned to a GS1 member organization.

    References:
        https://www.gs1.org/standards/id-keys/company-prefix

    Examples:
        >>> from biip.gs1_prefixes import GS1Prefix
        >>> GS1Prefix.extract("9781492053743")
        GS1Prefix(value='978', usage='Bookland (ISBN)')
    """

    value: str
    """The prefix itself."""

    usage: str
    """Description of who is using the prefix."""

    @classmethod
    def extract(cls, value: str) -> GS1Prefix | None:
        """Extract the GS1 Prefix from the given value.

        Args:
            value: The string to extract a GS1 Prefix from.

        Returns:
            Metadata about the extracted prefix, or `None` if the prefix is unknown.

        Raises:
            ParseError: If the parsing fails.
        """
        if not value.isdecimal():
            msg = f"Failed to get GS1 Prefix from {value!r}."
            raise ParseError(msg)

        node = _GS1_PREFIX_TRIE
        digits = list(value)

        while digits:
            digit = digits.pop(0)

            assert isinstance(node, dict)
            if digit not in node:
                # Prefix is undefined.
                return None
            node = node[digit]

            if isinstance(node, list):
                length, usage = node
                return cls(value=value[:length], usage=usage)

        return None


@dataclass(frozen=True)
class GS18Prefix:
    """GS1-8 Prefix assigned by GS1.

    This prefix is specifically for GTIN-8 numbers.

    The GS1-8 Prefix does not identify the origin of a product, only where the
    number was assigned to a GS1 member organization.

    References:
        GS1 General Specifications, section 1.4.3

    Examples:
        >>> from biip.gs1_prefixes import GS18Prefix
        >>> GS1Prefix.extract("30056640")
        GS1Prefix(value='300', usage='GS1 France')
    """

    value: str
    """The prefix itself."""

    usage: str
    """Description of who is using the prefix."""

    @classmethod
    def extract(cls, value: str) -> GS18Prefix | None:
        """Extract the GS1-8 Prefix from the given value.

        Args:
            value: The string to extract a GS1-8 Prefix from.

        Returns:
            Metadata about the extracted prefix, or `None` if the prefix is unknown.

        Raises:
            ParseError: If the parsing fails.
        """
        if not value.isdecimal():
            msg = f"Failed to get GS1-8 Prefix from {value!r}."
            raise ParseError(msg)

        if len(value) < 3:
            return None

        prefix = value[:3]
        int_prefix = int(prefix)

        if (0 <= int_prefix <= 99) or (200 <= int_prefix <= 299):
            return cls(
                value=prefix,
                usage="Used to issue Restricted Circulation Numbers within a company",
            )

        if (100 <= int_prefix <= 199) or (300 <= int_prefix <= 976):
            # Use the regular GS1 prefix table for these
            gs1_prefix = GS1Prefix.extract(value)
            if gs1_prefix is None:
                return None
            return GS18Prefix(value=prefix, usage=gs1_prefix.usage)

        if 977 <= int_prefix <= 999:
            return cls(value=prefix, usage="Reserved for future use")

        return None  # pragma: no cover


@dataclass(frozen=True)
class GS1CompanyPrefix:
    """Company prefix assigned by GS1.

    The prefix assigned to a single company.

    Examples:
        >>> from biip.gs1_prefixes import GS1CompanyPrefix
        >>> GS1CompanyPrefix.extract("7044610873466")
        GS1CompanyPrefix(value='704461')
    """

    value: str
    """The company prefix itself."""

    @classmethod
    def extract(cls, value: str) -> GS1CompanyPrefix | None:
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


_GS1_PREFIX_TRIE_FILE = (
    resources.files("biip") / "gs1_prefixes" / "_prefix_trie.json.lzma"
)
_GS1_PREFIX_TRIE: _PrefixTrieNode = json.loads(
    lzma.decompress(_GS1_PREFIX_TRIE_FILE.read_bytes()).decode()
)

_GS1_COMPANY_PREFIX_TRIE_FILE = (
    resources.files("biip") / "gs1_prefixes" / "_company_prefix_trie.json.lzma"
)
_GS1_COMPANY_PREFIX_TRIE: _CompanyPrefixTrieNode = json.loads(
    lzma.decompress(_GS1_COMPANY_PREFIX_TRIE_FILE.read_bytes()).decode()
)
