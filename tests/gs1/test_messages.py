import pytest

from biip.gs1 import parse


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "010703206980498815210526100329",
            "(01)07032069804988(15)210526(10)0329",
        )
    ],
)
def test_as_hri(value: str, expected: str) -> None:
    assert parse(value).as_hri() == expected