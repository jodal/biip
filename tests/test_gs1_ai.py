from typing import Optional

import pytest

from biip import ParseError
from biip.gs1_ai import GS1ApplicationIdentifier, get_predefined_length


@pytest.mark.parametrize(
    "value, length",
    [
        # Valid data where first element has predefined length
        ("0195012345678903", 16),
        ("01950123456789033102000400", 16),
        ("3102000400", 10),
        #
        # Valid data where first element has unknown length
        ("800500365", None),
        ("10123456", None),
        #
        # Bogus data
        ("9995012345678903", None),
        ("9", None),
        ("", None),
    ],
)
def test_get_predefined_length(value: str, length: Optional[int]) -> None:
    assert get_predefined_length(value) == length


@pytest.mark.parametrize("unknown_ai", ["abcdef", "3376999999"])
def test_unknown_gs1_ai(unknown_ai: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1ApplicationIdentifier.extract(unknown_ai)

    assert (
        str(exc_info.value)
        == f"Failed to get GS1 Application Identifier from {unknown_ai!r}."
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "0195012345678903",
            GS1ApplicationIdentifier(
                ai="01",
                description="Global Trade Item Number (GTIN)",
                data_title="GTIN",
                fnc1_required=False,
                format="N2+N14",
                pattern=r"^01(\d{14})$",
            ),
        )
    ],
)
def test_gs1_ai(value: str, expected: GS1ApplicationIdentifier) -> None:
    assert GS1ApplicationIdentifier.extract(value) == expected
