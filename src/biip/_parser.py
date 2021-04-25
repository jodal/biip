"""The top-level Biip parser."""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Type, Union

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHARS, GS1Message, GS1Symbology
from biip.gtin import Gtin, GtinFormat, RcnRegion
from biip.sscc import Sscc
from biip.symbology import SymbologyIdentifier
from biip.upc import Upc

ParserType = Union[Type[GS1Message], Type[Gtin], Type[Sscc], Type[Upc]]


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
        parsers = [
            Upc,
            Gtin,  # Can override Upc result.
            Sscc,
            GS1Message,  # Can override Sscc and Gtin result, and thus Upc result.
        ]

    # Run all parsers in order
    for parser in parsers:
        if parser == GS1Message:
            result._parse_gs1_message(
                value,
                rcn_region=rcn_region,
                separator_chars=separator_chars,
            )
        if parser == Gtin:
            result._parse_gtin(value, rcn_region=rcn_region)
        if parser == Sscc:
            result._parse_sscc(value)
        if parser == Upc:
            result._parse_upc(value)

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

    #: The extracted UPC, if any.
    upc: Optional[Upc] = None

    #: The UPC parse error, if parsing as an UPC was attempted and failed.
    upc_error: Optional[str] = None

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

    def _parse_gtin(
        self: "ParseResult",
        value: str,
        *,
        rcn_region: Optional[RcnRegion] = None,
    ) -> None:
        try:
            self.gtin = Gtin.parse(value, rcn_region=rcn_region)
            self.gtin_error = None
        except ParseError as exc:
            self.gtin = None
            self.gtin_error = str(exc)
        else:
            # If GTIN is a GTIN-12, set UPC on the top-level result.
            if self.gtin.format == GtinFormat.GTIN_12:
                self._parse_upc(self.gtin.as_gtin_12())

    def _parse_upc(self: "ParseResult", value: str) -> None:
        try:
            self.upc = Upc.parse(value)
            self.upc_error = None
        except ParseError as exc:
            self.upc = None
            self.upc_error = str(exc)

    def _parse_sscc(self: "ParseResult", value: str) -> None:
        try:
            self.sscc = Sscc.parse(value)
            self.sscc_error = None
        except ParseError as exc:
            self.sscc = None
            self.sscc_error = str(exc)

    def _parse_gs1_message(
        self: "ParseResult",
        value: str,
        *,
        rcn_region: Optional[RcnRegion] = None,
        separator_chars: Iterable[str],
    ) -> None:
        try:
            self.gs1_message = GS1Message.parse(
                value,
                rcn_region=rcn_region,
                separator_chars=separator_chars,
            )
            self.gs1_message_error = None
        except ParseError as exc:
            self.gs1_message = None
            self.gs1_message_error = str(exc)
        else:
            # If the GS1 Message contains an SSCC, set SSCC on the top-level result.
            ai_00 = self.gs1_message.get(ai="00")
            if ai_00 is not None and ai_00.sscc is not None:
                self._parse_sscc(ai_00.sscc.value)

            # If the GS1 Message contains an GTIN, set GTIN on the top-level result.
            ai_01 = self.gs1_message.get(ai="01")
            if ai_01 is not None and ai_01.gtin is not None:
                self._parse_gtin(ai_01.gtin.value, rcn_region=rcn_region)

    def _has_result(self: "ParseResult") -> bool:
        return any([self.gtin, self.upc, self.sscc, self.gs1_message])

    def _get_errors_list(self: "ParseResult") -> str:
        return "\n".join(
            f"- {parser_name}: {error}"
            for parser_name, error in [
                ("GTIN", self.gtin_error),
                ("UPC", self.upc_error),
                ("SSCC", self.sscc_error),
                ("GS1", self.gs1_message_error),
            ]
            if error is not None
        )
