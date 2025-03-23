from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from biip.rcn import RcnRegion


@dataclass(frozen=True)
class ParseConfig:
    """Configuration options for parsers.

    Biip strives to do the right thing by default, but you can customize
    some of its the behavior by setting these options.
    """

    gs1_message_verify_date: bool = True
    """Whether to verify that the date in a GS1 message is valid.

    According to the GS1 General Specification, dates are required to contain a
    valid year and month. Only the day of month can be left as zeros, which
    should be interpreted as the last day of the month.

    Some barcodes include a GS1 element string with all zero dates, requiring
    this check to be disabled.
    """

    rcn_region: RcnRegion | str | None = None
    """The geographical region to use when parsing RCNs.

    Restricted Circulation Numbers (RCN) have different meanings in different
    geographical regions. Specify your region here so that Biip can use the
    right parsing rules.

    This must be set to extract variable weight or price from GTINs.
    """

    rcn_verify_variable_measure: bool = True
    """
    Whether to verify that the variable measure in a RCN matches its check digit.

    Some companies use the variable measure check digit for other purposes,
    requiring this check to be disabled.
    """

    separator_chars: Iterable[str] = ("\x1d",)
    """
    Characters to look for as separators between fields in GS1 messages.

    Defaults to the "group separator" character (byte `0x1d` in ASCII), which is
    commonly returned by barcode scanners in place of the FNC1 barcode symbol
    that separates fields.

    If variable-length fields in the middle of the message are not terminated
    with a separator character, the parser might greedily consume the rest of
    the message.
    """
