"""Script to download and extract Company Prefix data from GS1."""

import json
from typing import Dict, Union
from xml.etree import ElementTree  # noqa: ICN001

import httpx

TrieNode = Union[Dict[str, "TrieNode"], int]

COMPANY_PREFIX_URL = "https://www.gs1.org/docs/gcp_length/gcpprefixformatlist.xml"


def main() -> None:
    """The script's main function."""
    xml_content = download(COMPANY_PREFIX_URL)
    trie = parse(xml_content)
    output(trie)


def download(url: str) -> bytes:
    """Download the data from GS1."""
    return httpx.get(url, timeout=30).content


def parse(xml_content: bytes) -> TrieNode:
    """Parse the data from XML to a trie to make prefix length lookup easy."""
    trie: TrieNode = {}

    doc = ElementTree.fromstring(xml_content)  # noqa: S314
    for entry in doc.findall("entry"):
        shared_prefix = entry.attrib["prefix"]
        company_prefix_length = int(entry.attrib["gcpLength"])

        # Build/traverse the trie
        node: TrieNode = trie
        digits = list(shared_prefix)
        while digits:
            assert isinstance(node, dict)
            digit = digits.pop(0)
            if digits:
                if digit not in node:
                    node[digit] = {}
                node = node[digit]
            else:
                node[digit] = company_prefix_length

    return trie


def output(trie: TrieNode) -> None:
    """Output the trie data structure as JSON to stdout."""
    print(json.dumps(trie, indent=2))


if __name__ == "__main__":
    main()
