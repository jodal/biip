"""The top-level Biip parser."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

from biip import ParseConfig, ParseError
from biip.gs1_digital_link_uris import GS1DigitalLinkURI
from biip.gs1_messages import GS1Message
from biip.gtin import Gtin, GtinFormat
from biip.sscc import Sscc
from biip.symbology import GS1Symbology, SymbologyIdentifier
from biip.upc import Upc

if TYPE_CHECKING:
    from collections.abc import Iterator

    from biip.gs1_element_strings import GS1ElementStrings


def parse(
    value: str,
    *,
    config: ParseConfig | None = None,
) -> ParseResult:
    """Identify data format and parse data.

    The current strategy is:

    1. If Symbology Identifier prefix indicates a GTIN or GS1 Message,
       attempt to parse and validate as that.
    2. Else, if not Symbology Identifier, attempt to parse with all parsers.

    Args:
        value: The data to classify and parse.
        config: Configuration options for parsers.

    Returns:
        A `ParseResult` object with the results and errors from all parsers.
    """
    if config is None:
        config = ParseConfig()

    value = value.strip()
    result = ParseResult(value=value)

    # Extract Symbology Identifier
    if value.startswith("]"):
        result = replace(
            result, symbology_identifier=SymbologyIdentifier.extract(value)
        )
        assert result.symbology_identifier
        value = value[len(result.symbology_identifier) :]

    # Select parsers
    queue: ParseQueue = []
    if result.symbology_identifier is not None:
        if result.symbology_identifier.gs1_symbology in GS1Symbology.with_gtin():
            queue.append((_parse_gtin, value))
        if (
            result.symbology_identifier.gs1_symbology
            in GS1Symbology.with_gs1_messages()
        ):
            queue.append((_parse_gs1_message, value))
        if (
            result.symbology_identifier.gs1_symbology
            in GS1Symbology.with_gs1_digital_link_uri()
        ):
            queue.append((_parse_gs1_digital_link_uri, value))
    elif value.startswith("http"):
        queue.append((_parse_gs1_digital_link_uri, value))
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
        result = parse_func(val, config, queue, result)

    return result


@dataclass(frozen=True)
class ParseResult:
    """Results from a successful barcode parsing."""

    value: str
    """The raw value. Only stripped of surrounding whitespace."""

    symbology_identifier: SymbologyIdentifier | None = None
    """The Symbology Identifier, if any."""

    gtin: Gtin | None = None
    """The extracted [GTIN][biip.gtin.Gtin], if any.

    Is also set if a GS1 Message containing a GTIN was successfully parsed."""

    gtin_error: str | None = None
    """The GTIN parse error, if parsing as a GTIN was attempted and failed."""

    upc: Upc | None = None
    """The extracted [UPC][biip.upc.Upc], if any."""

    upc_error: str | None = None
    """The UPC parse error, if parsing as an UPC was attempted and failed."""

    sscc: Sscc | None = None
    """The extracted [SSCC][biip.sscc.Sscc], if any.

    Is also set if a GS1 Message containing an SSCC was successfully parsed.
    """

    sscc_error: str | None = None
    """The SSCC parse error, if parsing as an SSCC was attempted and failed."""

    gs1_message: GS1Message | None = None
    """The extracted [GS1 Message][biip.gs1_messages.GS1Message], if any."""

    gs1_message_error: str | None = None
    """The GS1 Message parse error.

    If parsing as a GS1 Message was attempted and failed.
    """

    gs1_digital_link_uri: GS1DigitalLinkURI | None = None
    """
    The extracted [GS1 Digtal Link URI][biip.gs1_digital_link_uris.GS1DigitalLinkURI],
    if any.
    """

    gs1_digital_link_uri_error: str | None = None
    """The GS1 Digital Link URI parse error.

    If parsing as a GS1 Digital Link URI was attempted and failed.
    """

    def __rich_repr__(self) -> Iterator[tuple[str, Any] | tuple[str, Any, Any]]:
        # Skip printing fields with default values
        yield "value", self.value
        yield "symbology_identifier", self.symbology_identifier, None
        yield "gtin", self.gtin, None
        yield "gtin_error", self.gtin_error, None
        yield "upc", self.upc, None
        yield "upc_error", self.upc_error, None
        yield "sscc", self.sscc, None
        yield "sscc_error", self.sscc_error, None
        yield "gs1_message", self.gs1_message, None
        yield "gs1_message_error", self.gs1_message_error, None
        yield "gs1_digital_link_uri", self.gs1_digital_link_uri, None
        yield "gs1_digital_link_uri_error", self.gs1_digital_link_uri_error, None


ParseQueue = list[tuple["Parser", str]]
Parser = Callable[[str, ParseConfig, ParseQueue, ParseResult], ParseResult]


def _parse_gtin(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,
    result: ParseResult,
) -> ParseResult:
    if result.gtin is not None:
        return result  # pragma: no cover

    try:
        gtin = Gtin.parse(value, config=config)
        gtin_error = None
    except ParseError as exc:
        gtin = None
        gtin_error = str(exc)

    result = replace(
        result,
        gtin=gtin,
        gtin_error=gtin_error,
    )

    # If GTIN is a GTIN-12, set UPC on the top-level result.
    if result.gtin is not None and result.gtin.format == GtinFormat.GTIN_12:
        queue.append((_parse_upc, result.gtin.as_gtin_12()))

    return result


def _parse_upc(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,
    result: ParseResult,
) -> ParseResult:
    if result.upc is not None:
        return result  # pragma: no cover

    try:
        upc = Upc.parse(value, config=config)
        upc_error = None
    except ParseError as exc:
        upc = None
        upc_error = str(exc)

    if upc is not None:
        # If UPC, expand and set GTIN on the top-level result.
        queue.append((_parse_gtin, upc.as_upc_a()))

    return replace(result, upc=upc, upc_error=upc_error)


def _parse_sscc(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,  # noqa: ARG001
    result: ParseResult,
) -> ParseResult:
    if result.sscc is not None:
        return result  # pragma: no cover

    try:
        sscc = Sscc.parse(value, config=config)
        sscc_error = None
    except ParseError as exc:
        sscc = None
        sscc_error = str(exc)

    return replace(result, sscc=sscc, sscc_error=sscc_error)


def _parse_gs1_message(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,
    result: ParseResult,
) -> ParseResult:
    if result.gs1_message is not None:
        return result  # pragma: no cover

    try:
        gs1_message = GS1Message.parse(value, config=config)
        gs1_message_error = None
    except ParseError as exc:
        gs1_message = None
        gs1_message_error = str(exc)

    if gs1_message is not None:
        _promote_gs1_elements(gs1_message.element_strings, queue)

    return replace(result, gs1_message=gs1_message, gs1_message_error=gs1_message_error)


def _parse_gs1_digital_link_uri(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,
    result: ParseResult,
) -> ParseResult:
    if result.gs1_digital_link_uri is not None:
        return result  # pragma: no cover

    try:
        gs1_digital_link_uri = GS1DigitalLinkURI.parse(value, config=config)
        gs1_digital_link_uri_error = None
    except ParseError as exc:
        gs1_digital_link_uri = None
        gs1_digital_link_uri_error = str(exc)

    if gs1_digital_link_uri is not None:
        _promote_gs1_elements(gs1_digital_link_uri.element_strings, queue)

    return replace(
        result,
        gs1_digital_link_uri=gs1_digital_link_uri,
        gs1_digital_link_uri_error=gs1_digital_link_uri_error,
    )


def _promote_gs1_elements(
    gs1_element_strings: GS1ElementStrings,
    queue: ParseQueue,
) -> None:
    # If the GS1 Message contains an SSCC, set SSCC on the top-level result.
    ai_00 = gs1_element_strings.get(ai="00")
    if ai_00 is not None:
        queue.append((_parse_sscc, ai_00.value))

    # If the GS1 Message contains an GTIN, set GTIN on the top-level result.
    ai_01 = gs1_element_strings.get(ai="01")
    if ai_01 is not None:
        queue.append((_parse_gtin, ai_01.value))
