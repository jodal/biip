"""Script to download and extract Application Identifier data from GS1."""

import dataclasses
import json

import httpx

from biip.gs1 import GS1ApplicationIdentifier

AI_URL = "https://ref.gs1.org/ai/GS1_Application_Identifiers.jsonld"


def main() -> None:
    """The script's main function."""
    html_content = download(AI_URL)
    application_identifiers = parse(html_content)
    output(application_identifiers)


def download(url: str) -> bytes:
    """Download the data from GS1."""
    return httpx.get(url, timeout=30).content


def parse(json_content: bytes) -> list[GS1ApplicationIdentifier]:
    """Parse the data from HTML to GS1ApplicationIdentifier objects."""
    result: list[GS1ApplicationIdentifier] = []

    data = json.loads(json_content)

    for row in data["applicationIdentifiers"]:
        if "applicationIdentifier" not in row:
            continue
        result.append(
            GS1ApplicationIdentifier(
                ai=row["applicationIdentifier"],
                description=row["description"],
                format=row["formatString"],
                data_title=row["title"],
                fnc1_required=row["fnc1required"],
                pattern=rf"^{row['applicationIdentifier']}{_fix_pattern(row['regex'])}$",
            )
        )

    return result


def _fix_pattern(value: str) -> str:
    """Fix errors in regex patterns."""
    # Add missing opening square bracket to the regex for AI 723x
    if value == r"(!%-?A-Z_a-z\x22]{3,30})":
        return r"([!%-?A-Z_a-z\x22]{3,30})"
    return value


def output(application_identifiers: list[GS1ApplicationIdentifier]) -> None:
    """Output the GS1ApplicationIdentifier objects as JSON to stdout."""
    print(
        json.dumps([dataclasses.asdict(ai) for ai in application_identifiers], indent=2)
    )


if __name__ == "__main__":
    main()
