"""The top-level Biip parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

from biip import ParseError
from biip.gs1 import DEFAULT_SEPARATOR_CHARS, GS1Message, GS1Symbology
from biip.gtin import Gtin, GtinFormat, RcnRegion
from biip.sscc import Sscc
from biip.symbology import SymbologyIdentifier
from biip.upc import Upc

if TYPE_CHECKING:
    from collections.abc import Iterable


def parse(
    value: str,
    *,
    rcn_region: Optional[RcnRegion] = None,
    rcn_verify_variable_measure: bool = True,
    separator_chars: Iterable[str] = DEFAULT_SEPARATOR_CHARS,
) -> ParseResult:
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
        rcn_verify_variable_measure: Whether to verify that the variable measure
            in a RCN matches its check digit, if present. Some companies use the
            variable measure check digit for other purposes, requiring this
            check to be disabled.
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
    config = ParseConfig(
        rcn_region=rcn_region,
        rcn_verify_variable_measure=rcn_verify_variable_measure,
        separator_chars=separator_chars,
    )
    result = ParseResult(value=value)

    # Extract Symbology Identifier
    if value.startswith("]"):
        result.symbology_identifier = SymbologyIdentifier.extract(value)
        value = value[len(result.symbology_identifier) :]

    # Select parsers
    queue: ParseQueue = []
    if result.symbology_identifier is not None:
        if result.symbology_identifier.gs1_symbology in GS1Symbology.with_gtin():
            queue.append((_parse_gtin, value))
        if (
            result.symbology_identifier.gs1_symbology
            in GS1Symbology.with_ai_element_strings()
        ):
            queue.append((_parse_gs1_message, value))
    if not queue:
        # If we're not able to select a subset based on Symbology Identifiers,
        # run all parsers on the full value.
        queue = [
            (_parse_gs1_message, value),
            (_parse_gtin, value),
            (_parse_sscc, value),
            (_parse_upc, value),
        ]

    # Work through queue of parsers and the values to run them on. Any parser may
    # add additional work to the queue. Only the first result for a field is kept.
    while queue:
        (parse_func, val) = queue.pop(0)
        parse_func(val, config, queue, result)

    if result._has_result():  # noqa: SLF001
        return result

    msg = f"Failed to parse {value!r}:\n{result._get_errors_list()}"  # noqa: SLF001
    raise ParseError(msg)


@dataclass
class ParseConfig:
    """Configuration options for parsers."""

    rcn_region: Optional[RcnRegion]
    rcn_verify_variable_measure: bool
    separator_chars: Iterable[str]


@dataclass
class ParseResult:
    """Results from a successful barcode parsing."""

    value: str
    """The raw value. Only stripped of surrounding whitespace."""

    symbology_identifier: Optional[SymbologyIdentifier] = None
    """The Symbology Identifier, if any."""

    gtin: Optional[Gtin] = None
    """The extracted GTIN, if any.

    Is also set if a GS1 Message containing a GTIN was successfully parsed."""

    gtin_error: Optional[str] = None
    """The GTIN parse error, if parsing as a GTIN was attempted and failed."""

    upc: Optional[Upc] = None
    """The extracted UPC, if any."""

    upc_error: Optional[str] = None
    """The UPC parse error, if parsing as an UPC was attempted and failed."""

    sscc: Optional[Sscc] = None
    """The extracted SSCC, if any.

    Is also set if a GS1 Message containing an SSCC was successfully parsed.
    """

    sscc_error: Optional[str] = None
    """The SSCC parse error, if parsing as an SSCC was attempted and failed."""

    gs1_message: Optional[GS1Message] = None
    """The extracted GS1 Message, if any."""

    gs1_message_error: Optional[str] = None
    """The GS1 Message parse error.

    If parsing as a GS1 Message was attempted and failed.
    """

    def _has_result(self) -> bool:
        return any([self.gtin, self.upc, self.sscc, self.gs1_message])

    def _get_errors_list(self) -> str:
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


ParseQueue = list[tuple["Parser", str]]
Parser = Callable[[str, ParseConfig, ParseQueue, ParseResult], None]


def _parse_gtin(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,
    result: ParseResult,
) -> None:
    if result.gtin is not None:
        return  # pragma: no cover

    try:
        result.gtin = Gtin.parse(
            value,
            rcn_region=config.rcn_region,
            rcn_verify_variable_measure=config.rcn_verify_variable_measure,
        )
        result.gtin_error = None
    except ParseError as exc:
        result.gtin = None
        result.gtin_error = str(exc)
    else:
        # If GTIN is a GTIN-12, set UPC on the top-level result.
        if result.gtin.format == GtinFormat.GTIN_12:
            queue.append((_parse_upc, result.gtin.as_gtin_12()))


def _parse_upc(
    value: str,
    config: ParseConfig,  # noqa: ARG001
    queue: ParseQueue,
    result: ParseResult,
) -> None:
    if result.upc is not None:
        return  # pragma: no cover

    try:
        result.upc = Upc.parse(value)
        result.upc_error = None
    except ParseError as exc:
        result.upc = None
        result.upc_error = str(exc)
    else:
        # If UPC, expand and set GTIN on the top-level result.
        queue.append((_parse_gtin, result.upc.as_upc_a()))


def _parse_sscc(
    value: str,
    config: ParseConfig,  # noqa: ARG001
    queue: ParseQueue,  # noqa: ARG001
    result: ParseResult,
) -> None:
    if result.sscc is not None:
        return  # pragma: no cover

    try:
        result.sscc = Sscc.parse(value)
        result.sscc_error = None
    except ParseError as exc:
        result.sscc = None
        result.sscc_error = str(exc)


def _parse_gs1_message(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,
    result: ParseResult,
) -> None:
    if result.gs1_message is not None:
        return  # pragma: no cover

    try:
        result.gs1_message = GS1Message.parse(
            value,
            rcn_region=config.rcn_region,
            rcn_verify_variable_measure=config.rcn_verify_variable_measure,
            separator_chars=config.separator_chars,
        )
        result.gs1_message_error = None
    except ParseError as exc:
        result.gs1_message = None
        result.gs1_message_error = str(exc)
    else:
        # If the GS1 Message contains an SSCC, set SSCC on the top-level result.
        ai_00 = result.gs1_message.get(ai="00")
        if ai_00 is not None:
            queue.append((_parse_sscc, ai_00.value))

        # If the GS1 Message contains an GTIN, set GTIN on the top-level result.
        ai_01 = result.gs1_message.get(ai="01")
        if ai_01 is not None:
            queue.append((_parse_gtin, ai_01.value))
