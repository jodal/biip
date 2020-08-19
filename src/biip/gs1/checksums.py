"""Checksum algorithms used by GS1 standards."""

import itertools


def numeric_check_digit(value: str) -> int:
    """Get GS1 check digit for numeric string.

    Args:
        value: The numeric string to calculate the check digit for.

    Returns:
        The check digit.

    Raises:
        ValueError: If the value isn't numeric.

    References:
        GS1 General Specification, section 7.9

    Example:
        >>> from biip.gs1.checksums import numeric_check_digit
        >>> numeric_check_digit("950110153100")  # GTIN-13
        0
        >>> numeric_check_digit("9501234")  # GTIN-8
        6
    """
    if not value.isnumeric():
        raise ValueError(f"Expected numeric value, got {value!r}.")

    digits = list(map(int, list(value)))
    reversed_digits = reversed(digits)

    weighted_sum = 0
    for digit, weight in zip(reversed_digits, itertools.cycle([3, 1])):
        weighted_sum += digit * weight

    return (10 - weighted_sum % 10) % 10


def price_check_digit(value: str) -> int:
    """Get GS1 check digit for a price or weight field.

    Args:
        value: The numeric string to calculate the check digit for.

    Returns:
        The check digit.

    Raises:
        ValueError: If the value isn't numeric.

    References:
        GS1 General Specification, section 7.9.2-7.9.4

    Example:
        >>> from biip.gs1.checksums import price_check_digit
        >>> price_check_digit("2875")
        9
        >>> price_check_digit("14685")
        6
    """
    if not value.isnumeric():
        raise ValueError(f"Expected numeric value, got {value!r}.")

    if len(value) == 4:
        return _four_digit_price_check_digit(value)
    elif len(value) == 5:
        return _five_digit_price_check_digit(value)
    else:
        raise ValueError(f"Expected input of length 4 or 5, got {value!r}.")


def _four_digit_price_check_digit(value: str) -> int:
    digits = list(map(int, list(value)))
    weight_sum = 0
    for digit, weight_map in zip(digits, _FOUR_DIGIT_POSITION_WEIGHTS):
        weight = weight_map[digit]
        weight_sum += weight
    return (weight_sum * 3) % 10


def _five_digit_price_check_digit(value: str) -> int:
    digits = list(map(int, list(value)))
    weighted_sum = 0
    for digit, weight_map in zip(digits, _FIVE_DIGIT_POSITION_WEIGHTS):
        weight = weight_map[digit]
        weighted_sum += weight
    result = (10 - weighted_sum % 10) % 10
    return _FIVE_MINUS_WEIGHT_REVERSE[result]


# See GS1 General Specification, section 7.9.2 for details.
_TWO_MINUS_WEIGHT = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 9, 6: 1, 7: 3, 8: 5, 9: 7}
_THREE_WEIGHT = {0: 0, 1: 3, 2: 6, 3: 9, 4: 2, 5: 5, 6: 8, 7: 1, 8: 4, 9: 7}
_FIVE_PLUS_WEIGHT = {0: 0, 1: 5, 2: 1, 3: 6, 4: 2, 5: 7, 6: 3, 7: 8, 8: 4, 9: 9}
_FIVE_MINUS_WEIGHT = {
    0: 0,
    1: 5,
    2: 9,
    3: 4,
    4: 8,
    5: 3,
    6: 7,
    7: 2,
    8: 6,
    9: 1,
}
_FIVE_MINUS_WEIGHT_REVERSE = {v: k for k, v in _FIVE_MINUS_WEIGHT.items()}

# See GS1 General Specification, section 7.9.3 for details.
_FOUR_DIGIT_POSITION_WEIGHTS = [
    _TWO_MINUS_WEIGHT,
    _TWO_MINUS_WEIGHT,
    _THREE_WEIGHT,
    _FIVE_MINUS_WEIGHT,
]

# See GS1 General Specification, section 7.9.4 for details.
_FIVE_DIGIT_POSITION_WEIGHTS = [
    _FIVE_PLUS_WEIGHT,
    _TWO_MINUS_WEIGHT,
    _FIVE_MINUS_WEIGHT,
    _FIVE_PLUS_WEIGHT,
    _TWO_MINUS_WEIGHT,
]
