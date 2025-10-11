from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from typing import Never  # pragma: no cover
else:
    from typing_extensions import Never  # pragma: no cover


def assert_never() -> Never:  # pragma: no cover
    msg = "Expected code to be unreachable"
    raise AssertionError(msg)
