import datetime as dt
from collections.abc import Iterable
from decimal import Decimal

import pytest

from biip import ParseConfig, ParseError
from biip.gs1_application_identifiers import GS1ApplicationIdentifier
from biip.gs1_messages import GS1ElementString, GS1Message
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix
from biip.gtin import Gtin, GtinFormat
from biip.rcn import Rcn, RcnRegion


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "010703206980498815210526100329",
            GS1Message(
                value="010703206980498815210526100329",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("01"),
                        value="07032069804988",
                        pattern_groups=["07032069804988"],
                        gtin=Gtin(
                            value="07032069804988",
                            format=GtinFormat.GTIN_13,
                            prefix=GS1Prefix(value="703", usage="GS1 Norway"),
                            company_prefix=GS1CompanyPrefix(value="703206"),
                            payload="703206980498",
                            check_digit=8,
                        ),
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("15"),
                        value="210526",
                        pattern_groups=["210526"],
                        date=dt.date(2021, 5, 26),
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("10"),
                        value="0329",
                        pattern_groups=["0329"],
                    ),
                ],
            ),
        ),
        (
            "800307071324001022085952",
            GS1Message(
                value="800307071324001022085952",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("8003"),
                        value="07071324001022085952",
                        pattern_groups=["0", "7071324001022", "085952"],
                    )
                ],
            ),
        ),
    ],
)
def test_parse(value: str, expected: GS1Message) -> None:
    assert GS1Message.parse(value) == expected


@pytest.mark.parametrize(
    ("value", "separator_chars", "expected_hri"),
    [
        (
            # Variable-length lot number field last, all OK.
            "010703206980498815210526100329",
            ("\x1d",),
            "(01)07032069804988(15)210526(10)0329",
        ),
        (
            # Variable-length lot number field in the middle, consuming the
            # best before date field at the end.
            "010703206980498810032915210526",
            ("\x1d",),
            "(01)07032069804988(10)032915210526",
        ),
        (
            # Variable-length lot number field in the middle, end marked with
            # default separator character.
            "0107032069804988100329\x1d15210526",
            ("\x1d",),
            "(01)07032069804988(10)0329(15)210526",
        ),
        (
            # Variable-length lot number field in the middle, end marked with
            # custom separator character.
            "0107032069804988100329|15210526",
            ("|",),
            "(01)07032069804988(10)0329(15)210526",
        ),
        (
            # Unrealistic corner case just to exercise the code:
            # Two variable-length fields marked with different separators
            "0107032069804988100329|2112345\x1d15210526",
            ("|", "\x1d"),
            "(01)07032069804988(10)0329(21)12345(15)210526",
        ),
    ],
)
def test_parse_with_separator_char(
    value: str, separator_chars: Iterable[str], expected_hri: str
) -> None:
    assert (
        GS1Message.parse(
            value,
            config=ParseConfig(separator_chars=separator_chars),
        ).as_hri()
        == expected_hri
    )


def test_parse_with_too_long_separator_char_fails() -> None:
    with pytest.raises(
        ValueError,
        match=(
            r"^All separator characters must be exactly 1 character long, "
            r"got \['--'\].$"
        ),
    ):
        GS1Message.parse(
            "10222--15210526",
            config=ParseConfig(separator_chars=["--"]),
        )


@pytest.mark.parametrize(
    ("value", "error"),
    [
        # 10 = AI for BATCH/LOT
        # 222... = Max length BATCH/LOT
        # aaa = Superflous data
        (
            "1022222222222222222222aaa",
            "Failed to get GS1 Application Identifier from 'aaa'.",
        ),
        # Too short to match optional time group (as this is really a GTIN-13)
        ("701103020185", "Failed to get GS1 Application Identifier from '85'."),
    ],
)
def test_parse_fails_if_unparsed_data_left(value: str, error: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1Message.parse(value)

    assert str(exc_info.value) == error


@pytest.mark.parametrize(
    ("value", "expected_hri"),
    [
        # A separator at the end of the string is never needed.
        ("15210526100329\x1d", "(15)210526(10)0329"),
        # 15... is a fixed length date, and should not end with a separator.
        ("15210526\x1d100329", "(15)210526(10)0329"),
        # Double separator chars are ignored.
        (
            "0107032069804988100329\x1d\x1d15210526",
            "(01)07032069804988(10)0329(15)210526",
        ),
    ],
)
def test_parse_ignores_redundant_separator_chars(value: str, expected_hri: str) -> None:
    assert GS1Message.parse(value).as_hri() == expected_hri


def test_parse_strips_surrounding_whitespace() -> None:
    message = GS1Message.parse("  \t 800307071324001022085952 \n  ")

    assert message.value == "800307071324001022085952"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "(17)221231",
            GS1Message(
                value="17221231",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("17"),
                        value="221231",
                        pattern_groups=["221231"],
                        date=dt.date(2022, 12, 31),
                    )
                ],
            ),
        ),
        (
            "(10)123(17)221231",
            GS1Message(
                value="10123\x1d17221231",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("10"),
                        value="123",
                        pattern_groups=["123"],
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("17"),
                        value="221231",
                        pattern_groups=["221231"],
                        date=dt.date(2022, 12, 31),
                    ),
                ],
            ),
        ),
        (
            "(17)221231(10)123",
            GS1Message(
                value="1722123110123",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("17"),
                        value="221231",
                        pattern_groups=["221231"],
                        date=dt.date(2022, 12, 31),
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("10"),
                        value="123",
                        pattern_groups=["123"],
                    ),
                ],
            ),
        ),
    ],
)
def test_parse_hri(value: str, expected: GS1Message) -> None:
    assert GS1Message.parse_hri(value) == expected


