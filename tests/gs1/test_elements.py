from datetime import date

import pytest

from biip import ParseError
from biip.gs1 import GS1ApplicationIdentifier, GS1Element


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
        GS1Element.extract(bad_value)

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
        GS1Element.extract(f"{ai_code}{bad_value}")

    assert (
        str(exc_info.value)
        == f"Failed to parse GS1 AI {ai.ai} date from {bad_value!r}."
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "0107032069804988",
            GS1Element(
                ai=GS1ApplicationIdentifier.get("01"),
                value="07032069804988",
                groups=["07032069804988"],
            ),
        ),
        (
            "15210526",
            GS1Element(
                ai=GS1ApplicationIdentifier.get("15"),
                value="210526",
                groups=["210526"],
                date=date(2021, 5, 26),
            ),
        ),
        (
            "100329",
            GS1Element(
                ai=GS1ApplicationIdentifier.get("10"),
                value="0329",
                groups=["0329"],
            ),
        ),
        (
            "800370713240010220085952",
            GS1Element(
                ai=GS1ApplicationIdentifier.get("8003"),
                value="70713240010220085952",
                groups=["70713240010220", "085952"],
            ),
        ),
    ],
)
def test_extract(value: str, expected: GS1Element) -> None:
    assert GS1Element.extract(value) == expected
