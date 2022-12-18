"""Script to download and extract Company Prefix data from GS1."""

import dataclasses
import json
from typing import List

import httpx
from bs4 import BeautifulSoup

from biip.gs1._prefixes import _GS1PrefixRange

COMPANY_PREFIX_URL = "https://www.gs1.org/standards/id-keys/company-prefix"


def main() -> None:
    """The script's main function."""
    html_content = download(COMPANY_PREFIX_URL)
    company_prefixes: List[_GS1PrefixRange] = parse(html_content)
    output(company_prefixes)


def download(url: str) -> bytes:
    """Download the data from GS1."""
    return httpx.get(url, timeout=30).content


def parse(html_content: bytes) -> List[_GS1PrefixRange]:
    """Parse the data from HTML to _GS1PrefixRange objects."""
    result = []

    page = BeautifulSoup(html_content, "html.parser")
    datatable = page.find("table", {"class": ["table"]})
    tbody = datatable.find("tbody")

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

        for range in prefixes.split("&"):
            if "-" in range:
                start, end = map(str.strip, range.split("-"))
            else:
                start, end = range.strip(), range.strip()

            length = len(start)
            min_value = int(start)
            max_value = int(end)

            result.append(
                _GS1PrefixRange(
                    length=length,
                    min_value=min_value,
                    max_value=max_value,
                    usage=usage,
                )
            )

    # Remove duplicates
    result = list(set(result))

    # Order prefixes
    result = sorted(result, key=lambda pr: str(pr.min_value).zfill(pr.length))

    return result


def output(company_prefixes: List[_GS1PrefixRange]) -> None:
    """Output the _GS1PrefixRange objects as JSON to stdout."""
    print(json.dumps([dataclasses.asdict(cp) for cp in company_prefixes], indent=2))


if __name__ == "__main__":
    main()
