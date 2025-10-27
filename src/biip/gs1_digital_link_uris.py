"""Support for GS1 Digital Link URIs.

GS1 Digital Link URIs are HTTPS URIs pointing to any hostname, optionally with a
path prefix, where GS1 element strings are encoded in the path and query
parameters.

Examples of GS1 Digital Link URIs:

- `https://id.gs1.org/01/614141123452/lot/ABC1/ser/12345?exp=180426`
- `https://id.gs1.org/01/614141123452?3103=000195`
- `https://id.gs1.org/00/106141412345678908?02=00614141123452&37=25&10=ABC123`

This makes it possible to use GS1 Digital Link URIs encoded in 2D barcodes both
in supply chain and logistics applications, as well as for consumers to look up
product information.

References:
    https://www.gs1.org/standards/gs1-digital-link

## Example

If you only want to parse GS1 Digital Link URIs, you can import the GS1 Digital
Link URI parser directly instead of using [`biip.parse()`][biip.parse].

    >>> from biip.gs1_digital_link_uris import GS1DigitalLinkURI

If the parsing succeeds, it returns a
[`GS1DigitalLinkURI`][biip.gs1_digital_link_uris.GS1DigitalLinkURI] object.

    >>> dl_uri = GS1DigitalLinkURI.parse("https://id.gs1.org/00/106141412345678908?02=00614141123452&37=25&10=ABC123")

In this case, the URI is parsed into the SSCC of a shipping container, the GTIN
of the product within the shipping container, the number of item within, and the
batch number.

    >>> pprint(dl_uri.element_strings)
    [
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='00',
                description='Serial Shipping Container Code (SSCC)',
                data_title='SSCC',
                separator_required=False,
                format='N2+N18'
            ),
            value='106141412345678908',
            pattern_groups=[
                '106141412345678908'
            ],
            sscc=Sscc(
                value='106141412345678908',
                prefix=GS1Prefix(
                    value='061',
                    usage='GS1 US'
                ),
                company_prefix=GS1CompanyPrefix(
                    value='0614141'
                ),
                extension_digit=1,
                payload='10614141234567890',
                check_digit=8
            )
        ),
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='02',
                description='Global Trade Item Number (GTIN) of contained trade items',
                data_title='CONTENT',
                separator_required=False,
                format='N2+N14'
            ),
            value='00614141123452',
            pattern_groups=[
                '00614141123452'
            ],
            gtin=Gtin(
                value='00614141123452',
                format=GtinFormat.GTIN_12,
                prefix=GS1Prefix(
                    value='061',
                    usage='GS1 US'
                ),
                company_prefix=GS1CompanyPrefix(
                    value='0614141'
                ),
                item_reference='12345',
                payload='61414112345',
                check_digit=2
            )
        ),
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='37',
                description='Count of trade items or trade item pieces contained in a logistic unit',
                data_title='COUNT',
                separator_required=True,
                format='N2+N..8'
            ),
            value='25',
            pattern_groups=[
                '25'
            ]
        ),
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='10',
                description='Batch or lot number',
                data_title='BATCH/LOT',
                separator_required=True,
                format='N2+X..20'
            ),
            value='ABC123',
            pattern_groups=[
                'ABC123'
            ]
        )
    ]
"""  # noqa: E501

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlencode, urlparse, urlunsplit

from biip import ParseConfig, ParseError
from biip._exceptions import EncodeError
from biip.gs1_application_identifiers import (
    _GS1_APPLICATION_IDENTIFIERS,
    GS1ApplicationIdentifier,
)
from biip.gs1_element_strings import GS1ElementString, GS1ElementStrings

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from biip.gs1_messages import GS1Message


