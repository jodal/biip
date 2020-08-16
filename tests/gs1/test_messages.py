import pytest

from biip.gs1 import GS1Message


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
    assert GS1Message.parse(value).as_hri() == expected
