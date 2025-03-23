import pytest

from biip import ParseError
from biip.gs1_application_identifiers import GS1ApplicationIdentifier


@pytest.mark.parametrize("unknown_ai", ["abcdef", "3376999999"])
def test_extract_unknown_gs1_ai(unknown_ai: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1ApplicationIdentifier.extract(unknown_ai)

    assert (
        str(exc_info.value)
        == f"Failed to get GS1 Application Identifier from {unknown_ai!r}."
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "0195012345678903",
            GS1ApplicationIdentifier(
                ai="01",
                description="Global Trade Item Number (GTIN)",
                data_title="GTIN",
                separator_required=False,
                format="N2+N14",
                pattern=r"^01(\d{14})$",
            ),
        ),
        (
            "90SE011\x1d2501611262",
            GS1ApplicationIdentifier(
                ai="90",
                description="Information mutually agreed between trading partners",
                data_title="INTERNAL",
                separator_required=True,
                format="N2+X..30",
                pattern=r"^90([!%-?A-Z_a-z\x22]{1,30})$",
            ),
        ),
    ],
)
def test_extract_gs1_ai(value: str, expected: GS1ApplicationIdentifier) -> None:
    assert GS1ApplicationIdentifier.extract(value) == expected


def test_gs1_ai_object_len_is_ai_str_len() -> None:
    ai = GS1ApplicationIdentifier.extract("01")

    assert len(ai) == len("01")


def test_is_hashable() -> None:
    ai = GS1ApplicationIdentifier.extract("01")

    assert hash(ai) is not None
