from decimal import Decimal

import pytest
from moneyed import Money

from biip import ParseConfig, ParseError
from biip.gs1_prefixes import GS1Prefix
from biip.gtin import Gtin, GtinFormat
from biip.rcn import Rcn, RcnRegion, RcnUsage


@pytest.mark.parametrize(
    ("rcn_region", "value", "weight", "price", "money"),
    [
        # NOTE: These examples are constructed from a template. This should be
        # extended with actual examples from either specifications or real
        # Baltic products.
        #
        # Estonia
        (RcnRegion.ESTONIA, "2311111112345", Decimal("1.234"), None, None),
        (RcnRegion.ESTONIA, "2411111112342", Decimal("12.34"), None, None),
        (RcnRegion.ESTONIA, "2511111112349", Decimal("123.4"), None, None),
        (RcnRegion.ESTONIA, "2911111111111", None, None, None),
        # Latvia
        (RcnRegion.LATVIA, "2311111112345", Decimal("1.234"), None, None),
        (RcnRegion.LATVIA, "2411111112342", Decimal("12.34"), None, None),
        (RcnRegion.LATVIA, "2511111112349", Decimal("123.4"), None, None),
        (RcnRegion.LATVIA, "2911111111111", None, None, None),
        # Lithuania
        (RcnRegion.LITHUANIA, "2311111112345", Decimal("1.234"), None, None),
        (RcnRegion.LITHUANIA, "2411111112342", Decimal("12.34"), None, None),
        (RcnRegion.LITHUANIA, "2511111112349", Decimal("123.4"), None, None),
        (RcnRegion.LITHUANIA, "2911111111111", None, None, None),
    ],
)
def test_region_baltics(
    rcn_region: RcnRegion,
    value: str,
    weight: Decimal | None,
    price: Decimal | None,
    money: Money | None,
) -> None:
    # The three Baltic countries share the same rules and allocation pool.
    #
    # References:
    #   https://gs1lv.org/img/upload/ENG.Variable%20measure_in_Latvia.pdf

    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=rcn_region))

    assert isinstance(rcn, Rcn)
    assert rcn.region == rcn_region
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


@pytest.mark.parametrize(
    ("value", "weight", "price", "money"),
    [
        ("2135040039753", None, Decimal("39.75"), Money("39.75", "DKK")),
        ("2235040039750", None, Decimal("39.75"), Money("39.75", "DKK")),
        ("2335040039757", None, Decimal("39.75"), Money("39.75", "DKK")),
        ("2435040039754", None, Decimal("39.75"), Money("39.75", "DKK")),
        ("2623570001505", Decimal("0.150"), None, None),
        ("2712341002251", Decimal("0.225"), None, None),
        ("2823570001509", Decimal("0.150"), None, None),
        ("2911111111111", None, None, None),
    ],
)
def test_region_denmark(
    value: str,
    weight: Decimal | None,
    price: Decimal | None,
    money: Money | None,
) -> None:
    # References:
    #   https://www.gs1.dk/om-gs1/overblik-over-gs1-standarder/gtin-13-pris
    #   https://www.gs1.dk/om-gs1/overblik-over-gs1-standarder/gtin-13-vaegt

    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=RcnRegion.DENMARK))

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.DENMARK
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


@pytest.mark.parametrize(
    ("value", "weight", "price", "money"),
    [
        ("2388060112344", Decimal("1.234"), None, None),
        ("2488060112341", Decimal("12.34"), None, None),
        ("2588060112348", Decimal("123.4"), None, None),
        ("2911111111111", None, None, None),
    ],
)
def test_region_finland(
    value: str,
    weight: Decimal | None,
    price: Decimal | None,
    money: Money | None,
) -> None:
    # References:
    #   https://gs1.fi/en/instructions/gs1-company-prefix/how-identify-product-gtin

    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=RcnRegion.FINLAND))

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.FINLAND
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


@pytest.mark.parametrize(
    ("value", "weight", "count", "price", "money"),
    [
        # Money
        ("2211114002394", None, None, Decimal("2.39"), Money("2.39", "EUR")),
        ("2330714002396", None, None, Decimal("2.39"), Money("2.39", "EUR")),
        # Count
        ("2511119000129", None, 12, None, None),
        ("2630719000121", None, 12, None, None),
        # Weight
        ("2811111068708", Decimal("6.870"), None, None, None),
        ("2930711068700", Decimal("6.870"), None, None, None),
        # GTIN-14 works exactly like GTIN-13
        ("02211114002394", None, None, Decimal("2.39"), Money("2.39", "EUR")),
        ("02511119000129", None, 12, None, None),
        ("02811111068708", Decimal("6.870"), None, None, None),
    ],
)
def test_region_germany(
    value: str,
    weight: Decimal | None,
    count: int | None,
    price: Decimal | None,
    money: Money | None,
) -> None:
    # References:
    #   https://www.gs1-germany.de/fileadmin/gs1/fachpublikationen/globale-artikelnummer-gtin-in-der-anwendung.pdf
    #   https://san.gs1-germany.de/SAN-4-Konzept

    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=RcnRegion.GERMANY))

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.GERMANY
    assert rcn.weight == weight
    assert rcn.count == count
    assert rcn.price == price
    assert rcn.money == money


