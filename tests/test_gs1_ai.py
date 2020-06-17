from typing import Optional

import pytest

from biip.gs1_ai import get_predefined_length


@pytest.mark.parametrize(
    "value, length",
    [
        # Valid data where first element has predefined length
        ("0195012345678903", 16),
        ("01950123456789033102000400", 16),
        ("3102000400", 10),
        #
        # Valid data where first element has unknown length
        ("800500365", None),
        ("10123456", None),
        #
        # Bogus data
        ("9995012345678903", None),
        ("9", None),
        ("", None),
    ],
)
def test_get_predefined_length(value: str, length: Optional[int]) -> None:
    assert get_predefined_length(value) == length
