from datetime import date

import pytest

from biip import ParseError
from biip.gs1 import GS1ApplicationIdentifier, GS1ElementString, GS1Prefix
from biip.gtin import GTIN, GTINFormat


@pytest.mark.parametrize(
    "ai_code, bad_value",
    [
        # Too short product number
        ("01", "01123"),
        # Too short weight
        ("3100", "3100123"),
    ],
)
def test_extract_when_not_matching_pattern(
    ai_code: str, bad_value: str
) -> None:
    ai = GS1ApplicationIdentifier.get(ai_code)

    with pytest.raises(ParseError) as exc_info:
        GS1ElementString.extract(bad_value)

    assert (
        str(exc_info.value)
        == f"Failed to match GS1 AI {ai.ai} pattern {ai.pattern!r} with {bad_value!r}."
    )


@pytest.mark.parametrize(
    "ai_code, bad_value",
    [
        # Bad production date
        ("11", "131313"),
        # Bad best before date
        ("15", "999999"),
    ],
)
def test_extract_with_invalid_date(ai_code: str, bad_value: str) -> None:
    ai = GS1ApplicationIdentifier.get(ai_code)

    with pytest.raises(ParseError) as exc_info:
        GS1ElementString.extract(f"{ai_code}{bad_value}")

    assert (
        str(exc_info.value)
        == f"Failed to parse GS1 AI {ai.ai} date from {bad_value!r}."
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "0107032069804988",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.get("01"),
                value="07032069804988",
                pattern_groups=["07032069804988"],
                gtin=GTIN(
                    value="07032069804988",
                    format=GTINFormat.GTIN_13,
                    prefix=GS1Prefix(value="703", usage="GS1 Norway"),
                    payload="703206980498",
                    check_digit=8,
                    packaging_level=None,
                ),
            ),
        ),
        (
            "100329",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.get("10"),
                value="0329",
                pattern_groups=["0329"],
            ),
        ),
        (
            "800370713240010220085952",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.get("8003"),
                value="70713240010220085952",
                pattern_groups=["70713240010220", "085952"],
            ),
        ),
    ],
)
def test_extract(value: str, expected: GS1ElementString) -> None:
    assert GS1ElementString.extract(value) == expected


THIS_YEAR = date.today().year
THIS_YEAR_SHORT = str(THIS_YEAR)[2:]
MIN_YEAR = THIS_YEAR - 49
MIN_YEAR_SHORT = str(MIN_YEAR)[2:]
MAX_YEAR = THIS_YEAR + 50
MAX_YEAR_SHORT = str(MAX_YEAR)[2:]


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            # Best before date, around the current date
            f"15{THIS_YEAR_SHORT}0526",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.get("15"),
                value=f"{THIS_YEAR_SHORT}0526",
                pattern_groups=[f"{THIS_YEAR_SHORT}0526"],
                date=date(THIS_YEAR, 5, 26),
            ),
        ),
        (
            # Best before date, 49 years into the past
            f"15{MIN_YEAR_SHORT}0526",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.get("15"),
                value=f"{MIN_YEAR_SHORT}0526",
                pattern_groups=[f"{MIN_YEAR_SHORT}0526"],
                date=date(MIN_YEAR, 5, 26),
            ),
        ),
        (
            # Best before date, 50 years into the future
            f"15{MAX_YEAR_SHORT}0526",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.get("15"),
                value=f"{MAX_YEAR_SHORT}0526",
                pattern_groups=[f"{MAX_YEAR_SHORT}0526"],
                date=date(MAX_YEAR, 5, 26),
            ),
        ),
    ],
)
def test_extract_date(value: str, expected: GS1ElementString) -> None:
    assert GS1ElementString.extract(value) == expected


@pytest.mark.parametrize(
    "value, expected", [("0107032069804988", "(01)07032069804988",)],
)
def test_as_hri(value: str, expected: str) -> None:
    assert GS1ElementString.extract(value).as_hri() == expected
