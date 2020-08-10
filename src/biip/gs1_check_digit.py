"""GS1 check digit calculations."""

import itertools
import math


def numeric_check_digit(value: str) -> int:
    """Get GS1 check digit for numeric string.

    Args:
        value: The numeric string to calculate the check digit for.

    Returns:
        The check digit.

    Raises:
        ValueError: If the value isn't numeric.

    Reference:
        GS1 General Specification, chapter 7.9.
    """
    if not value.isnumeric():
        raise ValueError(f"Expected numeric value, got {value!r}.")

    digits = list(map(int, list(value)))
    reversed_digits = reversed(digits)

    weighted_sum = 0
    for digit, weight in zip(reversed_digits, itertools.cycle([3, 1])):
        weighted_sum += digit * weight

    next_ten = math.ceil(weighted_sum / 10) * 10

    return next_ten - weighted_sum
