import datetime as dt

import pytest

from biip import ParseConfig, ParseError
from biip.gs1_application_identifiers import GS1ApplicationIdentifier
from biip.gs1_digital_link_uris import GS1DigitalLinkURI
from biip.gs1_element_strings import GS1ElementString, GS1ElementStrings
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix
from biip.gtin import Gtin, GtinFormat
from biip.sscc import Sscc


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            # Canonical URI
            "https://id.gs1.org/01/00614141123452",
            GS1DigitalLinkURI(
                value="https://id.gs1.org/01/00614141123452",
                element_strings=GS1ElementStrings(
                    [
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("01"),
                            value="00614141123452",
                            pattern_groups=["00614141123452"],
                            gtin=Gtin(
                                value="00614141123452",
                                format=GtinFormat.GTIN_12,
                                prefix=GS1Prefix(value="061", usage="GS1 US"),
                                company_prefix=GS1CompanyPrefix(value="0614141"),
                                payload="61414112345",
                                check_digit=2,
                            ),
                        ),
                    ]
                ),
            ),
        ),
        (
            # Custom domain and path prefix, with unpadded GTIN-12
            "https://example.com/foo/01/614141123452",
            GS1DigitalLinkURI(
                value="https://example.com/foo/01/614141123452",
                element_strings=GS1ElementStrings(
                    [
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("01"),
                            value="00614141123452",
                            pattern_groups=["00614141123452"],
                            gtin=Gtin(
                                value="00614141123452",
                                format=GtinFormat.GTIN_12,
                                prefix=GS1Prefix(value="061", usage="GS1 US"),
                                company_prefix=GS1CompanyPrefix(value="0614141"),
                                payload="61414112345",
                                check_digit=2,
                            ),
                        ),
                    ]
                ),
            ),
        ),
        (
            # Canonical URI with lot number
            "https://id.gs1.org/01/00614141123452/10/ABC123",
            GS1DigitalLinkURI(
                value="https://id.gs1.org/01/00614141123452/10/ABC123",
                element_strings=GS1ElementStrings(
                    [
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("01"),
                            value="00614141123452",
                            pattern_groups=["00614141123452"],
                            gtin=Gtin(
                                value="00614141123452",
                                format=GtinFormat.GTIN_12,
                                prefix=GS1Prefix(value="061", usage="GS1 US"),
                                company_prefix=GS1CompanyPrefix(value="0614141"),
                                payload="61414112345",
                                check_digit=2,
                            ),
                        ),
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("10"),
                            value="ABC123",
                            pattern_groups=["ABC123"],
                        ),
                    ]
                ),
            ),
        ),
        (
            # GTIN-14 with extra query parameter that is ignored
            "https://id.gs1.org/01/00614141123452?foo=bar",
            GS1DigitalLinkURI(
                value="https://id.gs1.org/01/00614141123452?foo=bar",
                element_strings=GS1ElementStrings(
                    [
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("01"),
                            value="00614141123452",
                            pattern_groups=["00614141123452"],
                            gtin=Gtin(
                                value="00614141123452",
                                format=GtinFormat.GTIN_12,
                                prefix=GS1Prefix(value="061", usage="GS1 US"),
                                company_prefix=GS1CompanyPrefix(value="0614141"),
                                payload="61414112345",
                                check_digit=2,
                            ),
                        ),
                    ]
                ),
            ),
        ),
        (
            # SSCC with content, count, and batch/lot number
            "https://id.gs1.org/00/106141412345678908?02=00614141123452&37=25&10=ABC123",
            GS1DigitalLinkURI(
                value="https://id.gs1.org/00/106141412345678908?02=00614141123452&37=25&10=ABC123",
                element_strings=GS1ElementStrings(
                    [
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("00"),
                            value="106141412345678908",
                            pattern_groups=["106141412345678908"],
                            sscc=Sscc(
                                value="106141412345678908",
                                prefix=GS1Prefix(value="061", usage="GS1 US"),
                                company_prefix=GS1CompanyPrefix(value="0614141"),
                                extension_digit=1,
                                payload="10614141234567890",
                                check_digit=8,
                            ),
                        ),
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("02"),
                            value="00614141123452",
                            pattern_groups=["00614141123452"],
                            gln=None,
                            gln_error=None,
                            gtin=Gtin(
                                value="00614141123452",
                                format=GtinFormat.GTIN_12,
                                prefix=GS1Prefix(value="061", usage="GS1 US"),
                                company_prefix=GS1CompanyPrefix(value="0614141"),
                                payload="61414112345",
                                check_digit=2,
                                packaging_level=None,
                            ),
                        ),
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("37"),
                            value="25",
                            pattern_groups=["25"],
                        ),
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("10"),
                            value="ABC123",
                            pattern_groups=["ABC123"],
                        ),
                    ]
                ),
            ),
        ),
    ],
)
def test_parse(value: str, expected: GS1DigitalLinkURI) -> None:
    assert GS1DigitalLinkURI.parse(value) == expected


