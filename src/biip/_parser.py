"""The top-level Biip parser."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from biip import ParseConfig, ParseError
from biip.gs1_messages import GS1Message
from biip.gtin import Gtin, GtinFormat
from biip.sscc import Sscc
from biip.symbology import GS1Symbology, SymbologyIdentifier
from biip.upc import Upc

if TYPE_CHECKING:
    from collections.abc import Iterator


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

    return result


@dataclass
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
        result.gtin = Gtin.parse(value, config=config)
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
    config: ParseConfig,
    queue: ParseQueue,
    result: ParseResult,
) -> None:
    if result.upc is not None:
        return  # pragma: no cover

    try:
        result.upc = Upc.parse(value, config=config)
        result.upc_error = None
    except ParseError as exc:
        result.upc = None
        result.upc_error = str(exc)
    else:
        # If UPC, expand and set GTIN on the top-level result.
        queue.append((_parse_gtin, result.upc.as_upc_a()))


def _parse_sscc(
    value: str,
    config: ParseConfig,
    queue: ParseQueue,  # noqa: ARG001
    result: ParseResult,
) -> None:
    if result.sscc is not None:
        return  # pragma: no cover

    try:
        result.sscc = Sscc.parse(value, config=config)
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
        result.gs1_message = GS1Message.parse(value, config=config)
        result.gs1_message_error = None
    except ParseError as exc:
        result.gs1_message = None
        result.gs1_message_error = str(exc)
    else:
        # If the GS1 Message contains an SSCC, set SSCC on the top-level result.
        ai_00 = result.gs1_message.element_strings.get(ai="00")
        if ai_00 is not None:
            queue.append((_parse_sscc, ai_00.value))

        # If the GS1 Message contains an GTIN, set GTIN on the top-level result.
        ai_01 = result.gs1_message.element_strings.get(ai="01")
        if ai_01 is not None:
            queue.append((_parse_gtin, ai_01.value))
