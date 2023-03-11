"""Tests of encoding GTINs."""

import pytest

from biip import EncodeError
from biip.gtin import Gtin


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # GTIN-8
        ("96385074", "00000096385074"),
        # GTIN-12 with three leading zeros
        ("000902914511", "00000902914511"),
        ("00000902914511", "00000902914511"),
        # GTIN-12 without leading zero
        ("123601057072", "00123601057072"),
        ("0123601057072", "00123601057072"),
        # GTIN-13
        ("5901234123457", "05901234123457"),
        ("05901234123457", "05901234123457"),
        # GTIN-14
        ("98765432109213", "98765432109213"),
    ],
)
def test_as_gtin_14(value: str, expected: str) -> None:
    assert Gtin.parse(value).as_gtin_14() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # GTIN-8
        ("96385074", "0000096385074"),
        # GTIN-12 with three leading zeros
        ("000902914511", "0000902914511"),
        ("00000902914511", "0000902914511"),
        # GTIN-12 without leading zero
        ("123601057072", "0123601057072"),
        ("0123601057072", "0123601057072"),
        # GTIN-13
        ("5901234123457", "5901234123457"),
        ("05901234123457", "5901234123457"),
    ],
)
def test_as_gtin_13(value: str, expected: str) -> None:
    assert Gtin.parse(value).as_gtin_13() == expected


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-14
        "98765432109213",
    ],
)
def test_as_gtin_13_fails_for_too_long_values(value: str) -> None:
    gtin = Gtin.parse(value)

    with pytest.raises(EncodeError) as exc_info:
        gtin.as_gtin_13()

    assert str(exc_info.value) == f"Failed encoding {value!r} as GTIN-13."


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # GTIN-8
        ("96385074", "000096385074"),
        # GTIN-12 with three leading zeros
        ("000902914511", "000902914511"),
        ("0000902914511", "000902914511"),
        ("00000902914511", "000902914511"),
        # GTIN-12 without leading zero
        ("123601057072", "123601057072"),
        ("0123601057072", "123601057072"),
        ("00123601057072", "123601057072"),
    ],
)
def test_as_gtin_12(value: str, expected: str) -> None:
    assert Gtin.parse(value).as_gtin_12() == expected


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-13
        "5901234123457",
        # GTIN-14
        "98765432109213",
    ],
)
def test_as_gtin_12_fails_for_too_long_values(value: str) -> None:
    gtin = Gtin.parse(value)

    with pytest.raises(EncodeError) as exc_info:
        gtin.as_gtin_12()

    assert str(exc_info.value) == f"Failed encoding {value!r} as GTIN-12."


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # GTIN-8
        ("96385074", "96385074"),
    ],
)
def test_as_gtin_8(value: str, expected: str) -> None:
    assert Gtin.parse(value).as_gtin_8() == expected


@pytest.mark.parametrize(
    "value",
    [
        # GTIN-12
        "000902914511",
        "123601057072",
        # GTIN-13
        "5901234123457",
        # GTIN-14
        "98765432109213",
    ],
)
def test_as_gtin_8_fails_for_too_long_values(value: str) -> None:
    gtin = Gtin.parse(value)

    with pytest.raises(EncodeError) as exc_info:
        gtin.as_gtin_8()

    assert str(exc_info.value) == f"Failed encoding {value!r} as GTIN-8."