@dataclass(frozen=True)
class GS1DigitalLinkURI:
    """A GS1 Digital Link URI is a URI that contains GS1 element strings."""

    value: str
    """Raw unprocessed value."""

    element_strings: GS1ElementStrings
    """List of element strings found in the message.

    See [`GS1ElementStrings`][biip.gs1_element_strings.GS1ElementStrings] for
    methods to extract interesting element strings from the list.
    """

    @classmethod
    def parse(  # noqa: C901
        cls,
        value: str,
        *,
        config: ParseConfig | None = None,
    ) -> GS1DigitalLinkURI:
        """Parse a string as a GS1 Digital Link URI.

        Args:
            value: The string to parse.
            config: The parse configuration.

        Returns:
            The parsed GS1 Digital Link URI.

        Raises:
            ParseError: If the parsing fails.
        """
        if config is None:
            config = ParseConfig()

        parsed = urlparse(value)

        match parsed.scheme:
            case "https" | "http":
                pass
            case "":
                msg = f"Expected URI, got {value!r}."
                raise ParseError(msg)
            case scheme:
                msg = f"Expected URI scheme to be 'http' or 'https', got {scheme!r}."
                raise ParseError(msg)

        # Consume path prefix
        path_parts = parsed.path.split("/")
        while path_parts:
            if path_parts[0] in _PRIMARY_IDENTIFIER_MAP:
                break
            path_parts.pop(0)

        if not path_parts:
            msg = f"Expected a primary identifier in the path, got '{parsed.path}'."
            raise ParseError(msg)

        if len(path_parts) % 2 != 0:
            path = f"/{'/'.join(path_parts)}"
            msg = f"Expected even number of path segments, got {path!r}."
            raise ParseError(msg)

        element_strings = GS1ElementStrings()
        path_pairs = _get_pairs(path_parts)

        # Extract exactly one primary identifier from path
        (pi_key, pi_value) = next(path_pairs)
        pi = _PRIMARY_IDENTIFIER_MAP[pi_key]
        if pi.zfill_to_width:
            pi_value = pi_value.zfill(pi.zfill_to_width)
        element_strings.append(
            GS1ElementString.extract(
                f"{pi.ai.ai}{pi_value}",
                config=config,
            )
        )

        # Extract qualifiers from path
        expected_qualifiers = list(pi.qualifiers)
        for qualifier_key, qualifier_value in path_pairs:
            qualifier = _get_qualifier(qualifier_key, expected_qualifiers)
            element_strings.append(
                GS1ElementString.extract(
                    f"{qualifier.ai.ai}{qualifier_value}",
                    config=config,
                )
            )

        # Extract query string components
        query_pairs = [
            (key, vals[-1])  # If an AI is repeated, the last value is used.
            for key, vals in parse_qs(parsed.query).items()
        ]
        for component_key, component_value in query_pairs:
            ai = _GS1_APPLICATION_IDENTIFIERS.get(component_key)
            if ai is None:
                # Extra query parameters are ignored.
                continue
            element_strings.append(
                GS1ElementString.extract(
                    f"{ai.ai}{component_value}",
                    config=config,
                )
            )

        return cls(value=value, element_strings=element_strings)

    @classmethod
    def from_element_strings(
        cls, element_strings: GS1ElementStrings
    ) -> GS1DigitalLinkURI:
        """Create a GS1 Digital Link URI from a list of GS1 element strings.

        Args:
            element_strings: A list of GS1 element strings.

        Returns:
            GS1DigitalLinkURI: The created GS1 Digital Link URI.
        """
        return GS1DigitalLinkURI(
            value=_build_uri(element_strings),
            element_strings=element_strings,
        )

    def as_uri(
        self,
        *,
        domain: str | None = None,
        prefix: str | None = None,
    ) -> str:
        """Render as a GS1 Digital Link URI.

        Args:
            domain: The domain name to use in the URI. Defaults to `id.gs1.org`.
            prefix: The path prefix to use in the URI. Defaults to no prefix.

        Returns:
            str: The GS1 Digital Link URI.
        """
        return _build_uri(
            self.element_strings,
            domain=domain or "id.gs1.org",
            prefix=prefix,
        )

    def as_canonical_uri(self) -> str:
        """Render as a canonical GS1 Digital Link URI.

        Canonical URIs:

        - Use the domain name `id.gs1.org`.
        - Uses numeric AI values in the URI path.
        - Excludes all query parameters that are not valid application identifiers.

        Returns:
            str: The canonical GS1 Digital Link URI.

        References:
            GS1 Digital Link Standard: URI Syntax, section 4.12
        """
        return _build_uri(self.element_strings)

    def as_gs1_message(self) -> GS1Message:
        """Converts the GS1 Digital Link URI to a GS1 Message."""
        from biip.gs1_messages import GS1Message  # noqa: PLC0415

        return GS1Message.from_element_strings(self.element_strings)


def _get_pairs(iterable: Iterable[str]) -> Iterator[tuple[str, str]]:
    # Replace this function with itertools.batched(v, 2) when we require Python >= 3.12.
    iterator = iter(iterable)
    try:
        while True:
            yield next(iterator), next(iterator)
    except StopIteration:
        return


def _get_qualifier(
    qualifier_key: str,
    expected_qualifiers: list[_Component],
) -> _Component:
    if not expected_qualifiers:
        msg = f"Did not expect a qualifier, got {qualifier_key!r}."
        raise ParseError(msg)
    expected_qualifier_names = ", ".join(f"{eq.ai.ai}" for eq in expected_qualifiers)
    while expected_qualifiers:
        # Consume the expected qualifier, so that they can only be used
        # once, and only in order.
        qualifier = expected_qualifiers.pop(0)
        if qualifier_key == qualifier.ai.ai:
            return qualifier
    msg = (
        f"Expected one of ({expected_qualifier_names}) as qualifier, "
        f"got {qualifier_key!r}."
    )
    raise ParseError(msg)


