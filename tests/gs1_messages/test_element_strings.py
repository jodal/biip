import datetime as dt
from decimal import Decimal

import pytest

from biip import ParseError
from biip.gln import Gln
from biip.gs1_application_identifiers import GS1ApplicationIdentifier
from biip.gs1_messages import GS1ElementString
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix
from biip.gtin import Gtin, GtinFormat
from biip.sscc import Sscc


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "00373400306809981733",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("00"),
                value="373400306809981733",
                pattern_groups=["373400306809981733"],
                sscc=Sscc(
                    value="373400306809981733",
                    prefix=GS1Prefix(value="734", usage="GS1 Sweden"),
                    company_prefix=GS1CompanyPrefix(value="73400306"),
                    extension_digit=3,
                    payload="37340030680998173",
                    check_digit=3,
                ),
            ),
        ),
        (
            "0107032069804988",
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
        ),
        (
            "100329",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("10"),
                value="0329",
                pattern_groups=["0329"],
            ),
        ),
        (
            "4101234567890128",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("410"),
                value="1234567890128",
                pattern_groups=["1234567890128"],
                gln=Gln(
                    value="1234567890128",
                    prefix=GS1Prefix(value="123", usage="GS1 US"),
                    company_prefix=GS1CompanyPrefix(value="1234567890"),
                    payload="123456789012",
                    check_digit=8,
                ),
            ),
        ),
        (
            "7011030102",  # Without optional pattern group for time
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("7011"),
                value="030102",
                pattern_groups=["030102"],
                date=dt.date(2003, 1, 2),
                datetime=None,
            ),
        ),
        (
            "70110301021430",  # With optional pattern group for time
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("7011"),
                value="0301021430",
                pattern_groups=["030102", "1430"],
                date=dt.date(2003, 1, 2),
                datetime=dt.datetime(2003, 1, 2, 14, 30),  # noqa: DTZ001
            ),
        ),
        (
            "800307071324001022085952",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("8003"),
                value="07071324001022085952",
                pattern_groups=["0", "7071324001022", "085952"],
            ),
        ),
    ],
)
def test_extract(value: str, expected: GS1ElementString) -> None:
    assert GS1ElementString.extract(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (  # GS1 element string with invalid GLN
            "4101234567890127",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("410"),
                value="1234567890127",
                pattern_groups=["1234567890127"],
                gln=None,  # Not set, because GLN is invalid.
                gln_error=(
                    "Invalid GLN check digit for '1234567890127': Expected 8, got 7."
                ),
            ),
        ),
        (  # GS1 element string with invalid GTIN
            "0107032069804987",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("01"),
                value="07032069804987",
                pattern_groups=["07032069804987"],
                gtin=None,  # Not set, because GTIN is invalid.
                gtin_error=(
                    "Invalid GTIN check digit for '07032069804987': Expected 8, got 7."
                ),
            ),
        ),
        (  # GS1 element string with invalid SSCC
            "00376130321109103421",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("00"),
                value="376130321109103421",
                pattern_groups=["376130321109103421"],
                sscc=None,  # Not set, because SSCC is invalid.
                sscc_error=(
                    "Invalid SSCC check digit for '376130321109103421': "
                    "Expected 0, got 1."
                ),
            ),
        ),
    ],
)
def test_extract_with_nested_error(value: str, expected: GS1ElementString) -> None:
    assert GS1ElementString.extract(value) == expected


@pytest.mark.parametrize(
    ("ai_code", "bad_value"),
    [
        # Too short product number
        ("01", "01123"),
        # Too short weight
        ("3100", "3100123"),
    ],
)
def test_extract_fails_when_not_matching_pattern(ai_code: str, bad_value: str) -> None:
    ai = GS1ApplicationIdentifier.extract(ai_code)

    with pytest.raises(ParseError) as exc_info:
        GS1ElementString.extract(bad_value)

    assert (
        str(exc_info.value)
        == f"Failed to match {bad_value!r} with GS1 AI {ai} pattern '{ai.pattern}'."
    )