def test_parse_hri_with_gtin_with_variable_weight() -> None:
    result = GS1Message.parse_hri(
        "(01)02302148210869",
        config=ParseConfig(rcn_region=RcnRegion.NORWAY),
    )

    gs1_gtin = result.get(ai="01")
    assert gs1_gtin
    gtin = gs1_gtin.gtin
    assert isinstance(gtin, Rcn)
    assert gtin.weight == Decimal("1.086")


def test_parse_hri_strips_surrounding_whitespace() -> None:
    message = GS1Message.parse_hri("  \t (17)221231 \n  ")

    assert message.value == "17221231"


@pytest.mark.parametrize(
    "value",
    [
        "",  # Empty string
        "17221231",  # Valid data, but no parenthesis
        "aaa(17)221231",  # Valid data, but extra data in front
    ],
)
def test_parse_hri_fails_if_not_starting_with_parenthesis(value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1Message.parse_hri(value)

    assert str(exc_info.value) == (
        f"Expected HRI string {value!r} to start with a parenthesis."
    )


@pytest.mark.parametrize(
    "value",
    [
        "(15)",  # Valid start of string, but no data
    ],
)
def test_parse_hri_fails_if_no_pattern_matches(value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1Message.parse_hri(value)

    assert str(exc_info.value) == (
        "Could not find any GS1 Application Identifiers in "
        f"{value!r}. Expected format: '(AI)DATA(AI)DATA'."
    )


@pytest.mark.parametrize(
    "value",
    [
        "(1)15210526",
    ],
)
def test_parse_hri_fails_if_ai_is_unknown(value: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1Message.parse_hri(value)

    assert str(exc_info.value) == (
        "Unknown GS1 Application Identifier '1' in '(1)15210526'."
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "010703206980498815210526100329",
            "(01)07032069804988(15)210526(10)0329",
        )
    ],
)
def test_as_hri(value: str, expected: str) -> None:
    assert GS1Message.parse(value).as_hri() == expected


@pytest.mark.parametrize(
    ("value", "ai", "expected"),
    [
        ("010703206980498815210526100329", "01", ["07032069804988"]),
        ("010703206980498815210526100329", "15", ["210526"]),
        ("010703206980498815210526100329", "37", []),
        ("7230EM123\x1d7231EM456\x1d7232EM789", "7231", ["EM456"]),
        (
            "7230EM123\x1d7231EM456\x1d7232EM789",
            "723",
            ["EM123", "EM456", "EM789"],
        ),
    ],
)
def test_filter_element_strings_by_ai(value: str, ai: str, expected: list[str]) -> None:
    matches = GS1Message.parse(value).filter(ai=ai)

    assert [element_string.value for element_string in matches] == expected


@pytest.mark.parametrize(
    ("value", "data_title", "expected"),
    [
        ("010703206980498815210526100329", "GTIN", ["07032069804988"]),
        ("010703206980498815210526100329", "BEST BY", ["210526"]),
        ("010703206980498815210526100329", "COUNT", []),
        (
            "7230EM123\x1d7231EM456\x1d7232EM789",
            "CERT",
            ["EM123", "EM456", "EM789"],
        ),
    ],
)
def test_filter_element_strings_by_data_title(
    value: str, data_title: str, expected: list[str]
) -> None:
    matches = GS1Message.parse(value).filter(data_title=data_title)

    assert [element_string.value for element_string in matches] == expected


@pytest.mark.parametrize(
    ("value", "ai", "expected"),
    [
        ("010703206980498815210526100329", "01", "07032069804988"),
        ("010703206980498815210526100329", "15", "210526"),
        ("010703206980498815210526100329", "10", "0329"),
        ("010703206980498815210526100329", "37", None),
        ("7230EM123\x1d7231EM456\x1d7232EM789", "7231", "EM456"),
        ("7230EM123\x1d7231EM456\x1d7232EM789", "723", "EM123"),
    ],
)
def test_get_element_string_by_ai(value: str, ai: str, expected: str | None) -> None:
    element_string = GS1Message.parse(value).get(ai=ai)

    if expected is None:
        assert element_string is None
    else:
        assert element_string is not None
        assert element_string.value == expected


@pytest.mark.parametrize(
    ("value", "data_title", "expected"),
    [
        ("010703206980498815210526100329", "GTIN", "07032069804988"),
        ("010703206980498815210526100329", "BEST BY", "210526"),
        ("010703206980498815210526100329", "BATCH", "0329"),
        ("010703206980498815210526100329", "COUNT", None),
        ("7230EM123\x1d7231EM456\x1d7232EM789", "CERT # 1", "EM456"),
        ("7230EM123\x1d7231EM456\x1d7232EM789", "CERT", "EM123"),
    ],
)
def test_get_element_string_by_data_title(
    value: str, data_title: str, expected: str | None
) -> None:
    element_string = GS1Message.parse(value).get(data_title=data_title)

    if expected is None:
        assert element_string is None
    else:
        assert element_string is not None
        assert element_string.value == expected


def test_filter_element_strings_by_ai_instance() -> None:
    ai = GS1ApplicationIdentifier.extract("01")
    msg = GS1Message.parse("010703206980498815210526100329")

    element_string = msg.get(ai=ai)

    assert element_string is not None
    assert element_string.value == "07032069804988"
