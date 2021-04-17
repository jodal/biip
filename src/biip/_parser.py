"""The top-level Biip parser."""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Type, Union

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHARS, GS1Message, GS1Symbology
from biip.gtin import Gtin, RcnRegion
from biip.sscc import Sscc
from biip.symbology import SymbologyIdentifier

ParserType = Union[Type[GS1Message], Type[Gtin], Type[Sscc]]


def parse(
    value: str,
    *,
    rcn_region: Optional[RcnRegion] = None,
    separator_chars: Iterable[str] = DEFAULT_SEPARATOR_CHARS,
) -> "ParseResult":
    """Identify data format and parse data.

    The current strategy is:

    1. If Symbology Identifier prefix indicates a GTIN or GS1 Message,
       attempt to parse and validate as that.
    2. Else, if not Symbology Identifier, attempt to parse with all parsers.

    Args:
        value: The data to classify and parse.
        rcn_region: The geographical region whose rules should be used to
            interpret Restricted Circulation Numbers (RCN).
            Needed to extract e.g. variable weight/price from GTIN.
        separator_chars: Characters used in place of the FNC1 symbol.
            Defaults to `<GS>` (ASCII value 29).
            If variable-length fields in the middle of the message are
            not terminated with a separator character, the parser might
            greedily consume the rest of the message.

    Returns:
        A data class depending upon what type of data is parsed.

    Raises:
        ParseError: If parsing of the data fails.
    """
    value = value.strip()
    result = ParseResult(value=value)

    # Extract Symbology Identifier
    if value.startswith("]"):
        result.symbology_identifier = SymbologyIdentifier.extract(value)
        value = value[len(result.symbology_identifier) :]

    # Select parsers
    parsers: List[ParserType] = []
    if result.symbology_identifier is not None:
        if result.symbology_identifier.gs1_symbology in GS1Symbology.with_gtin():
            parsers.append(Gtin)
        if (
            result.symbology_identifier.gs1_symbology
            in GS1Symbology.with_ai_element_strings()
        ):
            parsers.append(GS1Message)
    if not parsers:
        # If we're not able to select a subset based on Symbology Identifiers,
        # run all parsers in the default order.
        parsers = [Gtin, Sscc, GS1Message]

    # Run all parsers in order
    for parser in parsers:
        if parser == Gtin:
            try:
                result.gtin = Gtin.parse(value, rcn_region=rcn_region)
            except ParseError as exc:
                result.gtin_error = str(exc)

        if parser == Sscc:
            try:
                result.sscc = Sscc.parse(value)
            except ParseError as exc:
                result.sscc_error = str(exc)

        if parser == GS1Message:
            try:
                result.gs1_message = GS1Message.parse(
                    value,
                    rcn_region=rcn_region,
                    separator_chars=separator_chars,
                )
            except ParseError as exc:
                result.gs1_message_error = str(exc)
            else:
                ai_00 = result.gs1_message.get(ai="00")
                if ai_00 is not None:
                    # GS1 Message contains an SSCC
                    result.sscc = ai_00.sscc
                    # Clear error from parsing full value a SSCC.
                    result.sscc_error = None

                ai_01 = result.gs1_message.get(ai="01")
                if ai_01 is not None:
                    # GS1 Message contains a GTIN.
                    result.gtin = ai_01.gtin
                    # Clear error from parsing full value as GTIN.
                    result.gtin_error = None

    if result._has_result():
        return result
    else:
        raise ParseError(f"Failed to parse {value!r}:\n{result._get_errors_list()}")


@dataclass
class ParseResult:
    """Results from a successful barcode parsing."""

    #: The raw value. Only stripped of surrounding whitespace.
    value: str

    #: The Symbology Identifier, if any.
    symbology_identifier: Optional[SymbologyIdentifier] = None

    #: The extracted GTIN, if any.
    #: Is also set if a GS1 Message containing a GTIN was successfully parsed.
    gtin: Optional[Gtin] = None

    #: The GTIN parse error, if parsing as a GTIN was attempted and failed.
    gtin_error: Optional[str] = None

    #: The extracted SSCC, if any.
    #: Is also set if a GS1 Message containing an SSCC was successfully parsed.
    sscc: Optional[Sscc] = None

    #: The SSCC parse error, if parsing as an SSCC was attempted and failed.
    sscc_error: Optional[str] = None

    #: The extracted GS1 Message, if any.
    gs1_message: Optional[GS1Message] = None

    #: The GS1 Message parse error,
    #: if parsing as a GS1 Message was attempted and failed.
    gs1_message_error: Optional[str] = None

    def _has_result(self: "ParseResult") -> bool:
        return any([self.gtin, self.sscc, self.gs1_message])

    def _get_errors_list(self: "ParseResult") -> str:
        return "\n".join(
            f"- {parser_name}: {error}"
            for parser_name, error in [
                ("GTIN", self.gtin_error),
                ("SSCC", self.sscc_error),
                ("GS1", self.gs1_message_error),
            ]
            if error is not None
        )