@pytest.mark.parametrize(
    ("value", "config", "expected"),
    [
        (
            # Invalid date "000000"
            "https://id.gs1.org/01/614141123452?15=000000",
            ParseConfig(gs1_element_strings_verify_date=False),
            GS1DigitalLinkURI(
                value="https://id.gs1.org/01/614141123452?15=000000",
                element_strings=GS1ElementStrings(
                    [
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("01"),
                            value="00614141123452",
                            pattern_groups=["00614141123452"],
                            gtin=Gtin(
                                value="00614141123452",
                                format=GtinFormat.GTIN_12,
                                prefix=GS1Prefix(value="061", usage="GS1 US"),
                                company_prefix=GS1CompanyPrefix(value="0614141"),
                                payload="61414112345",
                                check_digit=2,
                            ),
                        ),
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("15"),
                            value="000000",
                            pattern_groups=["000000"],
                            date=None,
                        ),
                    ]
                ),
            ),
        ),
    ],
)
def test_parse_with_invalid_element_values(
    value: str,
    config: ParseConfig,
    expected: GS1DigitalLinkURI,
) -> None:
    assert GS1DigitalLinkURI.parse(value, config=config) == expected


@pytest.mark.parametrize(
    ("value", "error"),
    [
        (
            # Non-URI are not allowed
            "614141123452",
            r"^Expected URI, got '614141123452'.$",
        ),
        (
            # Non-HTTP URIs are not allowed
            "mailto:alice@example.com",
            r"^Expected URI scheme to be 'http' or 'https', got 'mailto'.$",
        ),
        (
            # A primary identifier in the path is required
            "http://example.com/foo/123",
            r"^Expected a primary identifier in the path, got '/foo/123'.$",
        ),
        (
            # The path must contain an even number of segments
            "https://example.com/foo/01/614141123452/123",
            r"^Expected even number of path segments, got '/01/614141123452/123'.$",
        ),
        (
            # "15" is not a valid qualifier for GTIN
            "https://id.gs1.org/01/614141123452/15/20250324",
            r"^Expected one of \(22, 10, 21\) as qualifier, got '15'.$",
        ),
        (
            # "22" is a valid qualifier, but not after "10"
            "https://id.gs1.org/01/614141123452/10/ABC123/22/123456789",
            r"^Expected one of \(21\) as qualifier, got '22'.$",
        ),
        (
            # "10" is a valid qualifier, but not after "21"
            "https://id.gs1.org/01/01234567890128/21/12345XYZ/10/ABC123",
            r"^Did not expect a qualifier, got '10'.$",
        ),
        (
            # "10" is not a valid qualifier for SSCC
            "https://id.gs1.org/00/106141412345678908/10/ABC123",
            r"^Did not expect a qualifier, got '10'.$",
        ),
    ],
)
def test_parse_error(value: str, error: str) -> None:
    with pytest.raises(ParseError, match=error):
        GS1DigitalLinkURI.parse(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            GS1ElementStrings(
                [
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
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("15"),
                        value="210526",
                        pattern_groups=["210526"],
                        date=dt.date(2021, 5, 26),
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("10"),
                        value="0329",
                        pattern_groups=["0329"],
                    ),
                ]
            ),
            GS1DigitalLinkURI(
                value="https://id.gs1.org/01/07032069804988/10/0329?15=210526",
                element_strings=GS1ElementStrings(
                    [
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
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("15"),
                            value="210526",
                            pattern_groups=["210526"],
                            date=dt.date(2021, 5, 26),
                        ),
                        GS1ElementString(
                            ai=GS1ApplicationIdentifier.extract("10"),
                            value="0329",
                            pattern_groups=["0329"],
                        ),
                    ]
                ),
            ),
        ),
    ],
)
def test_from_element_strings(
    value: GS1ElementStrings, expected: GS1DigitalLinkURI
) -> None:
    assert GS1DigitalLinkURI.from_element_strings(value) == expected


@pytest.mark.parametrize(
    ("value", "domain", "prefix", "expected"),
    [
        (
            # Defaults creates a canonical URI, using the canonical hostname,
            # numerical AIs, 14-digit GTINs.
            "https://example.com/01/614141123452",
            None,
            None,
            "https://id.gs1.org/01/00614141123452",
        ),
        (
            # Custom domain
            "https://id.gs1.org/01/00614141123452",
            "brand.example.net",
            None,
            "https://brand.example.net/01/00614141123452",
        ),
        (
            # Custom domain with prefix
            "https://id.gs1.org/01/00614141123452",
            "brand.example.net",
            "prefix",
            "https://brand.example.net/prefix/01/00614141123452",
        ),
    ],
)
def test_as_uri(
    *,
    value: str,
    domain: str | None,
    prefix: str | None,
    expected: str,
) -> None:
    assert (
        GS1DigitalLinkURI.parse(value).as_uri(
            domain=domain,
            prefix=prefix,
        )
        == expected
    )


