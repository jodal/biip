# Restricted Circulation Number (RCN)

If you have products where the price depends on the weight of each item,
and either the price or the weight are encoded in the GTIN, you are
dealing with Restricted Circulation Numbers, or RCN, another subset of
GTIN:

```python hl_lines="4-14"
>>> print(biip.parse("2011122912346"))
ParseResult(
    value='2011122912346',
    gtin=Rcn(
        value='2011122912346',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(
            value='201',
            usage='Used to issue GS1 Restricted Circulation Numbers within a geographic region (MO defined)'
        ),
        company_prefix=None,
        payload='201112291234',
        check_digit=6
    ),
    upc_error="Failed to parse '2011122912346' as UPC: Expected 6, 7, 8, or 12 digits, got 13.",
    sscc_error="Failed to parse '2011122912346' as SSCC: Expected 18 digits, got 13.",
    gs1_message_error="Failed to match '122912346' with GS1 AI (12) pattern
'^12(\\d{2}(?:0\\d|1[0-2])(?:[0-2]\\d|3[01]))$'."
)
```

In the example above, the number is detected to be an RCN, and an instance of
[`Rcn`][biip.rcn.Rcn], a subclass of [`Gtin`][biip.gtin.Gtin], which may
contain a few additional fields, is returned.

The rules for how to encode weight or price into an RCN varies between
geographical regions. The national GS1 Member Organizations (MO) specify
the rules for their region. Biip already supports a few of these
rulesets, and you can easily add more if detailed documentation on the
market's rules is available.

Because of the market variations, you must specify your geographical
region for Biip to be able to extract price or weight from the RCN:

```python hl_lines="1-2 15-18"
>>> from biip.rcn import RcnRegion
>>> config = biip.ParseConfig(rcn_region=RcnRegion.GREAT_BRITAIN)
>>> print(biip.parse("2011122912346", config=config))
ParseResult(
    value='2011122912346',
    gtin=Rcn(
        value='2011122912346',
        format=GtinFormat.GTIN_13,
        prefix=GS1Prefix(
            value='201',
            usage='Used to issue GS1 Restricted Circulation Numbers within a geographic region (MO defined)'
        ),
        company_prefix=None,
        payload='201112291234',
        check_digit=6,
        usage=RcnUsage.GEOGRAPHICAL,
        region=RcnRegion.GREAT_BRITAIN,
        price=Decimal('12.34'),
        money=Money('12.34', 'GBP')
    ),
    upc_error="Failed to parse '2011122912346' as UPC: Expected 6, 7, 8, or 12 digits, got 13.",
    sscc_error="Failed to parse '2011122912346' as SSCC: Expected 18 digits, got 13.",
    gs1_message_error="Failed to match '122912346' with GS1 AI (12) pattern
'^12(\\d{2}(?:0\\d|1[0-2])(?:[0-2]\\d|3[01]))$'."
)
```

The [`price`][biip.rcn.Rcn.price] and [`money`][biip.rcn.Rcn.money] fields
contain the same data. The difference is that while `price` is a simple
[`Decimal`][decimal.Decimal] type, `money` also carries currency information.
The `money` field is only set if the optional dependency
[`py-moneyed`](https://pypi.org/project/py-moneyed/) is installed.

/// note | Learn more
To learn more about RCN, see the
[`biip.rcn`](../reference/rcn.md) reference documentation.
///
