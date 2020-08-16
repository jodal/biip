"""The top-level Biip parser."""

from typing import Union

from biip import ParseError
from biip.gs1 import GS1Message
from biip.gtin import Gtin, GtinFormat


def parse(value: str) -> Union[Gtin, GS1Message]:
    """Identify data format and parse data.

    The current strategy is:

    1. If length matches a GTIN, attempt to parse and validate check digit.
    2. If that fails, attempt to parse as GS1 Element Strings.

    If you know what type of data you are parsing, consider using
    :meth:`biip.gtin.Gtin.parse` or :meth:`biip.gs1.GS1Message.parse`.

    Args:
        value: The data to classify and parse.

    Returns:
        A data class depending upon what type of data is parsed.

    Raises:
        ParseError: If parsing of the data fails.
    """
    try:
        if len(value) in list(GtinFormat):
            try:
                return Gtin.parse(value)
            except ParseError:
                pass  # Try the next parser

        return GS1Message.parse(value)
    except ParseError:
        raise ParseError(
            f"Failed to parse {value!r} as GTIN or GS1 Element String."
        )
