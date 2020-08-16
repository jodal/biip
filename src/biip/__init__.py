"""Biip interprets the data in barcodes.

Example:
    >>> from biip import parse
    >>> parse("96385074")
    Gtin(value='96385074', format=GtinFormat.GTIN_8,
    prefix=GS1Prefix(value='963', usage='Global Office - GTIN-8'),
    payload='9638507', check_digit=4, packaging_level=None)
    >>> parse("15210526")
    GS1Message(value='15210526',
    element_strings=[GS1ElementString(ai=GS1ApplicationIdentifier(ai='15',
    description='Best before date (YYMMDD)', data_title='BEST BEFORE or BEST BY',
    fnc1_required=False, format='N2+N6'), value='210526',
    pattern_groups=['210526'], gtin=None, date=datetime.date(2021, 5, 26))])
    >>> parse("123")
    Traceback (most recent call last):
        ...
    biip._exceptions.ParseError: Failed to parse '123' as GTIN or GS1 Element String.
"""

from __future__ import annotations


try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

from biip._exceptions import BiipException, EncodeError, ParseError
from biip._parser import parse


__all__ = [
    "parse",
    "BiipException",
    "EncodeError",
    "ParseError",
]


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
