"""The top-level Biip parser."""

from typing import Callable, List, Optional, Union

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHAR, GS1Message, GS1Symbology
from biip.gtin import Gtin, Rcn, RcnRegion
from biip.symbology import SymbologyIdentifier


ParseResult = Union[Gtin, GS1Message, Rcn]


def parse(
    value: str,
    *,
    rcn_region: Optional[RcnRegion] = None,
    separator_char: str = DEFAULT_SEPARATOR_CHAR,
) -> ParseResult:
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
    value = value.strip()

    symbology_identifier: Optional[SymbologyIdentifier]
    if value.startswith("]"):
        symbology_identifier = SymbologyIdentifier.extract(value)
        value = value[len(symbology_identifier) :]
    else:
        symbology_identifier = None

    parsers = _select_parsers(
        value=value,
        symbology_identifier=symbology_identifier,
        rcn_region=rcn_region,
        separator_char=separator_char,
    )

    errors: List[ParseError] = []

    for parser in parsers:
        try:
            return parser(value)
        except ParseError as exc:
            errors.append(exc)

    error_messages = "\n".join("- " + str(error) for error in errors)
    raise ParseError(f"Failed parsing {value!r}:\n{error_messages}")


def _select_parsers(
    *,
    value: str,
    symbology_identifier: Optional[SymbologyIdentifier],
    rcn_region: Optional[RcnRegion],
    separator_char: str,
) -> List[Callable[[str], ParseResult]]:
    parsers: List[Callable[[str], ParseResult]] = []

    # XXX: The following lambdas are just here to ensure the parsers have the
    # same API. Another way to implement this would be to pass the same
    # configuration object to each parser.
    gtin_parse = lambda value: Gtin.parse(value, rcn_region=rcn_region)  # noqa
    gs1_parse = lambda value: GS1Message.parse(  # noqa
        value, rcn_region=rcn_region, separator_char=separator_char
    )

    if symbology_identifier is not None:
        if symbology_identifier.gs1_symbology in GS1Symbology.with_gtin():
            parsers.append(gtin_parse)

        if (
            symbology_identifier.gs1_symbology
            in GS1Symbology.with_ai_element_strings()
        ):
            parsers.append(gs1_parse)

    if not parsers:
        # Default set of parsers, if we're not able to select a subset..
        parsers = [gtin_parse, gs1_parse]

    return parsers
