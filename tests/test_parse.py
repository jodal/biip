from typing import Type

import pytest

from biip import ParseError, parse
from biip.gs1 import GS1Message
from biip.gtin import Gtin


@pytest.mark.parametrize(
    "value, expected_cls",
    [
        (
            # GTIN-8
            "96385074",
            Gtin,
        ),
        (
            # GTIN-12
            "123601057072",
            Gtin,
        ),
        (
            # GTIN-13
            "5901234123457",
            Gtin,
        ),
        (
            # GTIN-14
            "05901234123457",
            Gtin,
        ),
        (
            # GS1 AI: GTIN
            "0105901234123457",
            GS1Message,
        ),
        (
            # GS1 AI: best before date
            "15210526",
            GS1Message,
        ),
    ],
)
def test_parse(value: str, expected_cls: Type) -> None:
    assert isinstance(parse(value), expected_cls)


def test_parse_with_separator_char() -> None:
    result = parse("101313|15210526", separator_char="|")

    assert isinstance(result, GS1Message)
    assert result.as_hri() == "(10)1313(15)210526"


def test_parse_invalid_data() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse("abc")

    assert (
        str(exc_info.value)
        == "Failed to parse 'abc' as GTIN or GS1 Element String."
    )