def test_region_germany_fails_with_invalid_variable_measure_check_digit() -> None:
    # The digit 8 in the value below is the variable measure check digit. The
    # correct value is 9.

    with pytest.raises(ParseError) as exc_info:
        Gtin.parse("2511118000120", config=ParseConfig(rcn_region=RcnRegion.GERMANY))

    assert str(exc_info.value) == (
        "Invalid check digit for variable measure value '00012' "
        "in RCN '2511118000120': Expected 9, got 8."
    )


def test_region_germany_when_not_verifying_invalid_check_digit() -> None:
    # The digit 8 in the value below is the variable measure check digit. The
    # correct value is 9.

    rcn = Gtin.parse(
        "2511118000120",
        config=ParseConfig(
            rcn_region=RcnRegion.GERMANY,
            rcn_verify_variable_measure=False,
        ),
    )

    assert isinstance(rcn, Rcn)
    assert rcn == Rcn(
        value="2511118000120",
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix.extract("251"),
        company_prefix=None,
        item_reference="1111",
        payload="251111800012",
        check_digit=0,
        region=RcnRegion.GERMANY,
        usage=RcnUsage.GEOGRAPHICAL,
        count=12,
    )


@pytest.mark.parametrize(
    ("value", "weight", "price", "money"),
    [
        # NOTE: These examples are constructed from a template. This should be
        # extended with actual examples from either specifications or real
        # British products.
        ("2011122912346", None, Decimal("12.34"), Money("12.34", "GBP")),
        ("2911111111111", None, None, None),
    ],
)
def test_region_great_britain(
    value: str,
    weight: Decimal | None,
    price: Decimal | None,
    money: Money | None,
) -> None:
    # References:
    #   https://www.gs1uk.org/how-to-barcode-variable-measure-items

    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=RcnRegion.GREAT_BRITAIN))

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.GREAT_BRITAIN
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


def test_region_great_britain_fails_with_invalid_price_check_digit() -> None:
    # The digit 8 in the value below is the price check digit. The correct value is 9.

    with pytest.raises(ParseError) as exc_info:
        Gtin.parse(
            "2011122812349",
            config=ParseConfig(rcn_region=RcnRegion.GREAT_BRITAIN),
        )

    assert str(exc_info.value) == (
        "Invalid check digit for variable measure value '1234' in RCN '2011122812349': "
        "Expected 9, got 8."
    )


def test_region_great_britain_when_not_verifying_invalid_check_digit() -> None:
    # The digit 8 in the value below is the price check digit. The correct value is 9.

    rcn = Gtin.parse(
        "2011122812349",
        config=ParseConfig(
            rcn_region=RcnRegion.GREAT_BRITAIN,
            rcn_verify_variable_measure=False,
        ),
    )

    assert isinstance(rcn, Rcn)
    assert rcn == Rcn(
        value="2011122812349",
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix.extract("201"),
        company_prefix=None,
        item_reference="11122",
        payload="201112281234",
        check_digit=9,
        region=RcnRegion.GREAT_BRITAIN,
        usage=RcnUsage.GEOGRAPHICAL,
        price=Decimal("12.34"),
        money=Money("12.34", "GBP"),
    )


@pytest.mark.parametrize(
    ("value", "weight", "price", "money"),
    [
        ("2302148210869", Decimal("1.086"), None, None),  # Norvegia 1kg
        ("2368091402263", Decimal("0.226"), None, None),  # Stange kyllingbryst
        ("2911111111111", None, None, None),
    ],
)
def test_region_norway(
    value: str,
    weight: Decimal | None,
    price: Decimal | None,
    money: Money | None,
) -> None:
    # References: TODO: Find specification.

    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=RcnRegion.NORWAY))

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.NORWAY
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money


@pytest.mark.parametrize(
    ("value", "weight", "price", "money"),
    [
        ("2088060112343", None, Decimal("12.34"), Money("12.34", "SEK")),
        ("2188060112340", None, Decimal("123.4"), Money("123.4", "SEK")),
        ("2288060112347", None, Decimal("1234"), Money("1234", "SEK")),
        ("2388060112344", Decimal("1.234"), None, None),
        ("2488060112341", Decimal("12.34"), None, None),
        ("2588060112348", Decimal("123.4"), None, None),
        ("2911111111111", None, None, None),
    ],
)
def test_region_sweden(
    value: str,
    weight: Decimal | None,
    price: Decimal | None,
    money: Money | None,
) -> None:
    # References:
    #   https://www.gs1.se/en/our-standards/Identify/variable-weight-number1/

    rcn = Gtin.parse(value, config=ParseConfig(rcn_region=RcnRegion.SWEDEN))

    assert isinstance(rcn, Rcn)
    assert rcn.region == RcnRegion.SWEDEN
    assert rcn.weight == weight
    assert rcn.price == price
    assert rcn.money == money
