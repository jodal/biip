"""Test setup for doctests."""

# For the fixture to be available when running doctests, this file must be placed
# in the `src/` tree or outside of it, not in the `tests/` tree.

from typing import Any

import pytest
from rich.pretty import pprint


def doctest_print(*args: Any) -> None:  # noqa: ANN401, D103
    return pprint(
        *args,
        expand_all=True,
        indent_guides=False,
    )


@pytest.fixture(autouse=True, scope="session")
def pprint_setup(doctest_namespace: dict[str, Any]) -> None:  # noqa: D103
    doctest_namespace["pprint"] = doctest_print
