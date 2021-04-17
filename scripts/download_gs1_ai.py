"""Script to download and extract Application Identifier data from GS1."""

import dataclasses
import json
from typing import List

import requests
from bs4 import BeautifulSoup

from biip.gs1 import GS1ApplicationIdentifier

AI_URL = "https://www.gs1.org/standards/barcodes/application-identifiers"


def main() -> None:
    """The script's main function."""
    html_content = download(AI_URL)
    application_identifiers = parse(html_content)
    output(application_identifiers)


def download(url: str) -> str:
    """Download the data from GS1."""
    return requests.get(url).content


def parse(html_content: str) -> List[GS1ApplicationIdentifier]:
    """Parse the data from HTML to GS1ApplicationIdentifier objects."""
    result = []

    page = BeautifulSoup(html_content, "html.parser")
    datatable = page.find("table", {"class": ["datatable"]})
    tbody = datatable.find("tbody")

    for row in tbody.find_all("tr"):
        columns = row.find_all("td")
        result.append(
            GS1ApplicationIdentifier(
                ai=columns[0].text.strip(),
                description=columns[1].text.strip(),
                format=columns[2].text.strip(),
                data_title=columns[3].text.strip(),
                fnc1_required=columns[4].text.strip() == "Yes",
                pattern=columns[5].text.strip(),
            )
        )

    return result


def output(application_identifiers: List[GS1ApplicationIdentifier]) -> None:
    """Output the GS1ApplicationIdentifier objects as JSON to stdout."""
    print(
        json.dumps(
            [dataclasses.asdict(ai) for ai in application_identifiers], indent=2
        )
    )


if __name__ == "__main__":
    main()
