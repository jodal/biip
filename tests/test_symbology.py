import pytest

from biip import ParseError
from biip.symbology import GS1Symbology, Symbology, SymbologyIdentifier


def test_gs1_symbology_enum() -> None:
    assert GS1Symbology("C1") == GS1Symbology.GS1_128


def test_gs1_symbology_with_ai_element_strings() -> None:
    assert GS1Symbology.EAN_13 not in GS1Symbology.with_ai_element_strings()
    assert GS1Symbology.GS1_128 in GS1Symbology.with_ai_element_strings()


def test_gs1_symbology_with_gtin() -> None:
    assert GS1Symbology.EAN_13 in GS1Symbology.with_gtin()

    # Even though GS1-128 can contain a GTIN,
    # it cannot be parsed with a pure GTIN parser.
    assert GS1Symbology.GS1_128 not in GS1Symbology.with_gtin()


def test_symbology_enum() -> None:
    assert Symbology("C") == Symbology.CODE_128


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "]E0abc",
            SymbologyIdentifier(
                value="]E0",
                symbology=Symbology.EAN_UPC,
                modifiers="0",
                gs1_symbology=GS1Symbology.EAN_13,
            ),
        ),
        (
            "]C0abc",
            SymbologyIdentifier(
                value="]C0",
                symbology=Symbology.CODE_128,
                modifiers="0",
                gs1_symbology=None,
            ),
        ),
        (
            "]C1abc",
            SymbologyIdentifier(
                value="]C1",
                symbology=Symbology.CODE_128,
                modifiers="1",
                gs1_symbology=GS1Symbology.GS1_128,
            ),
        ),
        (
            "]I1abc",
            SymbologyIdentifier(
                value="]I1",
                symbology=Symbology.ITF,
                modifiers="1",
                gs1_symbology=GS1Symbology.ITF_14,
            ),
        ),
        (
            "]Y1abcdefghijkl",
            SymbologyIdentifier(
                value="]Y1a",
                symbology=Symbology.SYSTEM_EXPANSION,
                modifiers="1a",
                gs1_symbology=None,
            ),
        ),
        (
            "]Y9abcdefghijkl",
            SymbologyIdentifier(
                value="]Y9abcdefghi",
                symbology=Symbology.SYSTEM_EXPANSION,
                modifiers="9abcdefghi",
                gs1_symbology=None,
            ),
        ),
    ],
)
def test_extract(value: str, expected: SymbologyIdentifier) -> None:
    assert SymbologyIdentifier.extract(value) == expected


def test_extract_fails_if_no_flag_character() -> None:
    with pytest.raises(ParseError) as exc_info:
        SymbologyIdentifier.extract("E0")

    assert str(exc_info.value) == (
        "Failed to get Symbology Identifier from 'E0'. "
        "No initial ']' flag character found."
    )


def test_extract_fails_if_unknown_code_character() -> None:
    with pytest.raises(ParseError) as exc_info:
        SymbologyIdentifier.extract("]J0")

    assert str(exc_info.value) == (
        "Failed to get Symbology Identifier from ']J0'. "
        "'J' is not a recognized code character."
    )


@pytest.mark.parametrize("value", ["]E0", "]C1", "]Y1a", "]Y9abcdefghi"])
def test_len(value: str) -> None:
    assert len(SymbologyIdentifier.extract(value)) == len(value)


@pytest.mark.parametrize("value", ["]E0", "]C1", "]Y1a", "]Y9abcdefghi"])
def test_str(value: str) -> None:
    assert str(SymbologyIdentifier.extract(value)) == value