@pytest.mark.parametrize(
    ("value", "expected_date", "expected_datetime"),
    [
        ("11030201", dt.date(2003, 2, 1), None),
        ("12030201", dt.date(2003, 2, 1), None),
        ("13030201", dt.date(2003, 2, 1), None),
        ("15030201", dt.date(2003, 2, 1), None),
        ("16030201", dt.date(2003, 2, 1), None),
        ("17030201", dt.date(2003, 2, 1), None),
        ("43240701029999", dt.date(2007, 1, 2), None),
        ("43240701021430", dt.date(2007, 1, 2), dt.datetime(2007, 1, 2, 14, 30)),  # noqa: DTZ001
        ("43250701029999", dt.date(2007, 1, 2), None),
        ("43250701021430", dt.date(2007, 1, 2), dt.datetime(2007, 1, 2, 14, 30)),  # noqa: DTZ001
        ("4326070102", dt.date(2007, 1, 2), None),
        ("70030701021415", dt.date(2007, 1, 2), dt.datetime(2007, 1, 2, 14, 15)),  # noqa: DTZ001
        ("7006030102", dt.date(2003, 1, 2), None),
        ("7007030102", dt.date(2003, 1, 2), None),
        ("7011030102", dt.date(2003, 1, 2), None),
        ("70110301021430", dt.date(2003, 1, 2), dt.datetime(2003, 1, 2, 14, 30)),  # noqa: DTZ001
        ("800800010214", dt.date(2000, 1, 2), dt.datetime(2000, 1, 2, 14, 0)),  # noqa: DTZ001
        ("80080001021415", dt.date(2000, 1, 2), dt.datetime(2000, 1, 2, 14, 15)),  # noqa: DTZ001
        ("8008000102141516", dt.date(2000, 1, 2), dt.datetime(2000, 1, 2, 14, 15, 16)),  # noqa: DTZ001
    ],
)
def test_extract_date_and_datetime(
    value: str, expected_date: dt.date, expected_datetime: dt.datetime | None
) -> None:
    element_string = GS1ElementString.extract(value)

    assert element_string.date == expected_date
    assert element_string.datetime == expected_datetime


@pytest.mark.parametrize(
    ("ai_code", "bad_value"),
    [
        # Bad production date
        ("11", "120230"),
        # Bad best before date
        ("15", "990229"),
    ],
)
def test_extract_fails_with_invalid_date(ai_code: str, bad_value: str) -> None:
    ai = GS1ApplicationIdentifier.extract(ai_code)

    with pytest.raises(ParseError) as exc_info:
        GS1ElementString.extract(f"{ai_code}{bad_value}")

    assert (
        str(exc_info.value)
        == f"Failed to parse GS1 AI {ai} date/time from {bad_value!r}."
    )


