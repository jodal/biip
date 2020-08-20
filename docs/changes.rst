=======
Changes
=======

v0.3.0 (UNRELEASED)
===================

:mod:`biip.gs1`

- Add :meth:`~biip.gs1.GS1Message.filter` to find all parsed Element Strings
  that matches the criteria.

- Add :meth:`~biip.gs1.GS1Message.get` to find first parsed Element String
  that matches the criteria.

- Add :attr:`~biip.gs1.GS1ElementString.decimal` field which is set for
  AIs with weight, volume, dimensions, dicount percentages, and amounts
  payable.

- Add :attr:`~biip.gs1.GS1ElementString.money` field which is set for AIs
  with both amounts payable and currency. This field is only set if the
  optional dependency ``py-moneyed`` is installed.

:mod:`biip.gtin`

- Detect Restricted Circulation Numbers (RCN) and return a subclass of
  :class:`~biip.gtin.Gtin`, :class:`~biip.gtin.Rcn`, with additional fields and
  helpers for working with RCNs.

- Classify a RCN as being restricted to either a geographical region or to a
  company.

- Support interpreting RCNs according to varying rules depending on the
  geopgraphical region specified by the user.

- Support for zeroing out the variable measure part, to help with looking up
  trade items in a database or similar.

- Add RCN rules for the Baltics, Great Britain, Norway, and Sweden.

- Bug fix: Keep all leading zeros in GTIN-8.

- Bug fix: Convert GTIN-8 to GTIN-12 before extracting GS1 Prefix.


v0.2.1 (2020-08-19)
===================

:mod:`biip.gtin`

- Raise :exc:`~biip.ParseError` if there is less than 8 or more than 14
  significant digits in the barcode.


v0.2.0 (2020-08-19)
===================

:mod:`biip`

- :func:`~biip.parse` can parse GTIN and GS1-128 data.

:mod:`biip.gs1`

- :class:`~biip.gs1.GS1Message` can parse GS1-128 data.
- :class:`~biip.gs1.GS1ApplicationIdentifier` recognizes all 480 existing GS1 AIs.
- :class:`~biip.gs1.GS1Prefix` recognizes all existing GS1 prefixes.
- :mod:`~biip.gs1.checksums` has functions to calculate check digits for
  numeric data and price/weight fields.

:mod:`biip.gtin`

- Support for validating, parsing, and converting between GTIN-8, GTIN-12,
  GTIN-13, and GTIN-14.


v0.1.0 (2020-05-20)
===================

Initial release to reserve the name on PyPI.
