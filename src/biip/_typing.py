from __future__ import annotations

from typing import Never


def assert_never() -> Never:  # pragma: no cover
    msg = "Expected code to be unreachable"
    raise AssertionError(msg)
