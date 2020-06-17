"""Application Identifiers specified by GS1."""

from __future__ import annotations

from typing import Optional


def get_predefined_length(value: str) -> Optional[int]:
    """Get predefined length of element string, including Application Identifier prefix.

    Args:
        value: Any string starting with a GS1 Application Identifier.

    Returns:
        Predefined length or ``None`` if undefined.
    """
    ai_prefix = value[:2]
    return {
        "00": 20,
        "01": 16,
        "02": 16,
        "03": 16,
        "04": 18,
        "11": 8,
        "12": 8,
        "13": 8,
        "14": 8,
        "15": 8,
        "16": 8,
        "17": 8,
        "18": 8,
        "19": 8,
        "20": 4,
        "31": 10,
        "32": 10,
        "33": 10,
        "34": 10,
        "35": 10,
        "36": 10,
        "41": 16,
    }.get(ai_prefix)
