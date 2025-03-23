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
