from datetime import date

import pytest

from biip import ParseError, ParseResult, parse
from biip.gs1 import (
    GS1ApplicationIdentifier,
    GS1ElementString,
    GS1Message,
    GS1Prefix,
    GS1Symbology,
)
from biip.gtin import Gtin, GtinFormat
from biip.sscc import Sscc
from biip.symbology import Symbology, SymbologyIdentifier


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            # GTIN-8
            "96385074",
            ParseResult(
                value="96385074",
                gtin=Gtin(
                    value="96385074",
                    format=GtinFormat.GTIN_8,
                    prefix=GS1Prefix(value="00009", usage="GS1 US"),
                    payload="9638507",
                    check_digit=4,
                ),
                gs1_message=GS1Message(
                    value="96385074",
                    element_strings=[
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("96"),
                            value="385074",
                            pattern_groups=["385074"],
                        )
                    ],
                ),
                sscc_error=(
                    "Failed parsing '96385074' as SSCC: Expected 18 digits, got 8."
                ),
            ),
        ),
        (
            # GTIN-12
            "123601057072",
            ParseResult(
                value="123601057072",
                gtin=Gtin(
                    value="123601057072",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="123", usage="GS1 US"),
                    payload="12360105707",
                    check_digit=2,
                ),
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from '7072'."
                ),
                sscc_error=(
                    "Failed parsing '123601057072' as SSCC: Expected 18 digits, got 12."
                ),
            ),
        ),
        (
            # GTIN-13
            "5901234123457",
            ParseResult(
                value="5901234123457",
                gtin=Gtin(
                    value="5901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    payload="590123412345",
                    check_digit=7,
                ),
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from '5901234123457'."
                ),
                sscc_error=(
                    "Failed parsing '5901234123457' as SSCC: "
                    "Expected 18 digits, got 13."
                ),
            ),
        ),
        (
            # GTIN-13 with Symbology Identifier
            "]E05901234123457",
            ParseResult(
                value="]E05901234123457",
                symbology_identifier=SymbologyIdentifier(
                    value="]E0",
                    symbology=Symbology.EAN_UPC,
                    modifiers="0",
                    gs1_symbology=GS1Symbology.EAN_13,
                ),
                gtin=Gtin(
                    value="5901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    payload="590123412345",
                    check_digit=7,
                ),
            ),
        ),
        (
            # GTIN-14
            "05901234123457",
            ParseResult(
                value="05901234123457",
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    payload="590123412345",
                    check_digit=7,
                ),
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from '05901234123457'."
                ),
                sscc_error=(
                    "Failed parsing '05901234123457' as SSCC: "
                    "Expected 18 digits, got 14."
                ),
            ),
        ),
        (
            # GTIN-14 with Symbology Identifier
            "]I105901234123457",
            ParseResult(
                value="]I105901234123457",
                symbology_identifier=SymbologyIdentifier(
                    value="]I1",
                    symbology=Symbology.ITF,
                    modifiers="1",
                    gs1_symbology=GS1Symbology.ITF_14,
                ),
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    payload="590123412345",
                    check_digit=7,
                ),
            ),
        ),
        (
            # SSCC
            "376130321109103420",
            ParseResult(
                value="376130321109103420",
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from '09103420'."
                ),
                gtin_error=(
                    "Failed parsing '376130321109103420' as GTIN: "
                    "Expected 8, 12, 13, or 14 digits, got 18."
                ),
                sscc=Sscc(
                    value="376130321109103420",
                    prefix=GS1Prefix(
                        value="761", usage="GS1 Schweiz, Suisse, Svizzera"
                    ),
                    extension_digit=3,
                    payload="37613032110910342",
                    check_digit=0,
                ),
            ),
        ),
        (
            # GS1 AI: SSCC
            "00376130321109103420",
            ParseResult(
                value="00376130321109103420",
                gtin_error=(
                    "Failed parsing '00376130321109103420' as GTIN: "
                    "Expected 8, 12, 13, or 14 digits, got 20."
                ),
                gs1_message=GS1Message(
                    value="00376130321109103420",
                    element_strings=[
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("00"),
                            value="376130321109103420",
                            pattern_groups=["376130321109103420"],
                            sscc=Sscc(
                                value="376130321109103420",
                                prefix=GS1Prefix(
                                    value="761",
                                    usage="GS1 Schweiz, Suisse, Svizzera",
                                ),
                                extension_digit=3,
                                payload="37613032110910342",
                                check_digit=0,
                            ),
                        )
                    ],
                ),
                sscc=Sscc(
                    value="376130321109103420",
                    prefix=GS1Prefix(
                        value="761", usage="GS1 Schweiz, Suisse, Svizzera"
                    ),
                    extension_digit=3,
                    payload="37613032110910342",
                    check_digit=0,
                ),
            ),
        ),
        (
            # GS1 AI: GTIN
            "0105901234123457",
            ParseResult(
                value="0105901234123457",
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    payload="590123412345",
                    check_digit=7,
                ),
                gs1_message=GS1Message(
                    value="0105901234123457",
                    element_strings=[
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("01"),
                            value="05901234123457",
                            pattern_groups=["05901234123457"],
                            gtin=Gtin(
                                value="05901234123457",
                                format=GtinFormat.GTIN_13,
                                prefix=GS1Prefix(
                                    value="590", usage="GS1 Poland"
                                ),
                                payload="590123412345",
                                check_digit=7,
                            ),
                        )
                    ],
                ),
                sscc_error=(
                    "Failed parsing '0105901234123457' as SSCC: "
                    "Expected 18 digits, got 16."
                ),
            ),
        ),
        (
            # GS1 AI: best before date
            "15210526",
            ParseResult(
                value="15210526",
                gtin_error=(
                    "Invalid GTIN check digit for '15210526': Expected 4, got 6."
                ),
                gs1_message=GS1Message(
                    value="15210526",
                    element_strings=[
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("15"),
                            value="210526",
                            pattern_groups=["210526"],
                            date=date(2021, 5, 26),
                        )
                    ],
                ),
                sscc_error=(
                    "Failed parsing '15210526' as SSCC: Expected 18 digits, got 8."
                ),
            ),
        ),
        (
            # GS1 AI with Symbology Identifier
            "]C1010590123412345715210526",
            ParseResult(
                value="]C1010590123412345715210526",
                symbology_identifier=SymbologyIdentifier(
                    value="]C1",
                    symbology=Symbology.CODE_128,
                    modifiers="1",
                    gs1_symbology=GS1Symbology.GS1_128,
                ),
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    payload="590123412345",
                    check_digit=7,
                ),
                gs1_message=GS1Message(
                    value="010590123412345715210526",
                    element_strings=[
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("01"),
                            value="05901234123457",
                            pattern_groups=["05901234123457"],
                            gtin=Gtin(
                                value="05901234123457",
                                format=GtinFormat.GTIN_13,
                                prefix=GS1Prefix(
                                    value="590", usage="GS1 Poland"
                                ),
                                payload="590123412345",
                                check_digit=7,
                            ),
                        ),
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("15"),
                            value="210526",
                            pattern_groups=["210526"],
                            date=date(2021, 5, 26),
                        ),
                    ],
                ),
            ),
        ),
    ],
)
def test_parse(value: str, expected: ParseResult) -> None:
    assert parse(value) == expected


def test_parse_strips_surrounding_whitespace() -> None:
    result = parse("  \t 5901234123457 \n  ")

    assert result.value == "5901234123457"
    assert result.gtin is not None
    assert result.gtin.value == "5901234123457"


def test_parse_strips_symbology_identifier() -> None:
    result = parse("]E05901234123457")

    assert result.value == "]E05901234123457"
    assert result.symbology_identifier is not None
    assert result.symbology_identifier.value == "]E0"
    assert result.gtin is not None
    assert result.gtin.value == "5901234123457"


def test_parse_with_separator_char() -> None:
    result = parse("101313|15210526", separator_char="|")

    assert result.gs1_message is not None
    assert result.gs1_message.as_hri() == "(10)1313(15)210526"


def test_parse_invalid_data() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse("abc")

    assert str(exc_info.value) == (
        "Failed parsing 'abc':\n"
        "- Failed parsing 'abc' as GTIN: Expected 8, 12, 13, or 14 digits, got 3.\n"
        "- Failed parsing 'abc' as SSCC: Expected 18 digits, got 3.\n"
        "- Failed to get GS1 Application Identifier from 'abc'."
    )
