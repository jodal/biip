=======
Changes
=======

v0.6.2 (2021-01-19)
===================

- Add ``py.typed`` marker file, as specified in PEP561, as Biip is fully typed.

v0.6.1 (2020-12-07)
===================

- Fix documentation build.

- Fix ``__all__`` export of :attr:`biip.DEFAULT_SEPARATOR_CHARS`.

v0.6.0 (2020-12-06)
===================

- Add Python 3.6 support, using the ``dataclasses`` backport for Python 3.6.

- Add Python 3.9 to the test matrix.

v0.5.2 (2020-09-04)
===================

- Bugfix: Add zero in front of GTIN-12 before extracting GS1 Prefix.
  GTIN-12s start with U.P.C. Company Prefixes, which have to be padded with a
  zero in front to convert them to valid GS1 Company Prefixes.

- Change the error message in the top level parser's :class:`~biip.ParseError`
  to include the name of data type we failed to parse.

v0.5.1 (2020-09-03)
===================

- Bugfix: :meth:`biip.gtin.Rcn.without_variable_measure` returns the instance
  unchanged for RCNs intended for usage within a company. Previously, this
  crashed as :attr:`~biip.gtin.Rcn.region` was unset for company RCNs.

v0.5.0 (2020-09-03)
===================

- **Breaking change:** Change argument `separator_char` to `separator_chars` in
  plural, accepting an iterable of multiple characters.

v0.4.0 (2020-08-31)
===================

- Add :doc:`quickstart` guide.

:mod:`biip`

- **Breaking change:** Change return value of :meth:`~biip.parse` from
  ``Union[Gtin, GS1Message]`` to :class:`~biip.ParseResult`.

- If a Symbology Identifier is present, select parser based on it.

- Improved parsing error messages.

:mod:`biip.sscc`

- Add :class:`~biip.sscc.Sscc` class to parse, validate, and format Serial
  Shipping Container Codes (SSCC).

:mod:`biip.symbology`

- Add support for parsing and stripping Symbology Identifiers.

v0.3.1 (2020-08-21)
===================

:mod:`biip`

- Strip surrounding whitespace before selecting parser.

v0.3.0 (2020-08-21)
===================

:mod:`biip.gs1`

- Add :meth:`~biip.gs1.GS1Message.filter` to find all parsed Element Strings
  that match the criteria.

- Add :meth:`~biip.gs1.GS1Message.get` to find first parsed Element String
  that matches the criteria.

- Add :attr:`~biip.gs1.GS1ElementString.decimal` field which is set for
  AIs with weight, volume, dimensions, dicount percentages, and amounts
  payable.

- Add :attr:`~biip.gs1.GS1ElementString.money` field which is set for AIs
  with both amounts payable and currency. This field is only set if the
  optional dependency ``py-moneyed`` is installed.

- Strip surrounding whitespace before parsing.

:mod:`biip.gtin`

- Detect Restricted Circulation Numbers (RCN) and return a subclass of
  :class:`~biip.gtin.Gtin`, :class:`~biip.gtin.Rcn`, with additional fields and
  helpers for working with RCNs.

- Classify an RCN as being restricted to either a geographical region or to a
  company.

- Support interpreting RCNs according to varying rules depending on the
  geographical region specified by the user.

- Support for zeroing out the variable measure part, to help with looking up
  trade items in a database or similar.

- Add RCN rules for the Baltics, Great Britain, Norway, and Sweden.

- Strip surrounding whitespace before parsing.

- Bugfix: Keep all leading zeros in GTIN-8.

- Bugfix: Convert GTIN-8 to GTIN-12 before extracting GS1 Prefix.


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
