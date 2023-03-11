"""Script to download and extract Application Identifier data from GS1."""

import dataclasses
import json
from typing import List

import bs4
import httpx

from biip.gs1 import GS1ApplicationIdentifier

AI_URL = "https://www.gs1.org/standards/barcodes/application-identifiers"


def main() -> None:
    """The script's main function."""
    html_content = download(AI_URL)
    application_identifiers = parse(html_content)
    output(application_identifiers)


def download(url: str) -> bytes:
    """Download the data from GS1."""
    return httpx.get(url, timeout=30).content


def parse(html_content: bytes) -> List[GS1ApplicationIdentifier]:
    """Parse the data from HTML to GS1ApplicationIdentifier objects."""
    result: List[GS1ApplicationIdentifier] = []

    page = bs4.BeautifulSoup(html_content, "html.parser")
    datatable = page.find("table", {"class": ["datatable"]})
    assert isinstance(datatable, bs4.element.Tag)
    tbody = datatable.find("tbody")
    assert isinstance(tbody, bs4.element.Tag)

    for row in tbody.find_all("tr"):
        columns = row.find_all("td")
        result.append(
            GS1ApplicationIdentifier(
                ai=columns[0].text.strip(),
                description=columns[1].text.strip(),
                format=columns[2].text.strip(),
                data_title=_fix_data_title(columns[3].text.strip()),
                fnc1_required=columns[4].text.strip() == "Yes",
                pattern=_fix_pattern(columns[5].text.strip()),
            )
        )

    return result


def _fix_data_title(value: str) -> str:
    """Remove HTML elements from the data title."""
    if "<sup>" in value:
        value = value.replace("<sup>", "")
    if "</sup>" in value:
        value = value.replace("</sup>", "")

    return value


def _fix_pattern(value: str) -> str:
    """Fix regular expression metacharacters that are missing their slash prefix."""
    if r"(d" in value:
        value = value.replace(r"(d", r"(\d")

    if "x" in value:
        parts = value.split("x")
        new_parts: List[str] = []
        for part in parts[:-1]:
            if part.endswith("\\"):
                new_parts.append(part)
            else:
                new_parts.append(part + "\\")
        new_parts.append(parts[-1])
        value = "x".join(new_parts)

    return value


def output(application_identifiers: List[GS1ApplicationIdentifier]) -> None:
    """Output the GS1ApplicationIdentifier objects as JSON to stdout."""
    print(
        json.dumps([dataclasses.asdict(ai) for ai in application_identifiers], indent=2)
    )


if __name__ == "__main__":
    main()
