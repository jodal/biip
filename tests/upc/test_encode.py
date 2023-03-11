"""Tests of encoding UPCs."""

import pytest

from biip import EncodeError
from biip.upc import Upc


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (  # UPC-A to UPC-A
            "123456789012",
            "123456789012",
        ),
        (  # Reverse of UPC-A suppression, condition A
            "02345673",
            "023456000073",
        ),
        (  # Reverse of UPC-A suppression, condition B
            "02345147",
            "023450000017",
        ),
        (  # Reverse of UPC-A suppression, condition C
            "06397126",
            "063200009716",
        ),
        (  # Reverse of UPC-A suppression, condition D
            "08679339",
            "086700000939",
        ),
    ],
)
def test_as_upc_a(value: str, expected: str) -> None:
    assert Upc.parse(value).as_upc_a() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (  # 6-digit UPC-E, implicit number system 0, no check digit.
            "425261",
            "04252614",
        ),
        (  # 7-digit UPC-E, explicit number system 1, no check digit.
            "1425261",
            "14252611",
        ),
        (  # 8-digit UPC-E, explicit number system 1, with check digit.
            "14252611",
            "14252611",
        ),
        (  # UPC-A suppression, condition A
            "023456000073",
            "02345673",
        ),
        (  # UPC-A suppression, condition B
            "023450000017",
            "02345147",
        ),
        (  # UPC-A suppression, condition C
            "063200009716",
            "06397126",
        ),
        (  # UPC-A suppression, condition D
            "086700000939",
            "08679339",
        ),
    ],
)
def test_as_upc_e(value: str, expected: str) -> None:
    assert Upc.parse(value).as_upc_e() == expected


def test_as_upc_e_when_suppression_is_not_possible() -> None:
    with pytest.raises(EncodeError) as exc_info:
        Upc.parse("123456789012").as_upc_e()

    assert str(exc_info.value) == "UPC-A '123456789012' cannot be represented as UPC-E."


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("425261", "042100005264"),  # UPC-E, 6 digit
        ("0425261", "042100005264"),  # UPC-E, 7 digit
        ("04252614", "042100005264"),  # UPC-E, 8 digit
        ("042100005264", "042100005264"),  # UPC-A
    ],
)
def test_as_gtin_12(value: str, expected: str) -> None:
    assert Upc.parse(value).as_gtin_12() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("425261", "0042100005264"),  # UPC-E, 6 digit
        ("0425261", "0042100005264"),  # UPC-E, 7 digit
        ("04252614", "0042100005264"),  # UPC-E, 8 digit
        ("042100005264", "0042100005264"),  # UPC-A
    ],
)
def test_as_gtin_13(value: str, expected: str) -> None:
    assert Upc.parse(value).as_gtin_13() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("425261", "00042100005264"),  # UPC-E, 6 digit
        ("0425261", "00042100005264"),  # UPC-E, 7 digit
        ("04252614", "00042100005264"),  # UPC-E, 8 digit
        ("042100005264", "00042100005264"),  # UPC-A
    ],
)
def test_as_gtin_14(value: str, expected: str) -> None:
    assert Upc.parse(value).as_gtin_14() == expected
