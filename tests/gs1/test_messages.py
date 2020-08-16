from datetime import date

import pytest

from biip import ParseError
from biip.gs1 import (
    DEFAULT_SEPARATOR_CHAR,
    GS1ApplicationIdentifier,
    GS1ElementString,
    GS1Message,
    GS1Prefix,
)
from biip.gtin import Gtin, GtinFormat


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "010703206980498815210526100329",
            GS1Message(
                value="010703206980498815210526100329",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="01",
                            description="Global Trade Item Number (GTIN)",
                            data_title="GTIN",
                            fnc1_required=False,
                            format="N2+N14",
                            pattern="^01(\\d{14})$",
                        ),
                        value="07032069804988",
                        pattern_groups=["07032069804988"],
                        gtin=Gtin(
                            value="07032069804988",
                            format=GtinFormat.GTIN_13,
                            prefix=GS1Prefix(value="703", usage="GS1 Norway"),
                            payload="703206980498",
                            check_digit=8,
                            packaging_level=None,
                        ),
                        date=None,
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="15",
                            description="Best before date (YYMMDD)",
                            data_title="BEST BEFORE or BEST BY",
                            fnc1_required=False,
                            format="N2+N6",
                            pattern="^15(\\d{6})$",
                        ),
                        value="210526",
                        pattern_groups=["210526"],
                        date=date(2021, 5, 26),
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="10",
                            description="Batch or lot number",
                            data_title="BATCH/LOT",
                            fnc1_required=True,
                            format="N2+X..20",
                            pattern=(
                                r"^10([\x21-\x22\x25-\x2F\x30-\x39\x3A-\x3F"
                                r"\x41-\x5A\x5F\x61-\x7A]{0,20})$"
                            ),
                        ),
                        value="0329",
                        pattern_groups=["0329"],
                    ),
                ],
            ),
        ),
        (
            "800370713240010220085952",
            GS1Message(
                value="800370713240010220085952",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="8003",
                            description="Global Returnable Asset Identifier (GRAI)",
                            data_title="GRAI",
                            fnc1_required=True,
                            format="N4+N14+X..16",
                            pattern=(
                                r"^8003(\d{14})([\x21-\x22\x25-\x2F\x30-\x39"
                                r"\x3A-\x3F\x41-\x5A\x5F\x61-\x7A]{0,16})$"
                            ),
                        ),
                        value="70713240010220085952",
                        pattern_groups=["70713240010220", "085952"],
                    )
                ],
            ),
        ),
    ],
)
def test_parse(value: str, expected: GS1Message) -> None:
    assert GS1Message.parse(value) == expected


@pytest.mark.parametrize(
    "value, separator_char, expected_hri",
    [
        (
            # Variable-length lot number field last, all OK.
            "010703206980498815210526100329",
            DEFAULT_SEPARATOR_CHAR,
            "(01)07032069804988(15)210526(10)0329",
        ),
        (
            # Variable-length lot number field in the middle, consuming the
            # best before date field at the end.
            "010703206980498810032915210526",
            DEFAULT_SEPARATOR_CHAR,
            "(01)07032069804988(10)032915210526",
        ),
        (
            # Variable-length lot number field in the middle, end marked with
            # default separator character.
            "0107032069804988100329\x1d15210526",
            DEFAULT_SEPARATOR_CHAR,
            "(01)07032069804988(10)0329(15)210526",
        ),
        (
            # Variable-length lot number field in the middle, end marked with
            # custom separator character.
            "0107032069804988100329|15210526",
            "|",
            "(01)07032069804988(10)0329(15)210526",
        ),
    ],
)
def test_parse_with_separator_char(
    value: str, separator_char: str, expected_hri: str
) -> None:
    assert (
        GS1Message.parse(value, separator_char=separator_char).as_hri()
        == expected_hri
    )


def test_parse_with_too_long_separator_char_fails() -> None:
    with pytest.raises(ValueError) as exc_info:
        GS1Message.parse("10222--15210526", separator_char="--")

    assert (
        str(exc_info.value)
        == "separator_char must be exactly 1 character long."
    )


def test_parse_fails_if_unparsed_data_left() -> None:
    # 10 = AI for BATCH/LOT
    # 222... = Max length BATCH/LOT
    # aaa = Superflous data
    value = "1022222222222222222222aaa"

    with pytest.raises(ParseError) as exc_info:
        GS1Message.parse(value)

    assert (
        str(exc_info.value)
        == "Failed to get GS1 Application Identifier from 'aaa'."
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "010703206980498815210526100329",
            "(01)07032069804988(15)210526(10)0329",
        )
    ],
)
def test_as_hri(value: str, expected: str) -> None:
    assert GS1Message.parse(value).as_hri() == expected
