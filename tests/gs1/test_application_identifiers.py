import pytest

from biip import ParseError
from biip.gs1 import GS1ApplicationIdentifier


@pytest.mark.parametrize("unknown_ai", ["abcdef", "199999"])
def test_unknown_gs1_ai(unknown_ai: str) -> None:
    with pytest.raises(KeyError) as exc_info:
        GS1ApplicationIdentifier.get(unknown_ai)

    assert str(exc_info.value) == repr(unknown_ai)


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "01",
            GS1ApplicationIdentifier(
                ai="01",
                description="Global Trade Item Number (GTIN)",
                data_title="GTIN",
                fnc1_required=False,
                format="N2+N14",
                pattern=r"^01(\d{14})$",
            ),
        ),
        (
            "90",
            GS1ApplicationIdentifier(
                ai="90",
                description="Information mutually agreed between trading partners",
                data_title="INTERNAL",
                fnc1_required=True,
                format="N2+X..30",
                pattern=(
                    r"^90([\x21-\x22\x25-\x2F\x30-\x39\x3A-\x3F\x41-"
                    r"\x5A\x5F\x61-\x7A]{0,30})$"
                ),
            ),
        ),
    ],
)
def test_get_gs1_ai(value: str, expected: GS1ApplicationIdentifier) -> None:
    assert GS1ApplicationIdentifier.get(value) == expected


@pytest.mark.parametrize("unknown_ai", ["abcdef", "3376999999"])
def test_extract_unknown_gs1_ai(unknown_ai: str) -> None:
    with pytest.raises(ParseError) as exc_info:
        GS1ApplicationIdentifier.extract(unknown_ai)

    assert (
        str(exc_info.value)
        == f"Failed to get GS1 Application Identifier from {unknown_ai!r}."
    )


def test_extract_from_invalid_type() -> None:
    with pytest.raises(TypeError) as exc_info:
        GS1ApplicationIdentifier.extract(1234)  # type: ignore

    assert str(exc_info.value) == "Expected str or bytes, got <class 'int'>."


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
        ),
        (
            b"90SE011\x1d2501611262",
            GS1ApplicationIdentifier(
                ai="90",
                description="Information mutually agreed between trading partners",
                data_title="INTERNAL",
                fnc1_required=True,
                format="N2+X..30",
                pattern=(
                    r"^90([\x21-\x22\x25-\x2F\x30-\x39\x3A-\x3F\x41-"
                    r"\x5A\x5F\x61-\x7A]{0,30})$"
                ),
            ),
        ),
    ],
)
def test_extract_gs1_ai(value: str, expected: GS1ApplicationIdentifier) -> None:
    assert GS1ApplicationIdentifier.extract(value) == expected


def test_gs1_ai_object_len_is_ai_str_len() -> None:
    ai = GS1ApplicationIdentifier.get("01")

    assert len(ai) == len("01")
