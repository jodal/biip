from datetime import date

import pytest

from biip import gs1
from biip.gs1 import GS1ApplicationIdentifier, GS1ElementString, GS1Message


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "010703206980498815210526100329",
            GS1Message(
                value="010703206980498815210526100329",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="01",
                            description="Global Trade Item Number (GTIN)",
                            data_title="GTIN",
                            fnc1_required=False,
                            format="N2+N14",
                            pattern="^01(\\d{14})$",
                        ),
                        value="07032069804988",
                        groups=["07032069804988"],
                        date=None,
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="15",
                            description="Best before date (YYMMDD)",
                            data_title="BEST BEFORE or BEST BY",
                            fnc1_required=False,
                            format="N2+N6",
                            pattern="^15(\\d{6})$",
                        ),
                        value="210526",
                        groups=["210526"],
                        date=date(2021, 5, 26),
                    ),
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="10",
                            description="Batch or lot number",
                            data_title="BATCH/LOT",
                            fnc1_required=True,
                            format="N2+X..20",
                            pattern=(
                                r"^10([\x21-\x22\x25-\x2F\x30-\x39\x3A-\x3F"
                                r"\x41-\x5A\x5F\x61-\x7A]{0,20})$"
                            ),
                        ),
                        value="0329",
                        groups=["0329"],
                    ),
                ],
            ),
        ),
        (
            "800370713240010220085952",
            GS1Message(
                value="800370713240010220085952",
                element_strings=[
                    GS1ElementString(
                        ai=GS1ApplicationIdentifier(
                            ai="8003",
                            description="Global Returnable Asset Identifier (GRAI)",
                            data_title="GRAI",
                            fnc1_required=True,
                            format="N4+N14+X..16",
                            pattern=(
                                r"^8003(\d{14})([\x21-\x22\x25-\x2F\x30-\x39"
                                r"\x3A-\x3F\x41-\x5A\x5F\x61-\x7A]{0,16})$"
                            ),
                        ),
                        value="70713240010220085952",
                        groups=["70713240010220", "085952"],
                    )
                ],
            ),
        ),
    ],
)
def test_parse(value: str, expected: GS1Message) -> None:
    assert gs1.parse(value) == expected