def test_as_uri_errors() -> None:
    with pytest.raises(ValueError, match="Prefix must not start with '/'"):
        GS1DigitalLinkURI.parse("https://example.com/01/614141123452").as_uri(
            prefix="/prefix"
        )
    with pytest.raises(ValueError, match="Prefix must not end with '/'"):
        GS1DigitalLinkURI.parse("https://example.com/01/614141123452").as_uri(
            prefix="prefix/"
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "https://example.com/01/00614141123452",
            "https://id.gs1.org/01/00614141123452",
        ),
        (
            # With deprecated GTIN length
            "https://example.com/01/614141123452",
            "https://id.gs1.org/01/00614141123452",
        ),
        (
            # With deprecated GTIN length and qualifiers
            "https://example.com/01/614141123452/22/2A/10/ABC123",
            "https://id.gs1.org/01/00614141123452/22/2A/10/ABC123",
        ),
        (
            # Extra query parameters are ignored
            "https://example.com/00/106141412345678908?02=00614141123452&37=25&10=ABC123&foo=bar",
            "https://id.gs1.org/00/106141412345678908?02=00614141123452&37=25&10=ABC123",
        ),
    ],
)
def test_as_canonical_uri(value: str, expected: str) -> None:
    assert GS1DigitalLinkURI.parse(value).as_canonical_uri() == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "https://example.com/01/00614141123452",
            "(01)00614141123452",
        ),
        (
            # With deprecated GTIN length
            "https://example.com/01/614141123452",
            "(01)00614141123452",
        ),
        (
            # With deprecated GTIN length and qualifiers
            "https://example.com/01/00614141123452/22/2A/10/ABC123",
            "(01)00614141123452(22)2A(10)ABC123",
        ),
        (
            # Extra query parameters are ignored
            "https://example.com/00/106141412345678908?02=00614141123452&37=25&10=ABC123&foo=bar",
            "(00)106141412345678908(02)00614141123452(37)25(10)ABC123",
        ),
    ],
)
def test_as_gs1_message(value: str, expected: str) -> None:
    assert GS1DigitalLinkURI.parse(value).as_gs1_message().as_hri() == expected


@pytest.mark.parametrize(
    ("value", "ai", "expected"),
    [
        ("https://id.gs1.org/01/614141123452/10/ABC123", "01", ["00614141123452"]),
        ("https://id.gs1.org/01/614141123452/10/ABC123", "10", ["ABC123"]),
    ],
)
def test_filter_element_strings_by_ai(value: str, ai: str, expected: list[str]) -> None:
    matches = GS1DigitalLinkURI.parse(value).element_strings.filter(ai=ai)

    assert [element_string.value for element_string in matches] == expected


@pytest.mark.parametrize(
    ("value", "data_title", "expected"),
    [
        ("https://id.gs1.org/01/614141123452/10/ABC123", "GTIN", ["00614141123452"]),
        ("https://id.gs1.org/01/614141123452/10/ABC123", "BATCH", ["ABC123"]),
    ],
)
def test_filter_element_strings_by_data_title(
    value: str, data_title: str, expected: list[str]
) -> None:
    matches = GS1DigitalLinkURI.parse(value).element_strings.filter(
        data_title=data_title
    )

    assert [element_string.value for element_string in matches] == expected


@pytest.mark.parametrize(
    ("value", "ai", "expected"),
    [
        ("https://id.gs1.org/01/614141123452/10/ABC123", "01", "00614141123452"),
        ("https://id.gs1.org/01/614141123452/10/ABC123", "10", "ABC123"),
        ("https://id.gs1.org/01/614141123452/10/ABC123", "15", None),
    ],
)
def test_get_element_strings_by_ai(value: str, ai: str, expected: str | None) -> None:
    element_string = GS1DigitalLinkURI.parse(value).element_strings.get(ai=ai)

    if expected is None:
        assert element_string is None
    else:
        assert element_string is not None
        assert element_string.value == expected


@pytest.mark.parametrize(
    ("value", "data_title", "expected"),
    [
        ("https://id.gs1.org/01/614141123452/10/ABC123", "GTIN", "00614141123452"),
        ("https://id.gs1.org/01/614141123452/10/ABC123", "BATCH", "ABC123"),
        ("https://id.gs1.org/01/614141123452/10/ABC123", "LOT", "ABC123"),
        ("https://id.gs1.org/01/614141123452/10/ABC123", "BEST BY", None),
    ],
)
def test_get_element_strings_by_data_title(
    value: str, data_title: str, expected: str | None
) -> None:
    element_string = GS1DigitalLinkURI.parse(value).element_strings.get(
        data_title=data_title
    )

    if expected is None:
        assert element_string is None
    else:
        assert element_string is not None
        assert element_string.value == expected
