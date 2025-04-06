import datetime as dt
from decimal import Decimal

import pytest

from biip import ParseConfig, ParseResult, parse
from biip.gs1_application_identifiers import GS1ApplicationIdentifier
from biip.gs1_element_strings import GS1ElementString, GS1ElementStrings
from biip.gs1_messages import GS1Message
from biip.gs1_prefixes import GS1CompanyPrefix, GS1Prefix
from biip.gs1_web_uris import GS1WebURI
from biip.gtin import Gtin, GtinFormat
from biip.rcn import Rcn, RcnRegion, RcnUsage
from biip.sscc import Sscc
from biip.symbology import GS1Symbology, ISOSymbology, SymbologyIdentifier
from biip.upc import Upc, UpcFormat


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            # GTIN-8
            "96385074",
            ParseResult(
                value="96385074",
                gtin=Gtin(
                    value="96385074",
                    format=GtinFormat.GTIN_8,
                    prefix=GS1Prefix(value="00009", usage="GS1 US"),
                    company_prefix=GS1CompanyPrefix(value="0000963"),
                    payload="9638507",
                    check_digit=4,
                ),
                upc_error=(
                    "Invalid UPC-E number system for '96385074': "
                    "Expected 0 or 1, got 9."
                ),
                sscc_error=(
                    "Failed to parse '96385074' as SSCC: Expected 18 digits, got 8."
                ),
                gs1_message=GS1Message(
                    value="96385074",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("96"),
                                value="385074",
                                pattern_groups=["385074"],
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # GTIN-8 with Symbology Identifier
            "]E496385074",
            ParseResult(
                value="]E496385074",
                symbology_identifier=SymbologyIdentifier(
                    value="]E4",
                    iso_symbology=ISOSymbology.EAN_UPC,
                    modifiers="4",
                    gs1_symbology=GS1Symbology.EAN_8,
                ),
                gtin=Gtin(
                    value="96385074",
                    format=GtinFormat.GTIN_8,
                    prefix=GS1Prefix(value="00009", usage="GS1 US"),
                    company_prefix=GS1CompanyPrefix(value="0000963"),
                    payload="9638507",
                    check_digit=4,
                ),
            ),
        ),
        (
            # Both a valid GTIN-8 and a valid UPC-E. GTIN result should be the
            # GTIN-8, not the UPC-E expanded to UPC-A/GTIN-12.
            "12345670",
            ParseResult(
                value="12345670",
                gtin=Gtin(
                    value="12345670",
                    format=GtinFormat.GTIN_8,
                    prefix=GS1Prefix(value="00001", usage="GS1 US"),
                    company_prefix=GS1CompanyPrefix(value="0000123"),
                    payload="1234567",
                    check_digit=0,
                ),
                upc=Upc(
                    value="12345670",
                    format=UpcFormat.UPC_E,
                    number_system_digit=1,
                    payload="1234567",
                    check_digit=0,
                ),
                sscc_error=(
                    "Failed to parse '12345670' as SSCC: Expected 18 digits, got 8."
                ),
                gs1_message_error=(
                    "Failed to match '12345670' with GS1 AI (12) pattern "
                    r"'^12(\d{2}(?:0\d|1[0-2])(?:[0-2]\d|3[01]))$'."
                ),
            ),
        ),
        (
            # GTIN-12. GTIN-12 is also valid as UPC-A.
            "123601057072",
            ParseResult(
                value="123601057072",
                gtin=Gtin(
                    value="123601057072",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="012", usage="GS1 US"),
                    company_prefix=None,
                    payload="12360105707",
                    check_digit=2,
                ),
                upc=Upc(
                    value="123601057072",
                    format=UpcFormat.UPC_A,
                    number_system_digit=1,
                    payload="12360105707",
                    check_digit=2,
                ),
                sscc_error=(
                    "Failed to parse '123601057072' as SSCC: "
                    "Expected 18 digits, got 12."
                ),
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from '7072'."
                ),
            ),
        ),
        (
            # GTIN-12 with Symbology Identifier. GTIN-12 is also valid as UPC-A.
            "]E00123601057072",
            ParseResult(
                value="]E00123601057072",
                symbology_identifier=SymbologyIdentifier(
                    value="]E0",
                    iso_symbology=ISOSymbology.EAN_UPC,
                    modifiers="0",
                    gs1_symbology=GS1Symbology.EAN_13,
                ),
                gtin=Gtin(
                    value="0123601057072",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="012", usage="GS1 US"),
                    company_prefix=None,
                    payload="12360105707",
                    check_digit=2,
                ),
                upc=Upc(
                    value="123601057072",
                    format=UpcFormat.UPC_A,
                    number_system_digit=1,
                    payload="12360105707",
                    check_digit=2,
                ),
            ),
        ),
        (
            # GTIN-13
            "5901234123457",
            ParseResult(
                value="5901234123457",
                gtin=Gtin(
                    value="5901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    company_prefix=None,
                    payload="590123412345",
                    check_digit=7,
                ),
                upc_error=(
                    "Failed to parse '5901234123457' as UPC: "
                    "Expected 6, 7, 8, or 12 digits, got 13."
                ),
                sscc_error=(
                    "Failed to parse '5901234123457' as SSCC: "
                    "Expected 18 digits, got 13."
                ),
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from '5901234123457'."
                ),
            ),
        ),
        (
            # GTIN-13 with Symbology Identifier
            "]E05901234123457",
            ParseResult(
                value="]E05901234123457",
                symbology_identifier=SymbologyIdentifier(
                    value="]E0",
                    iso_symbology=ISOSymbology.EAN_UPC,
                    modifiers="0",
                    gs1_symbology=GS1Symbology.EAN_13,
                ),
                gtin=Gtin(
                    value="5901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    company_prefix=None,
                    payload="590123412345",
                    check_digit=7,
                ),
            ),
        ),
        (
            # GTIN-14
            "05901234123457",
            ParseResult(
                value="05901234123457",
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    company_prefix=None,
                    payload="590123412345",
                    check_digit=7,
                ),
                upc_error=(
                    "Failed to parse '05901234123457' as UPC: "
                    "Expected 6, 7, 8, or 12 digits, got 14."
                ),
                sscc_error=(
                    "Failed to parse '05901234123457' as SSCC: "
                    "Expected 18 digits, got 14."
                ),
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from '05901234123457'."
                ),
            ),
        ),
        (
            # GTIN-14 with Symbology Identifier
            "]I105901234123457",
            ParseResult(
                value="]I105901234123457",
                symbology_identifier=SymbologyIdentifier(
                    value="]I1",
                    iso_symbology=ISOSymbology.ITF,
                    modifiers="1",
                    gs1_symbology=GS1Symbology.ITF_14,
                ),
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    company_prefix=None,
                    payload="590123412345",
                    check_digit=7,
                ),
            ),
        ),
        (
            # UPC-E. UPC-E is expanded to UPC-A and exposed as GTIN too.
            # Coincidentally it is also a valid GS1 Message.
            "425261",
            ParseResult(
                value="425261",
                gtin=Gtin(
                    value="042100005264",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="004", usage="GS1 US"),
                    company_prefix=GS1CompanyPrefix(value="0042100"),
                    payload="04210000526",
                    check_digit=4,
                    packaging_level=None,
                ),
                upc=Upc(
                    value="425261",
                    format=UpcFormat.UPC_E,
                    number_system_digit=0,
                    payload="0425261",
                    check_digit=4,
                ),
                sscc_error=(
                    "Failed to parse '425261' as SSCC: Expected 18 digits, got 6."
                ),
                gs1_message=GS1Message(
                    value="425261",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("425"),
                                value="261",
                                pattern_groups=["261"],
                                gtin=None,
                                sscc=None,
                                date=None,
                                decimal=None,
                                money=None,
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # SSCC
            "157035381410375177",
            ParseResult(
                value="157035381410375177",
                gtin_error=(
                    "Failed to parse '157035381410375177' as GTIN: "
                    "Expected 8, 12, 13, or 14 digits, got 18."
                ),
                upc_error=(
                    "Failed to parse '157035381410375177' as UPC: "
                    "Expected 6, 7, 8, or 12 digits, got 18."
                ),
                sscc=Sscc(
                    value="157035381410375177",
                    prefix=GS1Prefix(value="570", usage="GS1 Denmark"),
                    company_prefix=GS1CompanyPrefix(value="5703538"),
                    extension_digit=1,
                    payload="15703538141037517",
                    check_digit=7,
                ),
                gs1_message_error=(
                    "Failed to match '157035381410375177' with GS1 AI (15) pattern "
                    r"'^15(\d{2}(?:0\d|1[0-2])(?:[0-2]\d|3[01]))$'."
                ),
            ),
        ),
        (
            # GS1 AI: SSCC
            "00157035381410375177",
            ParseResult(
                value="00157035381410375177",
                gtin_error=(
                    "Failed to parse '00157035381410375177' as GTIN: "
                    "Expected 8, 12, 13, or 14 digits, got 20."
                ),
                upc_error=(
                    "Failed to parse '00157035381410375177' as UPC: "
                    "Expected 6, 7, 8, or 12 digits, got 20."
                ),
                sscc=Sscc(
                    value="157035381410375177",
                    prefix=GS1Prefix(value="570", usage="GS1 Denmark"),
                    company_prefix=GS1CompanyPrefix(value="5703538"),
                    extension_digit=1,
                    payload="15703538141037517",
                    check_digit=7,
                ),
                gs1_message=GS1Message(
                    value="00157035381410375177",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("00"),
                                value="157035381410375177",
                                pattern_groups=["157035381410375177"],
                                sscc=Sscc(
                                    value="157035381410375177",
                                    prefix=GS1Prefix(value="570", usage="GS1 Denmark"),
                                    company_prefix=GS1CompanyPrefix(value="5703538"),
                                    extension_digit=1,
                                    payload="15703538141037517",
                                    check_digit=7,
                                ),
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 AI: Invalid SSCC
            "00376130321109103421",
            ParseResult(
                value="00376130321109103421",
                gtin_error=(
                    "Failed to parse '00376130321109103421' as GTIN: "
                    "Expected 8, 12, 13, or 14 digits, got 20."
                ),
                upc_error=(
                    "Failed to parse '00376130321109103421' as UPC: "
                    "Expected 6, 7, 8, or 12 digits, got 20."
                ),
                sscc_error=(
                    "Invalid SSCC check digit for "
                    "'376130321109103421': Expected 0, got 1."
                ),
                gs1_message=GS1Message(
                    value="00376130321109103421",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("00"),
                                value="376130321109103421",
                                pattern_groups=["376130321109103421"],
                                sscc_error=(
                                    "Invalid SSCC check digit for "
                                    "'376130321109103421': Expected 0, got 1."
                                ),
                            ),
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 AI: GTIN-12. GTIN-12 is also valid as UPC-A.
            "0100123601057072",
            ParseResult(
                value="0100123601057072",
                gtin=Gtin(
                    value="00123601057072",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="012", usage="GS1 US"),
                    company_prefix=None,
                    payload="12360105707",
                    check_digit=2,
                    packaging_level=None,
                ),
                upc=Upc(
                    value="123601057072",
                    format=UpcFormat.UPC_A,
                    number_system_digit=1,
                    payload="12360105707",
                    check_digit=2,
                ),
                sscc_error=(
                    "Failed to parse '0100123601057072' as SSCC: "
                    "Expected 18 digits, got 16."
                ),
                gs1_message=GS1Message(
                    value="0100123601057072",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("01"),
                                value="00123601057072",
                                pattern_groups=["00123601057072"],
                                gtin=Gtin(
                                    value="00123601057072",
                                    format=GtinFormat.GTIN_12,
                                    prefix=GS1Prefix(value="012", usage="GS1 US"),
                                    company_prefix=None,
                                    payload="12360105707",
                                    check_digit=2,
                                    packaging_level=None,
                                ),
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 AI: GTIN-13
            "0105901234123457",
            ParseResult(
                value="0105901234123457",
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    company_prefix=None,
                    payload="590123412345",
                    check_digit=7,
                ),
                upc_error=(
                    "Failed to parse '0105901234123457' as UPC: "
                    "Expected 6, 7, 8, or 12 digits, got 16."
                ),
                sscc_error=(
                    "Failed to parse '0105901234123457' as SSCC: "
                    "Expected 18 digits, got 16."
                ),
                gs1_message=GS1Message(
                    value="0105901234123457",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("01"),
                                value="05901234123457",
                                pattern_groups=["05901234123457"],
                                gtin=Gtin(
                                    value="05901234123457",
                                    format=GtinFormat.GTIN_13,
                                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                                    company_prefix=None,
                                    payload="590123412345",
                                    check_digit=7,
                                ),
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 AI: Invalid GTIN
            "0105901234123458",
            ParseResult(
                value="0105901234123458",
                gtin_error=(
                    "Invalid GTIN check digit for '05901234123458': Expected 7, got 8."
                ),
                upc_error=(
                    "Failed to parse '0105901234123458' as UPC: "
                    "Expected 6, 7, 8, or 12 digits, got 16."
                ),
                sscc_error=(
                    "Failed to parse '0105901234123458' as SSCC: "
                    "Expected 18 digits, got 16."
                ),
                gs1_message=GS1Message(
                    value="0105901234123458",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("01"),
                                value="05901234123458",
                                pattern_groups=["05901234123458"],
                                gtin_error=(
                                    "Invalid GTIN check digit for '05901234123458': "
                                    "Expected 7, got 8."
                                ),
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 AI: best before date
            "15210527",
            ParseResult(
                value="15210527",
                gtin_error=(
                    "Invalid GTIN check digit for '15210527': Expected 4, got 7."
                ),
                upc_error=(
                    "Invalid UPC-E check digit for '15210527': Expected 6, got 7."
                ),
                sscc_error=(
                    "Failed to parse '15210527' as SSCC: Expected 18 digits, got 8."
                ),
                gs1_message=GS1Message(
                    value="15210527",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("15"),
                                value="210527",
                                pattern_groups=["210527"],
                                date=dt.date(2021, 5, 27),
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 AI with GS1-128 Symbology Identifier
            "]C1010590123412345715210526",
            ParseResult(
                value="]C1010590123412345715210526",
                symbology_identifier=SymbologyIdentifier(
                    value="]C1",
                    iso_symbology=ISOSymbology.CODE_128,
                    modifiers="1",
                    gs1_symbology=GS1Symbology.GS1_128,
                ),
                gtin=Gtin(
                    value="05901234123457",
                    format=GtinFormat.GTIN_13,
                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                    company_prefix=None,
                    payload="590123412345",
                    check_digit=7,
                ),
                gs1_message=GS1Message(
                    value="010590123412345715210526",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("01"),
                                value="05901234123457",
                                pattern_groups=["05901234123457"],
                                gtin=Gtin(
                                    value="05901234123457",
                                    format=GtinFormat.GTIN_13,
                                    prefix=GS1Prefix(value="590", usage="GS1 Poland"),
                                    company_prefix=None,
                                    payload="590123412345",
                                    check_digit=7,
                                ),
                            ),
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("15"),
                                value="210526",
                                pattern_groups=["210526"],
                                date=dt.date(2021, 5, 26),
                            ),
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 AI with GS1 DataBar Symbology Identifier
            "]e00100123456789012",
            ParseResult(
                value="]e00100123456789012",
                symbology_identifier=SymbologyIdentifier(
                    value="]e0",
                    iso_symbology=ISOSymbology.RSS_EAN_UCC_COMPOSITE,
                    modifiers="0",
                    gs1_symbology=GS1Symbology.GS1_DATABAR,
                ),
                gtin=Gtin(
                    value="00123456789012",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="012", usage="GS1 US"),
                    company_prefix=None,
                    payload="12345678901",
                    check_digit=2,
                ),
                upc=Upc(
                    value="123456789012",
                    format=UpcFormat.UPC_A,
                    number_system_digit=1,
                    payload="12345678901",
                    check_digit=2,
                ),
                gs1_message=GS1Message(
                    value="0100123456789012",
                    element_strings=GS1ElementStrings(
                        [
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("01"),
                                value="00123456789012",
                                pattern_groups=["00123456789012"],
                                gtin=Gtin(
                                    value="00123456789012",
                                    format=GtinFormat.GTIN_12,
                                    prefix=GS1Prefix(value="012", usage="GS1 US"),
                                    company_prefix=None,
                                    payload="12345678901",
                                    check_digit=2,
                                ),
                            )
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 Web URI with GTIN-12, lot number, and expiration date
            "https://example.com/gtin/614141123452/lot/ABC123?15=250330",
            ParseResult(
                value="https://example.com/gtin/614141123452/lot/ABC123?15=250330",
                gtin=Gtin(
                    value="00614141123452",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="061", usage="GS1 US"),
                    company_prefix=GS1CompanyPrefix(value="0614141"),
                    payload="61414112345",
                    check_digit=2,
                ),
                upc=Upc(
                    value="614141123452",
                    format=UpcFormat.UPC_A,
                    number_system_digit=6,
                    payload="61414112345",
                    check_digit=2,
                ),
                gs1_web_uri=GS1WebURI(
                    value="https://example.com/gtin/614141123452/lot/ABC123?15=250330",
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
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("15"),
                                value="250330",
                                pattern_groups=[
                                    "250330",
                                ],
                                gln=None,
                                gln_error=None,
                                gtin=None,
                                gtin_error=None,
                                sscc=None,
                                sscc_error=None,
                                date=dt.date(2025, 3, 30),
                                datetime=None,
                                decimal=None,
                                money=None,
                            ),
                        ]
                    ),
                ),
            ),
        ),
        (
            # GS1 Web URI with GTIN-12, lot number, and expiration date with GS1
            # QR Code symbology identifier
            "]Q3https://example.com/gtin/614141123452/lot/ABC123?15=250330",
            ParseResult(
                value="]Q3https://example.com/gtin/614141123452/lot/ABC123?15=250330",
                symbology_identifier=SymbologyIdentifier(
                    value="]Q3",
                    iso_symbology=ISOSymbology.QR_CODE,
                    modifiers="3",
                    gs1_symbology=GS1Symbology.GS1_QR_CODE,
                ),
                gtin=Gtin(
                    value="00614141123452",
                    format=GtinFormat.GTIN_12,
                    prefix=GS1Prefix(value="061", usage="GS1 US"),
                    company_prefix=GS1CompanyPrefix(value="0614141"),
                    payload="61414112345",
                    check_digit=2,
                ),
                upc=Upc(
                    value="614141123452",
                    format=UpcFormat.UPC_A,
                    number_system_digit=6,
                    payload="61414112345",
                    check_digit=2,
                ),
                gs1_message_error=(
                    "Failed to get GS1 Application Identifier from "
                    "'https://example.com/gtin/614141123452/lot/ABC123?15=250330'."
                ),
                gs1_web_uri=GS1WebURI(
                    value="https://example.com/gtin/614141123452/lot/ABC123?15=250330",
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
                            GS1ElementString(
                                ai=GS1ApplicationIdentifier.extract("15"),
                                value="250330",
                                pattern_groups=[
                                    "250330",
                                ],
                                gln=None,
                                gln_error=None,
                                gtin=None,
                                gtin_error=None,
                                sscc=None,
                                sscc_error=None,
                                date=dt.date(2025, 3, 30),
                                datetime=None,
                                decimal=None,
                                money=None,
                            ),
                        ]
                    ),
                ),
            ),
        ),
    ],
)
def test_parse(value: str, expected: ParseResult) -> None:
    assert parse(value) == expected


def test_parse_rcn_with_ignored_invalid_check_digit() -> None:
    # NOTE: GTINs with variable weight usually only appear on consumer units,
    # and thus in barcodes like EAN-13, but we use a GS1-128 barcode (symbology
    # identifier `]C1`) in this example, so that we get to test the correct
    # passing of the `rcn_verify_variable_measure` parameter throughout all the
    # classes.

    result = parse(
        "]C10102824040005133",
        config=ParseConfig(
            rcn_region=RcnRegion.GERMANY,
            rcn_verify_variable_measure=False,
        ),
    )

    assert result == ParseResult(
        value="]C10102824040005133",
        symbology_identifier=SymbologyIdentifier(
            value="]C1",
            iso_symbology=ISOSymbology.CODE_128,
            modifiers="1",
            gs1_symbology=GS1Symbology.GS1_128,
        ),
        gtin=Rcn(
            value="02824040005133",
            format=GtinFormat.GTIN_13,
            prefix=GS1Prefix.extract("282"),
            company_prefix=None,
            payload="282404000513",
            check_digit=3,
            usage=RcnUsage.GEOGRAPHICAL,
            region=RcnRegion.GERMANY,
            weight=Decimal("0.513"),
        ),
        gs1_message=GS1Message(
            value="0102824040005133",
            element_strings=GS1ElementStrings(
                [
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier.extract("01"),
                        value="02824040005133",
                        pattern_groups=["02824040005133"],
                        gtin=Rcn(
                            value="02824040005133",
                            format=GtinFormat.GTIN_13,
                            prefix=GS1Prefix.extract("282"),
                            company_prefix=None,
                            payload="282404000513",
                            check_digit=3,
                            usage=RcnUsage.GEOGRAPHICAL,
                            region=RcnRegion.GERMANY,
                            weight=Decimal("0.513"),
                        ),
                    )
                ]
            ),
        ),
    )


def test_parse_strips_surrounding_whitespace() -> None:
    result = parse("  \t 5901234123457 \n  ")

    assert result.value == "5901234123457"
    assert result.gtin is not None
    assert result.gtin.value == "5901234123457"


def test_parse_strips_symbology_identifier() -> None:
    result = parse("]E05901234123457")

    assert result.value == "]E05901234123457"
    assert result.symbology_identifier is not None
    assert result.symbology_identifier.value == "]E0"
    assert result.gtin is not None
    assert result.gtin.value == "5901234123457"


def test_parse_with_separator_char() -> None:
    result = parse(
        "101313|15210526",
        config=ParseConfig(separator_chars=["|"]),
    )

    assert result.gs1_message is not None
    assert result.gs1_message.as_hri() == "(10)1313(15)210526"


def test_parse_invalid_data() -> None:
    result = parse("abc")

    assert result.gtin is None
    assert (
        result.gtin_error
        == "Failed to parse 'abc' as GTIN: Expected 8, 12, 13, or 14 digits, got 3."
    )
    assert result.gs1_message is None
    assert (
        result.gs1_message_error
        == "Failed to get GS1 Application Identifier from 'abc'."
    )
    assert result.gs1_web_uri is None
    assert result.gs1_web_uri_error is None
    assert result.sscc is None
    assert (
        result.sscc_error == "Failed to parse 'abc' as SSCC: Expected 18 digits, got 3."
    )
    assert result.upc is None
    assert (
        result.upc_error
        == "Failed to parse 'abc' as UPC: Expected 6, 7, 8, or 12 digits, got 3."
    )


def test_parse_invalid_http_uri() -> None:
    result = parse("https://example.com/foo/bar")

    assert result.gtin is None
    assert result.gtin_error is None
    assert result.gs1_message is None
    assert result.gs1_message_error is None
    assert result.gs1_web_uri is None
    assert (
        result.gs1_web_uri_error
        == "Expected a primary identifier in the path, got '/foo/bar'."
    )
    assert result.sscc is None
    assert result.sscc_error is None
    assert result.upc is None
    assert result.upc_error is None