THIS_YEAR = dt.datetime.now(tz=dt.timezone.utc).year
THIS_YEAR_SHORT = str(THIS_YEAR)[2:]
MIN_YEAR = THIS_YEAR - 49
MIN_YEAR_SHORT = str(MIN_YEAR)[2:]
MAX_YEAR = THIS_YEAR + 50
MAX_YEAR_SHORT = str(MAX_YEAR)[2:]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            # Best before date, around the current date
            f"15{THIS_YEAR_SHORT}0526",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("15"),
                value=f"{THIS_YEAR_SHORT}0526",
                pattern_groups=[f"{THIS_YEAR_SHORT}0526"],
                date=dt.date(THIS_YEAR, 5, 26),
            ),
        ),
        (
            # Best before date, 49 years into the past
            f"15{MIN_YEAR_SHORT}0526",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("15"),
                value=f"{MIN_YEAR_SHORT}0526",
                pattern_groups=[f"{MIN_YEAR_SHORT}0526"],
                date=dt.date(MIN_YEAR, 5, 26),
            ),
        ),
        (
            # Best before date, 50 years into the future
            f"15{MAX_YEAR_SHORT}0526",
            GS1ElementString(
                ai=GS1ApplicationIdentifier.extract("15"),
                value=f"{MAX_YEAR_SHORT}0526",
                pattern_groups=[f"{MAX_YEAR_SHORT}0526"],
                date=dt.date(MAX_YEAR, 5, 26),
            ),
        ),
    ],
)
def test_extract_handles_min_and_max_year_correctly(
    value: str, expected: GS1ElementString
) -> None:
    assert GS1ElementString.extract(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("15200200", dt.date(2020, 2, 29)),
        ("15210200", dt.date(2021, 2, 28)),
        ("17211200", dt.date(2021, 12, 31)),
    ],
)
def test_extract_handles_zero_day_as_last_day_of_month(
    value: str, expected: dt.date
) -> None:
    assert GS1ElementString.extract(value).date == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Trade measures (GS1 General Specifications, section 3.6.2)
        ("3105123456", Decimal("1.23456")),  # Net weight (kg)
        ("3114123456", Decimal("12.3456")),  # First dimension (m)
        ("3123123456", Decimal("123.456")),  # Second dimension (m)
        ("3132123456", Decimal("1234.56")),  # Third dimension (m)
        ("3141123456", Decimal("12345.6")),  # Area (m^2)
        ("3150123456", Decimal("123456")),  # Net volume (l)
        ("3161123456", Decimal("12345.6")),  # Net volume (m^3)
        # ... plus equivalent for imperial units
        ("3661123456", Decimal("12345.6")),  # Net volume (cubic yards)
        #
        # Logistic measures (GS1 General Specifications, section 3.6.3)
        ("3302023456", Decimal("234.56")),  # Logistic weight (kg)
        ("3313023456", Decimal("23.456")),  # First dimension (m)
        ("3324023456", Decimal("2.3456")),  # Second dimension (m)
        ("3335023456", Decimal("0.23456")),  # Third dimension (m)
        ("3344023456", Decimal("2.3456")),  # Area (m^2)
        ("3353023456", Decimal("23.456")),  # Logistic volume (l)
        ("3362023456", Decimal("234.56")),  # Logistic volume (m^3)
        # ... plus equivalent for imperial units
        ("3691123456", Decimal("12345.6")),  # Logistic volume (cubic yards)
        #
        # Kilograms per square meter (GS1 General Specifications, section 3.6.4)
        ("3372123456", Decimal("1234.56")),
    ],
)
def test_extract_variable_measures(value: str, expected: Decimal) -> None:
    assert GS1ElementString.extract(value).decimal == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Amount payable or coupon value (GS1 General Specifications, section 3.6.6)
        ("3901123", Decimal("12.3")),
        ("3901123456", Decimal("12345.6")),
        ("3903123456789012345", Decimal("123456789012.345")),
        ("3909123456789012345", Decimal("123456.789012345")),
        # Amount payable for variable measure trade item (section 3.6.8)
        ("3921123", Decimal("12.3")),
        ("3921123456", Decimal("12345.6")),
        ("3923123456789012345", Decimal("123456789012.345")),
        ("3929123456789012345", Decimal("123456.789012345")),
    ],
)
def test_extract_amount_payable(value: str, expected: Decimal) -> None:
    assert GS1ElementString.extract(value).decimal == expected


@pytest.mark.parametrize(
    ("value", "expected_currency", "expected_decimal"),
    [
        # Amount payable and ISO currency code (section 3.6.7)
        ("39127101230", "ZAR", Decimal("12.30")),
        ("39117101230", "ZAR", Decimal("123.0")),
        ("391097812301", "EUR", Decimal("12301")),
        #
        # Amount payable for variable measure trade item and currency (section 3.6.9)
        ("39327101230", "ZAR", Decimal("12.30")),
        ("39317101230", "ZAR", Decimal("123.0")),
        ("393097812301", "EUR", Decimal("12301")),
    ],
)
def test_extract_amount_payable_and_currency(
    value: str, expected_currency: str | None, expected_decimal: Decimal | None
) -> None:
    element_string = GS1ElementString.extract(value)

    assert element_string.decimal == expected_decimal

    # Optional: If py-moneyed is installed, create Money instances
    if expected_decimal is None:
        assert element_string.money is None
    else:
        assert element_string.money is not None
        assert element_string.money.amount == expected_decimal
        assert element_string.money.currency.code == expected_currency


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("39400010", Decimal("10")),
        ("39410055", Decimal("5.5")),
    ],
)
def test_extract_percentage_discount(value: str, expected: Decimal) -> None:
    assert GS1ElementString.extract(value).decimal == expected


@pytest.mark.parametrize(
    ("value", "expected"), [("0107032069804988", "(01)07032069804988")]
)
def test_as_hri(value: str, expected: str) -> None:
    assert GS1ElementString.extract(value).as_hri() == expected
