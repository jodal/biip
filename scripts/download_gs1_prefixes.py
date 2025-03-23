"""Script to download and extract Prefix data from GS1."""

import json
from typing import Union

import bs4
import httpx

TrieNode = Union[dict[str, "TrieNode"], tuple[int, str]]  # noqa: UP007

PREFIX_URL = "https://www.gs1.org/standards/id-keys/company-prefix"


def main() -> None:
    """The script's main function."""
    html_content = download(PREFIX_URL)
    trie = parse(html_content)
    output(trie)


def download(url: str) -> bytes:
    """Download the data from GS1."""
    return httpx.get(url, timeout=30).content


def parse(html_content: bytes) -> TrieNode:
    """Parse the data from HTML to _GS1PrefixRange objects."""
    trie: TrieNode = {}

    page = bs4.BeautifulSoup(html_content, "html.parser")
    datatable = page.find("table", {"class": ["table"]})
    assert isinstance(datatable, bs4.element.Tag)
    tbody = datatable.find("tbody")
    assert isinstance(tbody, bs4.element.Tag)

    for row in tbody.find_all("tr"):
        columns = row.find_all("td")

        prefixes: str = columns[0].text.strip()
        usage: str = columns[1].text.strip()

        # Standardize separator between ranges
        prefixes = prefixes.replace("  ", "&")

        # Standardize separator between range ends
        prefixes = prefixes.replace("\u2013", "-")

        # Strip note references from end of usage description
        if ", see" in usage:
            note_start = usage.index(", see")
            usage = usage[:note_start]

        for range_ in prefixes.split("&"):
            if "-" in range_:
                start, end = map(str.strip, range_.split("-"))
            else:
                start, end = range_.strip(), range_.strip()

            length = len(start)
            min_value = int(start)
            max_value = int(end)

            # Build/traverse the trie
            for prefix in range(min_value, max_value + 1):
                node: TrieNode = trie
                digits = list(str(prefix).zfill(length))
                while digits:
                    assert isinstance(node, dict)
                    digit = digits.pop(0)
                    if digits:
                        if digit not in node:
                            node[digit] = {}
                        node = node[digit]
                    else:
                        node[digit] = (length, usage)

    # Exceptions defined in the GS1 prefix table's footnotes
    trie["9"]["6"]["0"] = (3, "GS1 UK - GTIN-8")  # type: ignore  # noqa: PGH003
    trie["9"]["6"]["1"] = (3, "GS1 UK - GTIN-8")  # type: ignore  # noqa: PGH003
    trie["9"]["6"]["2"] = {  # type: ignore  # noqa: PGH003
        "0": (4, "GS1 UK - GTIN-8"),
        "1": (4, "GS1 UK - GTIN-8"),
        "2": (4, "GS1 UK - GTIN-8"),
        "3": (4, "GS1 UK - GTIN-8"),
        "4": (4, "GS1 UK - GTIN-8"),
        "5": (4, "GS1 Poland - GTIN-8"),
        "6": (4, "GS1 Poland - GTIN-8"),
        "7": (4, "GS1 Global Office - GTIN-8"),
        "8": (4, "GS1 Global Office - GTIN-8"),
        "9": (4, "GS1 Global Office - GTIN-8"),
    }

    return trie


def output(trie: TrieNode) -> None:
    """Output the trie data structure as JSON to stdout."""
    print(json.dumps(trie, indent=2))


if __name__ == "__main__":
    main()
