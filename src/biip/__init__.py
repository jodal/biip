r"""Biip interprets the data in barcodes.

    >>> import biip

An ambiguous value may be interpreted as different formats. In the following
example, the value can be interpreted as either a GTIN or a GS1 Message.

    >>> result = biip.parse("96385074")
    >>> result.gtin
    Gtin(value='96385074', format=GtinFormat.GTIN_8,
    prefix=GS1Prefix(value='00009', usage='GS1 US'), payload='9638507',
    check_digit=4, packaging_level=None)
    >>> result.gs1_message
    GS1Message(value='96385074',
    element_strings=[GS1ElementString(ai=GS1ApplicationIdentifier(ai='96',
    description='Company internal information', data_title='INTERNAL',
    fnc1_required=True, format='N2+X..90'), value='385074',
    pattern_groups=['385074'], gtin=None, sscc=None, date=None, decimal=None,
    money=None)])

In the next example, the value is only valid as a GS1 Message and the GTIN
parser returns an error explaining why the value cannot be interpreted as a
GTIN. If a format includes check digits, Biip always control them and fail if
the check digits are incorrect.

    >>> result = biip.parse("15210527")
    >>> result.gtin
    None
    >>> result.gtin_error
    "Invalid GTIN check digit for '15210527': Expected 4, got 7."
    >>> result.gs1_message
    GS1Message(value='15210527',
    element_strings=[GS1ElementString(ai=GS1ApplicationIdentifier(ai='15',
    description='Best before date (YYMMDD)', data_title='BEST BEFORE or BEST
    BY', fnc1_required=False, format='N2+N6'), value='210527',
    pattern_groups=['210527'], gtin=None, sscc=None, date=datetime.date(2021,
    5, 27), decimal=None, money=None)])

If a value cannot be interpreted as any supported format, an exception is
raised with a reason from each parser.

    >>> biip.parse("123")
    Traceback (most recent call last):
        ...
    biip._exceptions.ParseError: Failed to parse '123':
    - GTIN: Failed to parse '123' as GTIN: Expected 8, 12, 13, or 14 digits, got 3.
    - UPC: Failed to parse '123' as UPC: Expected 6, 7, 8, or 12 digits, got 3.
    - SSCC: Failed to parse '123' as SSCC: Expected 18 digits, got 3.
    - GS1: Failed to match '123' with GS1 AI (12) pattern '^12(\d{6})$'.
"""

try:
    from importlib.metadata import PackageNotFoundError, version  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

from biip._exceptions import BiipException, EncodeError, ParseError
from biip._parser import ParseResult, parse

__all__ = [
    "parse",
    "ParseResult",
    "BiipException",
    "EncodeError",
    "ParseError",
]


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
