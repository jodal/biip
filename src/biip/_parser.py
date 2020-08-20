"""The top-level Biip parser."""

from typing import Optional, Union

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHAR, GS1Message
from biip.gtin import Gtin, GtinFormat, Rcn, RcnRegion


def parse(
    value: str,
    *,
    rcn_region: Optional[RcnRegion] = None,
    separator_char: str = DEFAULT_SEPARATOR_CHAR,
) -> Union[Gtin, GS1Message, Rcn]:
    """Identify data format and parse data.

    The current strategy is:

    1. If length matches a GTIN, attempt to parse and validate check digit.
    2. If that fails, attempt to parse as GS1 Element Strings.

    If you know what type of data you are parsing, consider using
    :meth:`biip.gtin.Gtin.parse` or :meth:`biip.gs1.GS1Message.parse`.

    Args:
        value: The data to classify and parse.
        rcn_region: The geographical region whose rules should be used to
            interpret Restricted Circulation Numbers (RCN).
            Needed to extract e.g. variable weight/price from GTIN.
        separator_char: Character used in place of the FNC1 symbol.
            Defaults to `<GS>` (ASCII value 29).
            If variable-length fields in the middle of the message are
            not terminated with this character, the parser might greedily
            consume the rest of the message.

    Returns:
        A data class depending upon what type of data is parsed.

    Raises:
        ParseError: If parsing of the data fails.
    """
    try:
        if len(value) in list(GtinFormat):
            try:
                return Gtin.parse(value, rcn_region=rcn_region)
            except ParseError:
                pass  # Try the next parser

        return GS1Message.parse(
            value, rcn_region=rcn_region, separator_char=separator_char
        )
    except ParseError:
        raise ParseError(
            f"Failed to parse {value!r} as GTIN or GS1 Element String."
        )
