"""Barcode prefixes allocated by GS1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from biip import ParseError


@dataclass
class _GS1PrefixRange:
    length: int
    min_value: int
    max_value: int
    usage: str


_GS1_PREFIX_RANGES = [
    _GS1PrefixRange(
        7, 0, 0, "Used to issue Restricted Circulation Numbers within a company"
    ),
    _GS1PrefixRange(7, 1, 99, "Unused to avoid collision with GTIN-8"),
    _GS1PrefixRange(5, 1, 9, "GS1 US"),
    _GS1PrefixRange(4, 1, 9, "GS1 US"),
    _GS1PrefixRange(3, 1, 19, "GS1 US"),
    _GS1PrefixRange(
        3,
        20,
        29,
        "Used to issue Restricted Circulation Numbers "
        "within a geographic region (MO defined)",
    ),
    _GS1PrefixRange(3, 30, 39, "GS1 US"),
    _GS1PrefixRange(
        3,
        40,
        49,
        "Used to issue GS1 Restricted Circulation Numbers within a company",
    ),
    _GS1PrefixRange(3, 50, 59, "GS1 US reserved for future use"),
    _GS1PrefixRange(3, 60, 139, "GS1 US"),
    _GS1PrefixRange(
        3,
        200,
        299,
        "Used to issue Restricted Circulation Numbers "
        "within a geographic region (MO defined)",
    ),
    _GS1PrefixRange(3, 300, 379, "GS1 France"),
    _GS1PrefixRange(3, 380, 380, "GS1 Bulgaria"),
    _GS1PrefixRange(3, 383, 383, "GS1 Slovenija"),
    _GS1PrefixRange(3, 385, 385, "GS1 Croatia"),
    _GS1PrefixRange(3, 387, 387, "GS1 BIH (Bosnia-Herzegovina)"),
    _GS1PrefixRange(3, 389, 389, "GS1 Montenegro"),
    _GS1PrefixRange(3, 400, 440, "GS1 Germany"),
    _GS1PrefixRange(3, 450, 459, "GS1 Japan"),
    _GS1PrefixRange(3, 490, 499, "GS1 Japan"),
    _GS1PrefixRange(3, 460, 469, "GS1 Russia"),
    _GS1PrefixRange(3, 470, 470, "GS1 Kyrgyzstan"),
    _GS1PrefixRange(3, 471, 471, "GS1 Chinese Taipei"),
    _GS1PrefixRange(3, 474, 474, "GS1 Estonia"),
    _GS1PrefixRange(3, 475, 475, "GS1 Latvia"),
    _GS1PrefixRange(3, 476, 476, "GS1 Azerbaijan"),
    _GS1PrefixRange(3, 477, 477, "GS1 Lithuania"),
    _GS1PrefixRange(3, 478, 478, "GS1 Uzbekistan"),
    _GS1PrefixRange(3, 479, 479, "GS1 Sri Lanka"),
    _GS1PrefixRange(3, 480, 480, "GS1 Philippines"),
    _GS1PrefixRange(3, 481, 481, "GS1 Belarus"),
    _GS1PrefixRange(3, 482, 482, "GS1 Ukraine"),
    _GS1PrefixRange(3, 483, 483, "GS1 Turkmenistan"),
    _GS1PrefixRange(3, 484, 484, "GS1 Moldova"),
    _GS1PrefixRange(3, 485, 485, "GS1 Armenia"),
    _GS1PrefixRange(3, 486, 486, "GS1 Georgia"),
    _GS1PrefixRange(3, 487, 487, "GS1 Kazakstan"),
    _GS1PrefixRange(3, 488, 488, "GS1 Tajikistan"),
    _GS1PrefixRange(3, 489, 489, "GS1 Hong Kong, China"),
    _GS1PrefixRange(3, 500, 509, "GS1 UK"),
    _GS1PrefixRange(3, 520, 521, "GS1 Association Greece"),
    _GS1PrefixRange(3, 528, 528, "GS1 Lebanon"),
    _GS1PrefixRange(3, 529, 529, "GS1 Cyprus"),
    _GS1PrefixRange(3, 530, 530, "GS1 Albania"),
    _GS1PrefixRange(3, 531, 531, "GS1 Macedonia"),
    _GS1PrefixRange(3, 535, 535, "GS1 Malta"),
    _GS1PrefixRange(3, 539, 539, "GS1 Ireland"),
    _GS1PrefixRange(3, 540, 549, "GS1 Belgium & Luxembourg"),
    _GS1PrefixRange(3, 560, 560, "GS1 Portugal"),
    _GS1PrefixRange(3, 569, 569, "GS1 Iceland"),
    _GS1PrefixRange(3, 570, 579, "GS1 Denmark"),
    _GS1PrefixRange(3, 590, 590, "GS1 Poland"),
    _GS1PrefixRange(3, 594, 594, "GS1 Romania"),
    _GS1PrefixRange(3, 599, 599, "GS1 Hungary"),
    _GS1PrefixRange(3, 600, 601, "GS1 South Africa"),
    _GS1PrefixRange(3, 603, 603, "GS1 Ghana"),
    _GS1PrefixRange(3, 604, 604, "GS1 Senegal"),
    _GS1PrefixRange(3, 608, 608, "GS1 Bahrain"),
    _GS1PrefixRange(3, 609, 609, "GS1 Mauritius"),
    _GS1PrefixRange(3, 611, 611, "GS1 Morocco"),
    _GS1PrefixRange(3, 613, 613, "GS1 Algeria"),
    _GS1PrefixRange(3, 615, 615, "GS1 Nigeria"),
    _GS1PrefixRange(3, 616, 616, "GS1 Kenya"),
    _GS1PrefixRange(3, 617, 617, "GS1 Cameroon"),
    _GS1PrefixRange(3, 618, 618, "GS1 Côte d'Ivoire"),
    _GS1PrefixRange(3, 619, 619, "GS1 Tunisia"),
    _GS1PrefixRange(3, 620, 620, "GS1 Tanzania"),
    _GS1PrefixRange(3, 621, 621, "GS1 Syria"),
    _GS1PrefixRange(3, 622, 622, "GS1 Egypt"),
    _GS1PrefixRange(3, 623, 623, "GS1 Brunei"),
    _GS1PrefixRange(3, 624, 624, "GS1 Libya"),
    _GS1PrefixRange(3, 625, 625, "GS1 Jordan"),
    _GS1PrefixRange(3, 626, 626, "GS1 Iran"),
    _GS1PrefixRange(3, 627, 627, "GS1 Kuwait"),
    _GS1PrefixRange(3, 628, 628, "GS1 Saudi Arabia"),
    _GS1PrefixRange(3, 629, 629, "GS1 Emirates"),
    _GS1PrefixRange(3, 640, 649, "GS1 Finland"),
    _GS1PrefixRange(3, 690, 699, "GS1 China"),
    _GS1PrefixRange(3, 700, 709, "GS1 Norway"),
    _GS1PrefixRange(3, 729, 729, "GS1 Israel"),
    _GS1PrefixRange(3, 730, 739, "GS1 Sweden"),
    _GS1PrefixRange(3, 740, 740, "GS1 Guatemala"),
    _GS1PrefixRange(3, 741, 741, "GS1 El Salvador"),
    _GS1PrefixRange(3, 742, 742, "GS1 Honduras"),
    _GS1PrefixRange(3, 743, 743, "GS1 Nicaragua"),
    _GS1PrefixRange(3, 744, 744, "GS1 Costa Rica"),
    _GS1PrefixRange(3, 745, 745, "GS1 Panama"),
    _GS1PrefixRange(3, 746, 746, "GS1 Republica Dominicana"),
    _GS1PrefixRange(3, 750, 750, "GS1 Mexico"),
    _GS1PrefixRange(3, 754, 755, "GS1 Canada"),
    _GS1PrefixRange(3, 759, 759, "GS1 Venezuela"),
    _GS1PrefixRange(3, 760, 769, "GS1 Schweiz, Suisse, Svizzera"),
    _GS1PrefixRange(3, 770, 771, "GS1 Colombia"),
    _GS1PrefixRange(3, 773, 773, "GS1 Uruguay"),
    _GS1PrefixRange(3, 775, 775, "GS1 Peru"),
    _GS1PrefixRange(3, 777, 777, "GS1 Bolivia"),
    _GS1PrefixRange(3, 778, 779, "GS1 Argentina"),
    _GS1PrefixRange(3, 780, 780, "GS1 Chile"),
    _GS1PrefixRange(3, 784, 784, "GS1 Paraguay"),
    _GS1PrefixRange(3, 786, 786, "GS1 Ecuador"),
    _GS1PrefixRange(3, 789, 790, "GS1 Brasil"),
    _GS1PrefixRange(3, 800, 839, "GS1 Italy"),
    _GS1PrefixRange(3, 840, 849, "GS1 Spain"),
    _GS1PrefixRange(3, 850, 850, "GS1 Cuba"),
    _GS1PrefixRange(3, 858, 858, "GS1 Slovakia"),
    _GS1PrefixRange(3, 859, 859, "GS1 Czech"),
    _GS1PrefixRange(3, 860, 860, "GS1 Serbia"),
    _GS1PrefixRange(3, 865, 865, "GS1 Mongolia"),
    _GS1PrefixRange(3, 867, 867, "GS1 North Korea"),
    _GS1PrefixRange(3, 868, 869, "GS1 Turkey"),
    _GS1PrefixRange(3, 870, 879, "GS1 Netherlands"),
    _GS1PrefixRange(3, 880, 880, "GS1 South Korea"),
    _GS1PrefixRange(3, 883, 883, "GS1 Myanmar"),
    _GS1PrefixRange(3, 884, 884, "GS1 Cambodia"),
    _GS1PrefixRange(3, 885, 885, "GS1 Thailand"),
    _GS1PrefixRange(3, 888, 888, "GS1 Singapore"),
    _GS1PrefixRange(3, 890, 890, "GS1 India"),
    _GS1PrefixRange(3, 893, 893, "GS1 Vietnam"),
    _GS1PrefixRange(3, 896, 896, "GS1 Pakistan"),
    _GS1PrefixRange(3, 899, 899, "GS1 Indonesia"),
    _GS1PrefixRange(3, 900, 919, "GS1 Austria"),
    _GS1PrefixRange(3, 930, 939, "GS1 Australia"),
    _GS1PrefixRange(3, 940, 949, "GS1 New Zealand"),
    _GS1PrefixRange(3, 950, 950, "GS1 Global Office"),
    _GS1PrefixRange(3, 951, 951, "Global Office - General Manager Number"),
    _GS1PrefixRange(
        3, 952, 952, "Used for demonstrations and examples of the GS1 system"
    ),
    _GS1PrefixRange(3, 955, 955, "GS1 Malaysia"),
    _GS1PrefixRange(3, 958, 958, "GS1 Macau, China"),
    _GS1PrefixRange(3, 960, 969, "Global Office - GTIN-8"),
    _GS1PrefixRange(3, 977, 977, "Serial publications (ISSN)"),
    _GS1PrefixRange(3, 978, 979, "Bookland (ISBN)"),
    _GS1PrefixRange(3, 980, 980, "Refund receipts"),
    _GS1PrefixRange(
        3, 981, 984, "GS1 coupon identification for common currency areas"
    ),
    _GS1PrefixRange(2, 99, 99, "GS1 coupon identification"),
]


@dataclass
class GS1Prefix:
    """Prefix assigned by GS1.

    Source: https://www.gs1.org/standards/id-keys/company-prefix
    """

    #: The prefix itself.
    value: str

    #: Description of who is using the prefix.
    usage: str

    @classmethod
    def extract(cls: Type[GS1Prefix], value: str) -> GS1Prefix:
        """Extract the GS1 Prefix from the given value.

        Args:
            value: The string to extract a GS1 Prefix from.

        Returns:
            Metadata about the extracted prefix.

        Raises:
            ParseError: If the parsing fails.
        """
        for prefix_range in _GS1_PREFIX_RANGES:
            prefix = value[: prefix_range.length]

            if not prefix.isnumeric():
                continue
            number = int(prefix)

            if prefix_range.min_value <= number <= prefix_range.max_value:
                return cls(value=prefix, usage=prefix_range.usage)

        raise ParseError(f"Failed to get GS1 Prefix from {value!r}.")
