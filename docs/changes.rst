=======
Changes
=======


v0.2 (UNRELEASED)
=================

:mod:`biip.gs1`

- :class:`~biip.gs1.GS1Message` can parse GS1-128 numbers.
- :class:`~biip.gs1.GS1ApplicationIdentifier` recognizes all 480 existing GS1 AIs.
- :class:`~biip.gs1.GS1Prefix` recognizes all existing GS1 prefixes.
- :mod:`~biip.gs1.checksum` has functions to calculate check digits for
  numeric data and price/weight fields.

:mod:`biip.gtin`

- Support for validating, parsing, and converting between GTIN-8, GTIN-12,
  GTIN-13, and GTIN-14.


v0.1 (2020-05-20)
=================

Initial release to reserve the name on PyPI.