def _build_uri(
    element_strings: GS1ElementStrings,
    *,
    domain: str = "id.gs1.org",
    prefix: str | None = None,
) -> str:
    primary_identifiers = [
        pi for pi in _PRIMARY_IDENTIFIERS if element_strings.get(ai=pi.ai)
    ]
    match primary_identifiers:
        case []:  # pragma: no cover  # Prevented by the parser.
            msg = "Expected exactly one primary identifier, none found."
            raise EncodeError(msg)
        case [pi]:
            primary_identifier = pi
        case _:  # pragma: no cover  # Prevented by the parser.
            msg = "Expected exactly one primary identifier, multiple found."
            raise EncodeError(msg)
    pi_element_string = element_strings.get(ai=primary_identifier.ai)
    assert pi_element_string

    qualifiers = [
        es
        for q in primary_identifier.qualifiers
        if (es := element_strings.get(ai=q.ai))
    ]

    if prefix is not None:
        if prefix.startswith("/"):
            msg = "Prefix must not start with '/'"
            raise ValueError(msg)
        if prefix.endswith("/"):
            msg = "Prefix must not end with '/'"
            raise ValueError(msg)
        path = prefix
    else:
        path = ""

    path += f"/{pi_element_string.ai.ai}/{pi_element_string.value}"

    for element_string in qualifiers:
        path += f"/{element_string.ai.ai}/{element_string.value}"

    other_element_strings = [
        es for es in element_strings if es not in (pi_element_string, *qualifiers)
    ]
    # Sort params by AI in lexicographical order
    sorted_element_strings = sorted(other_element_strings, key=lambda es: es.ai.ai)
    params: dict[str, str] = {es.ai.ai: es.value for es in sorted_element_strings}

    return urlunsplit(
        [
            "https",
            domain,
            path,
            urlencode(params) if params else None,
            None,
        ]
    )


@dataclass(frozen=True)
class _Component:
    ai: GS1ApplicationIdentifier
    zfill_to_width: int | None = None
    qualifiers: tuple[_Component, ...] = field(default_factory=tuple)


_PRIMARY_IDENTIFIERS = [
    _Component(
        ai=GS1ApplicationIdentifier.extract("01"),  # gtin
        zfill_to_width=14,
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("22")),  # cpv
            _Component(ai=GS1ApplicationIdentifier.extract("10")),  # lot
            _Component(ai=GS1ApplicationIdentifier.extract("21")),  # ser
            _Component(ai=GS1ApplicationIdentifier.extract("235")),  # tpx
        ),
    ),
    _Component(
        ai=GS1ApplicationIdentifier.extract("8006"),  # itip
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("22")),  # cpv
            _Component(ai=GS1ApplicationIdentifier.extract("10")),  # lot
            _Component(ai=GS1ApplicationIdentifier.extract("21")),  # ser
        ),
    ),
    _Component(ai=GS1ApplicationIdentifier.extract("8013")),  # gmn
    _Component(
        ai=GS1ApplicationIdentifier.extract("8010"),  # cpid
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("8011")),  # cpsn
        ),
    ),
    _Component(
        ai=GS1ApplicationIdentifier.extract("414"),  # gln
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("254")),  # glnx
            _Component(ai=GS1ApplicationIdentifier.extract("7040")),  # uic-ext
        ),
    ),
    _Component(
        ai=GS1ApplicationIdentifier.extract("415"),  # payTo
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("8020")),  # refNo
        ),
    ),
    _Component(
        ai=GS1ApplicationIdentifier.extract("417"),  # partyGln
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("7040")),  # uic-ext
        ),
    ),
    _Component(
        ai=GS1ApplicationIdentifier.extract("8017"),  # gsrnp
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("8019")),  # srin
        ),
    ),
    _Component(
        ai=GS1ApplicationIdentifier.extract("8018"),  # gsrn
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("8019")),  # srin
        ),
    ),
    _Component(ai=GS1ApplicationIdentifier.extract("255")),  # gcn
    _Component(ai=GS1ApplicationIdentifier.extract("00")),  # sscc
    _Component(ai=GS1ApplicationIdentifier.extract("253")),  # gdti
    _Component(ai=GS1ApplicationIdentifier.extract("401")),  # ginc
    _Component(ai=GS1ApplicationIdentifier.extract("402")),  # gsin
    _Component(ai=GS1ApplicationIdentifier.extract("8003")),  # grai
    _Component(
        ai=GS1ApplicationIdentifier.extract("8004"),  # giai
        qualifiers=(
            _Component(ai=GS1ApplicationIdentifier.extract("7040")),  # uic-ext
        ),
    ),
]
_PRIMARY_IDENTIFIER_MAP = {pi.ai.ai: pi for pi in _PRIMARY_IDENTIFIERS}
