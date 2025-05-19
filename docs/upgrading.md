# Upgrading

When major versions of Biip are released, we try to keep the upgrade path as
smooth as possible. However, there are some breaking changes that you need to
consider when upgrading from one major version to another.

## Upgrading from 4.x to 5.x

### GS1 Web URIs are now GS1 Digital Link URIs

GS1 Digital Link standard v1.1 renamed the concept from "Web URI" to "Digital
Link URI". The corresponding APIs in Biip have been renamed.

- `biip.ParseResult.gs1_web_uri` field has moved to
  [`biip.ParseResult.gs1_digital_link_uri`][biip.ParseResult.gs1_digital_link_uri]
  (PR #396)

- `biip.ParseResult.gs1_web_uri_error` field has moved to
  [`biip.ParseResult.gs1_digital_link_uri_error`][biip.ParseResult.gs1_digital_link_uri_error]
  (PR #396)

- `biip.gs1_messages.GS1Message.as_gs1_web_uri()` has moved to
  [`biip.gs1_messages.GS1Message.as_gs1_digital_link_uri()`][biip.gs1_messages.GS1Message.as_gs1_digital_link_uri]
  (PR #396)

- `biip.gs1_web_uris.GS1WebURI` has moved to
  [`biip.gs1_digital_link_uris.GS1DigitalLinkURI`][biip.gs1_digital_link_uris.GS1DigitalLinkURI]
  (PR #396)

- `biip.symbology.GS1Symbology.with_gs1_web_uri()` has moved to
  [`biip.symbology.GS1Symbology.with_gs1_digital_link_uri()`][biip.symbology.GS1Symbology.with_gs1_digital_link_uri]
  (PR #396)

### GS1 Application Identifier aliases in URIs are not supported

GS1 Digital Link standard v1.2 deprecated and v1.3 removed the concept of
aliases. Biip no longer supports aliases in URIs, as this is recommended to not
support in newer implementations to reduce complexity.

That is, the following is not supported:

```
https://id.gs1.org/gtin/07032069804988100329/lot/ABC
```

But this is supported:

```
https://id.gs1.org/01/07032069804988100329/10/ABC
```

(Fixes: #394, PR: #396)

## Upgrading from 3.x to 4.x

### Result objects are immutable

All the dataclasses returned by Biip are now immutable. This means that you can
no longer set attributes on them after they are created.

### `biip.parse()` no longer raises `ParseError`

[`biip.parse()`][biip.parse] no longer raises [`ParseError`][biip.ParseError]
when all parsers fail. This means that you can remove the `try/except` block
around any calls to `biip.parse()` and base your logic on the returned
[`ParseResult`][biip.ParseResult]. (PR #376)

### All config passed via `ParseConfig`

All parser configuration options have been moved to the
[`ParseConfig`][biip.ParseConfig] class. (PR #385)

Look for anywhere you use the old configuration options:

- `rcn_region`,
- `rcn_verify_variable_measure`, or
- `separator_chars`

and replace them with a [`ParseConfig`][biip.ParseConfig] instance.
For example, if you previously used:

```python
result = biip.parse("0107032069804988100329|15210525", separator_chars=["|"])
```

You should now use:

```python
config = biip.ParseConfig(separator_chars=["|"])
result = biip.parse("0107032069804988100329|15210525", config=config)
```

### `biip.gs1` module

- `biip.gs1.checksums.numeric_check_digit()` function has moved to
  [`biip.checksums.gs1_standard_check_digit()`][biip.checksums.gs1_standard_check_digit]
  (PR #375)

- `biip.gs1.checksums.price_check_digit()` function has moved to
  [`biip.checksums.gs1_price_weight_check_digit()`][biip.checksums.gs1_price_weight_check_digit]
  (PR #375)

- `biip.gs1.GS1ApplicationIdentifier` class has moved to
  [`biip.gs1_application_identifiers.GS1ApplicationIdentifier`][biip.gs1_application_identifiers.GS1ApplicationIdentifier]
  (PR #380)

- `biip.gs1.GS1ApplicationIdentifier.fnc1_required` field has moved to
  [`biip.gs1_application_identifiers.GS1ApplicationIdentifier.separator_required`][biip.gs1_application_identifiers.GS1ApplicationIdentifier.separator_required]
  (PR #382)

- `biip.gs1.GS1CompanyPrefix` class has moved to
  [`biip.gs1_prefixes.GS1CompanyPrefix`][biip.gs1_prefixes.GS1CompanyPrefix]
  (PR #380)

- `biip.gs1.GS1ElementString` class has moved to
  [`biip.gs1_element_strings.GS1ElementString`][biip.gs1_element_strings.GS1ElementString]
  (PR #380, #388)

- `biip.gs1.GS1Message` class has moved to
  [`biip.gs1_messages.GS1Message`][biip.gs1_messages.GS1Message]
  (PR #380)

- `biip.gs1.GS1Message.filter()` method has moved to
  [`biip.gs1_element_strings.GS1ElementStrings.filter()`][biip.gs1_element_strings.GS1ElementStrings.filter]
  (PR #391).
  Change any use of `gs1_message.filter()` to
  `gs1_message.element_strings.filter()`.

- `biip.gs1.GS1Message.get()` method has moved to
  [`biip.gs1_element_strings.GS1ElementStrings.get()`][biip.gs1_element_strings.GS1ElementStrings.get]
  (PR #391)
  Change any use of `gs1_message.get()` to `gs1_message.element_strings.get()`.

- `biip.gs1.GS1Prefix` class has moved to
  [`biip.gs1_prefixes.GS1Prefix`][biip.gs1_prefixes.GS1Prefix]
  (PR #380)

- `biip.gs1.GS1Symbology` class has moved to
  [`biip.symbology.GS1Symbology`][biip.symbology.GS1Symbology]
  (PR #379)

- `biip.gs1.GS1Symbology.with_ai_element_strings()` method has moved to
  [`biip.symbology.GS1Symbology.with_gs1_messages()`][biip.symbology.GS1Symbology.with_gs1_messages]
  (PR #392)

### `biip.gtin` module

- `biip.gtin.Rcn` class has moved to
  [`biip.rcn.Rcn`][biip.rcn.Rcn]
  (PR #381)

- `biip.gtin.RcnRegion` class has moved to
  [`biip.rcn.RcnRegion`][biip.rcn.RcnRegion]
  (PR #381)

- `biip.gtin.RcnUsage` class has moved to
  [`biip.rcn.RcnUsage`][biip.rcn.RcnUsage]
  (PR #381)

### `biip.symbology` module

- `biip.symbology.Symbology` class has moved to
  [`biip.symbology.ISOSymbology`][biip.symbology.ISOSymbology]
  (PR #379)

- `biip.symbology.SymbologyIdentifier.symbology` field has moved to
  [`biip.symbology.SymbologyIdentifier.iso_symbology`][biip.symbology.SymbologyIdentifier.iso_symbology]
  (PR #379)

## Upgrading from 2.x to 3.x

### Errors in GS1 element string data

Parsing and validation errors of GLNs, GTINs, and SSCCs nested inside GS1
element strings no longer raises [`ParseError`][biip.ParseError]. Instead, the
exception message is exposed on the
[`GS1ElementString`][biip.gs1_element_strings.GS1ElementString] class as the new
fields `gln_error`, `gtin_error`, and `sscc_error`.

This is a breaking change, but makes it possible to extract some information
from GS1 Element Strings that are not entirely valid.
(Fixes: #157, PR: #169)

### Removed APIs

- Removed `RcnRegion.from_iso_3166_1_numeric_code()` method which as been
  deprecated since Biip 2.2.
  (Fixes: #161, PR: #166)

## Upgrading from 1.x to 2.x

### Prefixes may be missing

- When a prefix looks valid but cannot be found in Biip's list of known GS1
  prefixes [`GS1Prefix.extract()`][biip.gs1_prefixes.GS1Prefix.extract] now
  returns `None` instead of raising an exception.
  (Fixes: #93, PR: #94)

- Following from the above, [`Gtin.prefix`][biip.gtin.Gtin.prefix] and
  [`Sscc.prefix`][biip.sscc.Sscc.prefix] can now be None. This makes it possible
  to parse and validate GTINs and SSCCs with prefixes missing from Biip's list
  of known GS1 prefixes. (Fixes: #93, PR: #94)

### Removed APIs

- The deprecated RCN region `RcnRegion.BALTICS` has been removed. Use
  [`ESTONIA`][biip.rcn.RcnRegion.ESTONIA],
  [`LATVIA`][biip.rcn.RcnRegion.LATVIA], or
  [`LITHUANIA`][biip.rcn.RcnRegion.LITHUANIA] instead. (PR: #100)
